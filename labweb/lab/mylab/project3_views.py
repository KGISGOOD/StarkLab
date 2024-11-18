from django.shortcuts import render
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
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date

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

def fetch_url(url, session):
    try:
        response = session.get(url)
        response.raise_for_status()  # 確保請求成功
        print(f"成功抓取: {url}")
        return response.text
    except requests.RequestException as e:
        print(f"錯誤抓取 {url}: {e}")
        return None

def process_html(html):
    # 此處根據需求解析 HTML（例如使用 BeautifulSoup）
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        # 假設你需要解析文章標題
        title = soup.title.string if soup.title else "無標題"
        print(f"標題: {title}")

# 時間解析函數
def parse_date(date_str):
    if '天前' in date_str:
        days_ago = int(re.search(r'\d+', date_str).group())
        date = datetime.now() - timedelta(days=days_ago)
    elif '小時前' in date_str:
        hours_ago = int(re.search(r'\d+', date_str).group())
        date = datetime.now() - timedelta(hours=hours_ago)
    elif '分鐘前' in date_str:
        minutes_ago = int(re.search(r'\d+', date_str).group())
        date = datetime.now() - timedelta(minutes=minutes_ago)
    elif '昨天' in date_str:
        date = datetime.now() - timedelta(days=1)
    else:
        try:
            date = datetime.strptime(f'{datetime.now().year}年{date_str}', '%Y年%m月%d日')
        except ValueError:
            date = '未知'

    return date.strftime('%Y-%m-%d') if isinstance(date, datetime) else date

# URL 處理函數
def extract_final_url(google_news_url):
    match = re.search(r'(https?://[^&]+)', google_news_url)
    if match:
        return match.group(1)
    return google_news_url

# 爬取新聞列表函數
def fetch_news(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
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

            time_element = article.find('div', class_='UOVeFe').find('time', class_='hvbAAd') if article.find('div', 'UOVeFe') else None
            date_str = time_element.get_text(strip=True) if time_element else '未知'

            date = parse_date(date_str)

            # 抓取文章內的圖片
            image_urls = []
            article_response = requests.get(full_link, headers=headers)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # 各新聞網站的圖片提取邏輯
            if "udn.com" in full_link:
                container_div = article_soup.find('section', class_='article-body__editor')
                if container_div:
                    img_tag = container_div.find('img', src=lambda x: x and 'pgw.udn.com.tw' in x)
                    if img_tag:
                        image_urls.append(img_tag['src'])

            elif "newtalk.tw" in full_link:
                image_divs = article_soup.find_all('div', class_='news_img')
                for div in image_divs:
                    img_tag = div.find('img', itemprop="image")
                    if img_tag:
                        image_urls.append(img_tag['src'])

            elif "tw.news.yahoo.com" in full_link:
                img_div = article_soup.find("div", class_="caas-body")
                if img_div:
                    figure_tag = img_div.find("figure", class_="caas-figure")
                    if figure_tag:
                        img_tag = figure_tag.find("img", class_="caas-img")
                        if img_tag:
                            image_urls.append(img_tag.get("data-src"))

            elif "ltn.com.tw" in full_link:
                image_divs = article_soup.find_all('div', class_='image-popup-vertical-fit')
                for div in image_divs:
                    img_tag = div.find('img')
                    if img_tag:
                        image_urls.append(img_tag['src'])

            # 通用圖片提取邏輯
            if not image_urls:
                for img_tag in article_soup.find_all('img', src=True):
                    img_src = img_tag['src']
                    if img_src:
                        image_urls.append(img_src)

            news_list.append({
                '標題': title,
                '連結': full_link,
                '來源': source_name,
                '時間': date,
                '圖片': image_urls if image_urls else '找不到圖片。'
            })

        return news_list

    except Exception as e:
        print(f"抓取新聞時發生錯誤: {e}")
        return []

# 抓取文章內容函數
def fetch_article_content(driver, source_name, url):
    content = ''
    
    try:
        driver.get(url)

        # 等待段落元素出現
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'p'))
        )

        # 根據不同新聞來源處理內容
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

    except Exception as e:
        content = '錯誤'

    return content

# 從資料庫擷取新聞資料函數
def fetch_news_data():
    db_name = 'w.db'
    table_name = 'news'

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f'SELECT id, title, link, content, source, date, image FROM {table_name}')
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
            'date': row[5],
            'image': row[6] 
        })
    
    return news_list

# Django 視圖函數
def update_news(request):
    main()
    return JsonResponse({'message': '新聞更新成功！'})

# 主要執行函數
def main():
    start_time = time.time()
    
    # 定義要爬取的關鍵字 URL
    urls = [
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'
    ]

    # 爬取所有新聞
    all_news_items = []
    for url in urls:
        news_items = fetch_news(url)
        all_news_items.extend(news_items)

    if all_news_items:
        # 建立 DataFrame 並去除重複
        news_df = pd.DataFrame(all_news_items)
        news_df = news_df.drop_duplicates(subset='標題', keep='first')

        driver = setup_chrome_driver()

        # 處理輸出檔案
        output_file = 'w.csv'
        if os.path.exists(output_file):
            os.remove(output_file)

        # 定義關鍵字
        skip_keywords = ['台灣', '台北', '新北', '基隆', '新竹市', '桃園', '新竹縣', '宜蘭', 
                        '台中', '苗栗', '彰化', '南投', '雲林', '高雄', '台南', '嘉義', 
                        '屏東', '澎湖', '花東', '花蓮', '台9線', '金門', '馬祖', '綠島', '蘭嶼',
                        '臺灣', '台北', '臺中', '臺南', '臺9縣', '全台', '全臺','票','戰爭','GDP']
        
        desired_keywords = ['大雨', '豪雨', '暴雨', '淹水', '洪水', '水災', '颱風', '颶風', '風災', 
                         '海嘯', '地震', '乾旱', '旱災']

        # 處理每篇新聞
        for index, item in news_df.iterrows():
            source_name = item['來源']
            original_url = item['連結']
            final_url = extract_final_url(original_url)

            content = fetch_article_content(driver, source_name, final_url)

            if content != '未找到內容' and content != '錯誤':
                result = {
                    '標題': item['標題'],
                    '連結': original_url,
                    '內文': content,
                    '來源': source_name,
                    '時間': item['時間'],
                    '圖片': item['圖片']
                }

                # 檢查關鍵字
                if any(keyword in result['標題'] or keyword in result['內文'] for keyword in skip_keywords):
                    print(f"跳過包含指定關鍵字的文章: {result['標題']}")
                    continue

                if not any(keyword in result['標題'] or keyword in result['內文'] for keyword in desired_keywords):
                    print(f"文章不包含所需的關鍵字: {result['標題']}")
                    continue

                # 保存到 CSV
                output_df = pd.DataFrame([result])
                output_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), 
                               index=False, encoding='utf-8')

                # 輸出爬取結果
                print(f"標題: {result['標題']}")
                print(f"連結: {result['連結']}")
                print(f"內文: {result['內文'][:50]}...")
                print(f"來源: {result['來源']}")
                print(f"時間: {result['時間']}")
                print(f"圖片: {result['圖片']}")
                print('-' * 80)

        driver.quit()

    # 資料庫處理
    db_name = 'w.db'
    table_name = 'news'

    # 建立資料庫連線
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 建立資料表
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        link TEXT,
        image TEXT,
        content TEXT,
        source TEXT,
        date TEXT
    )
    ''')

    # 清空表格內容
    cursor.execute(f'DELETE FROM {table_name}')
    conn.commit()

    # 讀取並排序 CSV 檔案
    w_df = pd.read_csv('w.csv')
    w_df['時間'] = pd.to_datetime(w_df['時間'], format='%Y-%m-%d', errors='coerce')
    w_df = w_df.sort_values(by='時間', ascending=False)

    # 將資料寫入資料庫
    for _, row in w_df.iterrows():
        cursor.execute(f'''
        SELECT COUNT(*) FROM {table_name} WHERE title = ? AND link = ?
        ''', (row['標題'], row['連結']))
        exists = cursor.fetchone()[0]

        if exists == 0:
            cursor.execute(f'''
            INSERT INTO {table_name} (title, link, content, source, date, image)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['標題'], row['連結'], row['內文'], row['來源'], 
              row['時間'].strftime('%Y-%m-%d'), row['圖片']))

    # 關閉資料庫連線
    conn.commit()
    conn.close()

    # 計算執行時間
    end_time = time.time()
    elapsed_time = int(end_time - start_time)
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    time_str = ''
    if hours > 0:
        time_str += f'{hours} 小時 '
    if minutes > 0 or hours > 0:
        time_str += f'{minutes} 分 '
    time_str += f'{seconds} 秒'
    
    # 輸出執行結果
    print(f'爬取新聞並儲存資料共耗時 {time_str}')
    print('新聞更新已完成！')
    print('爬取後的內容已成功儲存到 CSV 和 SQLite 資料庫中')

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
            'date': row[5],
            'image': row[6] 
        })

    # 將新聞列表傳遞給模板
    return render(request, 'news.html', {'news_list': news_list})


# RESTful API 查詢所有新聞資料並以JSON格式返回
def news_list(request):
    if request.method == 'GET':
        # 查詢所有新聞記錄，並返回標題、連結、內容、來源和日期
        news = News.objects.all().values('title', 'link', 'content', 'source', 'date','image')
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
            date=data['date'],
            image=data.get('image', 'null')
        )
        return JsonResponse({"message": "News created", "news_id": news.id}, status=201)
    
from django.views.decorators.http import require_GET

@require_GET
def news_api(request):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect('w.db')
        cursor = conn.cursor()

        # 執行查詢，確保包含 'image' 欄位
        cursor.execute("SELECT id, title, link, content, source, date, image FROM news")
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
                'date': row[5],
                'image': row[6]  # 確保 image 欄位存在於查詢中
            })

        return JsonResponse(news_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    