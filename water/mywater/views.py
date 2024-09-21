from django.shortcuts import render, redirect
import pandas as pd
import os
import sqlite3
import requests
from bs4 import BeautifulSoup
import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 爬取新聞的函數
def fetch_news(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all('article', class_='IFHyqb')

        news_list = []
        for article in articles:
            title_element = article.find('a', class_='JtKRv')
            title = title_element.get_text(strip=True) if title_element else '未知'
            link = title_element.get('href', '').strip() if title_element else ''
            full_link = requests.compat.urljoin(url, link)

            news_source = article.find('div', class_='vr1PYe')
            source_name = news_source.get_text(strip=True) if news_source else '未知'

            time_element = article.find('div', class_='UOVeFe').find('time', class_='hvbAAd') if article.find('div', class_='UOVeFe') else None
            date = time_element.get_text(strip=True) if time_element else '未知'

            news_list.append({
                '標題': title,
                '連結': full_link,
                '來源': source_name,
                '時間': date
            })

        return news_list

    except Exception as e:
        print(f"抓取新聞時發生錯誤: {e}")
        return []

# 保存到 CSV 文件的函數
def save_to_csv(news_items, filename):
    headers = ['標題', '連結', '來源', '時間']
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for item in news_items:
            writer.writerow(item)

# 設置 Chrome 的選項
def setup_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_final_url(google_news_url):
    match = re.search(r'(https?://[^&]+)', google_news_url)
    if match:
        return match.group(1)
    return google_news_url

def fetch_article_content(driver, source_name, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'p')))

        content = ''
        if source_name == '經濟日報':
            paragraphs = driver.find_elements(By.CSS_SELECTOR, 'section.article-body__editor p')
            content = '\n'.join([p.text for p in paragraphs])
        elif source_name == 'Yahoo奇摩新聞':
            paragraphs = driver.find_elements(By.CSS_SELECTOR, 'div.caas-body p')
            content = '\n'.join([p.text for p in paragraphs])
        elif source_name == 'Newtalk新聞':
            paragraphs = driver.find_elements(By.CSS_SELECTOR, 'div.articleBody.clearfix p')
            content = '\n'.join([p.text for p in paragraphs])
        elif source_name == '自由時報':
            paragraphs = driver.find_elements(By.CSS_SELECTOR, 'p')
            content = '\n'.join([p.text.strip() for p in paragraphs])

        if not content.strip():
            content = '未找到內容'

        return content

    except Exception as e:
        print(f"抓取內容時發生錯誤: {e}")
        return '錯誤'

def main():
    urls = [
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%A8%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際大雨 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際豪雨 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際暴雨 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際淹水 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際洪水 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際水災 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際颱風 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際颶風 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際風災 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際海嘯 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際地震 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',  # 國際乾旱 when:30d
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A30d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'  # 國際旱災 when:30d
    ]

    all_news_items = []
    for url in urls:
        news_items = fetch_news(url)
        all_news_items.extend(news_items)

    filename = '123all_news.csv'
    save_to_csv(all_news_items, filename)
    print(f"所有新聞已保存到 {filename}")

    df = pd.read_csv(filename)
    valid_sources = {'經濟日報', 'Yahoo奇摩新聞', 'Newtalk新聞', '自由時報'}
    filtered_df = df[df['來源'].isin(valid_sources)]

    driver = setup_chrome_driver()

    output_file = 'w.csv'
    if os.path.exists(output_file):
        os.remove(output_file)

    for _, row in filtered_df.iterrows():
        source_name = row['來源']
        original_url = row['連結']
        final_url = extract_final_url(original_url)

        content = fetch_article_content(driver, source_name, final_url)

        if content != '未找到內容' and content != '錯誤':
            result = {
                '標題': row['標題'],
                '連結': original_url,
                '內文': content,
                '來源': source_name,
                '時間': row['時間']
            }

            output_df = pd.DataFrame([result])
            output_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False, encoding='utf-8')

            print(f"標題: {result['標題']}")
            print(f"連結: {result['連結']}")
            print(f"內文: {result['內文'][:1000]}...")
            print(f"來源: {result['來源']}")
            print(f"時間: {result['時間']}")
            print('-' * 80)

    print('爬取後的內容已輸出到控制台')

    driver.quit()

    db_name = 'db.sqlite3'
    table_name = 'news'

    df = pd.read_csv('w.csv')
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        title TEXT,
        link TEXT,
        content TEXT,
        source TEXT,
        date TEXT
    )
    ''')

    cursor.execute(f'DELETE FROM {table_name}')

    for _, row in df.iterrows():
        cursor.execute(f'''
        INSERT INTO {table_name} (title, link, content, source, date)
        VALUES (?, ?, ?, ?, ?)
        ''', (row['標題'], row['連結'], row['內文'], row['來源'], row['時間']))

    conn.commit()
    conn.close()

    print('CSV 資料已成功存儲到 SQLite 資料庫中')

def fetch_news_data():
    db_name = 'w.db'
    table_name = 'news'

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f'SELECT title, link, content, source, date FROM {table_name}')
    news_data = cursor.fetchall()

    conn.close()

    news_list = []
    for row in news_data:
        news_list.append({
            'title': row[0],
            'link': row[1],
            'content': row[2],
            'source': row[3],
            'date': row[4]
        })
    
    return news_list

def news_view(request):
    news_list = fetch_news_data()
    return render(request, 'news.html', {'news_list': news_list})

def update_news(request):
    main()  # 確保在這裡引用主函數
    return redirect('news_list')  # 確保在這裡引用正確的路由名稱
