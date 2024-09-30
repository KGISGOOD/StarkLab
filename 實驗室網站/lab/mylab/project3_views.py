from django.shortcuts import render, redirect
import pandas as pd
import os
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

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

def fetch_article_content(driver, source_name, url, retries=3):
    for attempt in range(retries):
        try:
            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p'))
            )

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
            print(f"第 {attempt + 1} 次嘗試抓取內容失敗: {e}")

            if attempt < retries - 1:
                print(f"嘗試重新爬取...（剩餘嘗試次數：{retries - attempt - 1}）")
                time.sleep(2)
            else:
                print("多次嘗試後仍然失敗，停止嘗試。")
                return '錯誤'

    return '錯誤'


def main():
    start_time = time.time()
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

    driver = setup_chrome_driver()

    db_name = 'w.db'
    table_name = 'news'

    # 設置資料庫
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        link TEXT,
        content TEXT,
        source TEXT,
        date TEXT
    )
    ''')
    
    output_file = 'w.csv'
    if os.path.exists(output_file):
        os.remove(output_file)

    # 爬取新聞並同時儲存到 CSV 和資料庫
    for item in all_news_items:
        source_name = item['來源']
        original_url = item['連結']
        final_url = extract_final_url(original_url)

        content = fetch_article_content(driver, source_name, final_url, retries=3)

        if content != '未找到內容' and content != '錯誤':
            result = {
                '標題': item['標題'],
                '連結': original_url,
                '內文': content,
                '來源': source_name,
                '時間': item['時間']
            }

            # 保存到 CSV
            output_df = pd.DataFrame([result])
            output_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False, encoding='utf-8')

            # 保存到資料庫
            cursor.execute(f'''
            INSERT INTO {table_name} (title, link, content, source, date)
            VALUES (?, ?, ?, ?, ?)
            ''', (result['標題'], result['連結'], result['內文'], result['來源'], result['時間']))

            print(f"標題: {result['標題']}")
            print(f"連結: {result['連結']}")
            print(f"內文: {result['內文'][:1000]}...")
            print(f"來源: {result['來源']}")
            print(f"時間: {result['時間']}")
            print('-' * 80)

    conn.commit()
    conn.close()
    driver.quit()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'爬取新聞並儲存資料共耗時 {elapsed_time:.2f} 秒')
    print('新聞更新已完成！')
    print('爬取後的內容已成功儲存到 CSV 和 SQLite 資料庫中')

def fetch_news_data():
    db_name = 'w.db'
    table_name = 'news'

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f'SELECT id, title, link, content, source, date FROM {table_name}')
    news_data = cursor.fetchall()

    conn.close()

    news_list = []
    for row in news_data:
        news_list.append({
            'id': row[0],
            'title': row[1],
            'link': row[2],
            'content': row[3],
            'source': row[4],
            'date': row[5]
        })
    
    return news_list

from django.http import JsonResponse

def update_news(request):
    main()  # 執行爬取新聞的函數
    return JsonResponse({'message': '新聞更新成功！'})


# views.py
from django.http import JsonResponse
from django.shortcuts import render
from .models import News
import json
from django.views.decorators.csrf import csrf_exempt

# 處理新聞列表及搜尋功能
def news_view(request):
    # 取得搜尋關鍵字
    query = request.GET.get('search', '')

    # 連接到 SQLite 資料庫
    conn = sqlite3.connect('w.db')
    cursor = conn.cursor()

    # 查詢新聞資料，如果有搜尋關鍵字，則過濾標題中包含該關鍵字的新聞
    if query:
        cursor.execute("SELECT * FROM news WHERE title LIKE ?", ('%' + query + '%',))
    else:
        cursor.execute("SELECT * FROM news")

    # 獲取所有結果
    news_data = cursor.fetchall()

    # 關閉資料庫連接
    conn.close()

    # 將結果轉換為字典列表
    news_list = []
    for row in news_data:
        news_list.append({
            'id': row[0],
            'title': row[1],
            'link': row[2],
            'content': row[3],
            'source': row[4],
            'date': row[5]
        })

    # 將新聞列表傳遞給模板
    return render(request, 'news.html', {'news_list': news_list})


# RESTful API 查詢所有新聞資料並以JSON格式返回
def news_list(request):
    if request.method == 'GET':
        # 查詢所有新聞記錄，並返回標題、連結、內容、來源和日期
        news = News.objects.all().values('title', 'link', 'content', 'source', 'date')
        return JsonResponse(list(news), safe=False)

# RESTful API 新增新聞資料
@csrf_exempt
def news_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        news = News.objects.create(
            title=data['title'],
            link=data['link'],
            content=data['content'],
            source=data['source'],
            date=data['date']
        )
        return JsonResponse({"message": "News created", "news_id": news.id}, status=201)
    
from django.views.decorators.http import require_GET

@require_GET
def news_api(request):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect('w.db')
        cursor = conn.cursor()

        # 執行查詢
        cursor.execute("SELECT id, title, link, content, source, date FROM news")
        news_data = cursor.fetchall()

        # 關閉資料庫連接
        conn.close()

        # 將結果轉換為字典列表
        news_list = []
        for row in news_data:
            news_list.append({
                'id': row[0],
                'title': row[1],
                'link': row[2],
                'content': row[3][:50] + '...' if len(row[3]) > 50 else row[3],  # 限制內容為50字
                'source': row[4],
                'date': row[5]
            })

        return JsonResponse(news_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    