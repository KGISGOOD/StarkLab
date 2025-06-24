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
import json
import threading
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from .models import News
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import re
from datetime import datetime, timedelta
from collections import defaultdict
import random
import psutil


# 修改 ALLOWED_SOURCES 為只包含四家報社
ALLOWED_SOURCES = {
    'Newtalk新聞',
    '經濟日報',
    '自由時報',
    'BBC News 中文'
}

# 定義允許的自然災害關鍵字
DISASTER_KEYWORDS = {
    '大雨', '豪雨', '暴雨', '淹水', '洪水', '水災',
    '颱風', '颶風', '風災',
    '地震', '海嘯',
    '乾旱', '旱災', '大火', '野火'
}

# 關鍵字設定 - 用於判斷國內新聞
domestic_keywords = [
    '台灣', '台北', '新北', '基隆', '新竹市', '桃園', '新竹縣', '宜蘭',
    '台中', '苗栗', '彰化', '南投', '雲林', '高雄', '台南', '嘉義',
    '屏東', '澎湖', '花東', '花蓮', '台9線', '金門', '馬祖', '綠島', '蘭嶼',
    '臺灣', '台北', '臺中', '臺南', '臺9縣', '全台', '全臺'
]

# 設定 AI API 最大重試次數和初始延遲時間
max_retries = 3  # 最大重試次數
retry_delay = 2  # 初始延遲2秒

# 從 Google News 抓取資料（原始版本，使用 requests 和 BeautifulSoup）
def fetch_news(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all(['article', 'div'], class_=['IFHyqb', 'xrnccd', 'IBr9hb', 'NiLAwe'])
        news_list = []
        allowed_sources_set = set(ALLOWED_SOURCES)

        for article in articles:
            try:
                title_element = article.find(['a', 'h3', 'h4'], class_=['JtKRv', 'ipQwMb', 'DY5T1d', 'gPFEn']) or article.find('a', recursive=True)
                if not title_element:
                    continue

                title = title_element.get_text(strip=True)
                link = title_element.get('href', '')
                link = f'https://news.google.com/{link[2:]}' if link.startswith('./') else f'https://news.google.com{link}' if link.startswith('/') else link

                source_element = article.find(['div', 'a'], class_=['vr1PYe', 'wEwyrc', 'SVJrMe', 'NmQAAc']) or article.find(lambda tag: tag.name in ['div', 'a'] and 'BBC' in tag.get_text())
                if not source_element:
                    continue

                source_name = source_element.get_text(strip=True)
                source_name = 'BBC News 中文' if 'BBC' in source_name else source_name

                if source_name not in allowed_sources_set:
                    continue

                time_element = article.find(['time', 'div'], class_=['UOVeFe', 'hvbAAd', 'WW6dff', 'LfVVr'])
                date_str = time_element.get_text(strip=True) if time_element else '未知'
                date = parse_date(date_str)

                news_item = {
                    '標題': title,
                    '連結': link,
                    '來源': source_name,
                    '時間': date
                }
                news_list.append(news_item)

            except Exception as e:
                print(f"處理文章時發生錯誤: {str(e)}")
                continue

        return news_list

    except Exception as e:
        print(f"抓取新聞時發生錯誤: {str(e)}")
        return []

# 從 Google News 抓取資料（僅用於第一個 URL，包含打開、延遲和刷新）
def fetch_news_with_refresh(url, driver):
    try:
        # 先打開網頁
        driver.get(url)
        print(f"已打開網頁: {url}")

        # 隨機延遲 2 到 3 秒
        delay_seconds = random.uniform(2, 3)
        print(f"⏳ 等待 {delay_seconds:.2f} 秒後刷新網頁...")
        time.sleep(delay_seconds)

        # 刷新網頁
        driver.refresh()
        print(f"已刷新網頁: {url}")

        # 等待新聞元素加載
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
        )

        allowed_sources_set = set(ALLOWED_SOURCES)
        news_list = []

        # 抓取新聞項目
        articles = driver.find_elements(By.CSS_SELECTOR, "article")
        for article in articles:
            try:
                title_element = article.find_element(By.CSS_SELECTOR, "h3, h4, a.JtKRv, a.ipQwMb, a.DY5T1d, a.gPFEn")
                if not title_element:
                    continue
                title = title_element.text.strip()
                link = title_element.get_attribute("href")
                if not link:
                    continue
                link = f'https://news.google.com/{link[2:]}' if link.startswith('./') else f'https://news.google.com{link}' if link.startswith('/') else link

                source_element = article.find_element(By.CSS_SELECTOR, "div.vr1PYe, a.wEwyrc, div.SVJrMe, div.NmQAAc")
                if not source_element:
                    continue
                source_name = source_element.text.strip()
                source_name = 'BBC News 中文' if 'BBC' in source_name else source_name

                if source_name not in allowed_sources_set:
                    continue

                time_element = article.find_element(By.CSS_SELECTOR, "time, div.UOVeFe, div.hvbAAd, div.WW6dff, div.LfVVr")
                date_str = time_element.text.strip() if time_element else '未知'
                date = parse_date(date_str)

                news_item = {
                    '標題': title,
                    '連結': link,
                    '來源': source_name,
                    '時間': date
                }
                news_list.append(news_item)

            except Exception as e:
                print(f"處理文章時發生錯誤: {str(e)}")
                continue

        return news_list

    except Exception as e:
        print(f"抓取新聞時發生錯誤: {str(e)}")
        return []

# 解析 Google News 上的日期字符串
def parse_date(date_str):
    current_date = datetime.now()
    
    if '天前' in date_str:
        days_ago = int(re.search(r'\d+', date_str).group())
        date = current_date - timedelta(days=days_ago)
    elif '小時前' in date_str:
        hours_ago = int(re.search(r'\d+', date_str).group())
        date = current_date - timedelta(hours=hours_ago)
    elif '分鐘前' in date_str:
        minutes_ago = int(re.search(r'\d+', date_str).group())
        date = current_date - timedelta(minutes=minutes_ago)
    elif '昨天' in date_str:
        date = current_date - timedelta(days=1)
    else:
        try:
            if '年' not in date_str:
                date_str = f'{current_date.year}年{date_str}'
            date = datetime.strptime(date_str, '%Y年%m月%d日')
        except ValueError:
            date = current_date

    return date.strftime('%Y-%m-%d')

# 設置 Chrome 驅動
def setup_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# 獲取最終網址（處理 Google News 跳轉）
def get_final_url(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))
        )
        final_url = driver.current_url
        return final_url
    except Exception as e:
        print(f"獲取最終網址失敗: {e}")
        return url

# 爬取文章內容
def fetch_article_content(driver, sources_urls):
    results = {}
    summaries = {}
    final_urls = {}

    content_selectors = {
        'Newtalk新聞': 'div.articleBody.clearfix p',
        '經濟日報': 'section.article-body__editor p',
        '自由時報': 'div.text p',
        'BBC News 中文': 'div.bbc-1cvxiy9 p'
    }

    for source_name, url in sources_urls.items():
        if source_name not in ALLOWED_SOURCES:
            continue

        try:
            final_url = get_final_url(driver, url)
            final_urls[source_name] = final_url

            driver.get(final_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p'))
            )

            selector = content_selectors.get(source_name)
            if not selector:
                continue

            paragraphs = driver.find_elements(By.CSS_SELECTOR, selector)
            content = '\n'.join(p.text.strip() for p in paragraphs if p.text.strip())
            summary = content[:100] if content else '未找到內容'

            results[source_name] = content if content else '未找到內容'
            summaries[source_name] = summary

        except Exception as e:
            print(f"抓取內容失敗: {e}")
            results[source_name] = '錯誤'
            summaries[source_name] = '錯誤'
            final_urls[source_name] = url

    return results, summaries, final_urls

# 爬取圖片 URL
def extract_image_url(driver, sources_urls):
    results = {}
    
    image_selectors = {
        'Newtalk新聞': "div.news_img img",
        '經濟日報': "section.article-body__editor img",
        '自由時報': "div.image-popup-vertical-fit img",
        'BBC News 中文': "div.bbc-1cvxiy9 img"
    }

    for source_name, url in sources_urls.items():
        if source_name not in ALLOWED_SOURCES:
            continue
            
        try:
            driver.get(url)
            selector = image_selectors.get(source_name)
            if not selector:
                continue
            
            if source_name == 'BBC News 中文':
                try:
                    content_div = driver.find_element(By.CSS_SELECTOR, 'div.bbc-1cvxiy9')
                    if content_div:
                        first_image = content_div.find_element(By.TAG_NAME, 'img')
                        if first_image and 'src' in first_image.get_attribute('outerHTML'):
                            results[source_name] = first_image.get_attribute('src')
                            continue
                except Exception as e:
                    print(f"無法找到 BBC 新聞圖片: {e}")

            image_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            image_url = image_element.get_attribute('src') or image_element.get_attribute('data-src')
            results[source_name] = image_url or ''
            
        except Exception as e:
            print(f"圖片擷取錯誤: {e}")
            results[source_name] = ''
            
    return results

# 初始化追蹤最高記憶體使用量
max_mem_mb = 0

# 顯示並回傳記憶體使用量（MB）
def log_memory_usage(note=''):
    global max_mem_mb
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    print(f"[Memory] {note} 使用記憶體：{mem_mb:.2f} MB")
    max_mem_mb = max(max_mem_mb, mem_mb)
    return mem_mb

# 爬蟲主函數
@require_GET
def crawler_first_stage(request):
    try:
        global max_mem_mb
        start_time = time.time()
        day = "7"
        log_memory_usage("開始爬蟲")
        
        # Google News 搜尋 URL
        urls = [
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際大雨
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際豪雨
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際暴雨
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際淹水
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際洪水
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際水災    
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際颱風
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際颶風    
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際風災
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際海嘯
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際地震
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際乾旱
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際旱災
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際大火＝野火
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際野火
            # 加上bbc關鍵字
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際海嘯
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際地震
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際大火＝野火
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'#國際野火      
        ]
        
        log_memory_usage("初始化 Chrome 驅動前")
        driver = setup_chrome_driver()
        log_memory_usage("初始化 Chrome 驅動後")

        all_news_items = []
        start_crawl_time = time.time()

        if urls:
            first_url = urls[0]
            news_items = fetch_news_with_refresh(first_url, driver)
            all_news_items.extend(news_items)
            log_memory_usage("第一個 URL 爬完後")

        for url in urls[1:]:
            news_items = fetch_news(url)
            all_news_items.extend(news_items)
            log_memory_usage(f"爬完 URL: {url}")

        if all_news_items:
            log_memory_usage("準備建立 DataFrame")
            news_df = pd.DataFrame(all_news_items)
            news_df = news_df.drop_duplicates(subset='標題', keep='first')
            log_memory_usage("建立並去重 DataFrame 後")

            end_crawl_time = time.time()
            crawl_time = int(end_crawl_time - start_crawl_time)
            hours, remainder = divmod(crawl_time, 3600)
            minutes, seconds = divmod(remainder, 60)

            time_str = ''
            if hours > 0:
                time_str += f'{hours}小時'
            if minutes > 0 or hours > 0:
                time_str += f'{minutes}分'
            time_str += f'{seconds}秒'

            print(f'Google News 爬取完成，耗時：{time_str}')

            first_stage_file = 'w2.csv'
            if os.path.exists(first_stage_file):
                os.remove(first_stage_file)

            for index, item in news_df.iterrows():
                source_name = item['來源']
                original_url = item['連結']
                sources_urls = {source_name: original_url}

                content_results, _, final_urls = fetch_article_content(driver, sources_urls)
                image_results = extract_image_url(driver, sources_urls)

                content = content_results.get(source_name, '')
                final_url = final_urls.get(source_name, original_url)
                image_url = image_results.get(source_name, '')

                result = {
                    '標題': item['標題'],
                    '連結': final_url,
                    '內文': content or '',
                    '來源': source_name,
                    '時間': item['時間'],
                    '圖片': image_url or ''
                }

                output_df = pd.DataFrame([result])
                log_memory_usage(f"儲存新聞：{item['標題']} 前")
                output_df.to_csv(first_stage_file, mode='a', header=not os.path.exists(first_stage_file),
                                 index=False, encoding='utf-8')
                log_memory_usage(f"儲存新聞：{item['標題']} 後")

                print(f"已儲存新聞: {result['標題']}")

            driver.quit()
            final_mem_mb = log_memory_usage("爬蟲結束前")

            return JsonResponse({
                'status': 'success',
                'message': f'第一階段爬蟲完成！耗時：{time_str}',
                'csv_file': first_stage_file,
                'total_news': len(news_df),
                'final_memory_mb': f'{final_mem_mb:.2f} MB',
                'peak_memory_mb': f'{max_mem_mb:.2f} MB'
            })

        driver.quit()
        return JsonResponse({
            'status': 'error',
            'message': '沒有找到新聞'
        })

    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return JsonResponse({
            'status': 'error',
            'message': f'爬蟲執行失敗：{str(e)}'
        }, status=500)

#ai 處理
#導入api key
from mylab.config import xai_api_key, model_name


def news_ai(request):

    def chat_with_xai(prompt, api_key, model_name, context=""):
        
        for attempt in range(max_retries):
            try:
                url = 'https://api.x.ai/v1/chat/completions'
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }
    
                messages = [
                    {"role": "system", "content": "你是一個新聞分析助手"},
                    {"role": "user", "content": prompt}
                ]
    
                data = {
                    "messages": messages,
                    "model": model_name,
                    "temperature": 0,
                    "stream": False
                }
    
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result and 'choices' in result and result['choices']:
                        content = result['choices'][0]['message']['content']
                        return content
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # 指數退避
                        print(f"API 速率限制，等待 {wait_time} 秒後重試...")
                        time.sleep(wait_time)
                        continue
                
                print(f"API 調用失敗 (狀態碼: {response.status_code})")
                return "無法取得回應"  # 改為有意義的預設值
    
            except Exception as e:
                print(f"API 錯誤: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                    continue
                return "發生錯誤"  # 改為有意義的預設值
    
    #防呆機制，刪除內文是錯誤的新聞
    # 讀取 CSV
    df = pd.read_csv('w2.csv')
    
    # 篩選出 '內文' 欄位不是 "錯誤" 的資料
    cleaned_df = df[df['內文'] != '錯誤'].copy()

    # 存回 CSV（不包含索引）
    cleaned_df.to_csv('w2.csv', index=False)
    print(f"已成功清除含有錯誤內文的新聞，共刪除 {len(df) - len(cleaned_df)} 筆資料。")

            
    #1.水利署_確認是否災害
    # 加入重試機制參數
    def is_disaster_news(title, content):
        """
        使用 X.AI 判斷新聞是否主要報導自然災害事件
        """
        # 確保 `content` 是字串，避免 TypeError
        content = str(content)  
        
        prompt = f"""
        請判斷以下新聞是否主要在報導自然災害事件本身，只需回答 true 或 false：
        
        允許的災害類型：大雨、豪雨、暴雨、淹水、洪水、水災、颱風、颶風、風災、地震、海嘯、乾旱、旱災、野火

        新聞標題：{title}
        新聞內容：{content[:500]}

        判斷標準：
        1. 新聞必須主要描述災害事件本身，包括：
        - 災害的發生過程
        - 災害造成的直接影響和損失
        - 災害現場的情況描述

        2. 以下類型的新聞都回答false：
        - 災後援助或捐贈活動的報導
        - 國際救援行動的新聞
        - 災後重建相關報導
        - 防災政策討論
        - 氣候變遷議題
        - 歷史災害回顧
        - 以災害為背景但主要報導其他事件的新聞
        - 焦點在於名人、奢華生活或政治人物的災後反應新聞
        - 以災害為背景，主要報導財產損失或奢華物品（如豪宅、奧運獎牌等）的新聞
        - 關於災後名人影響、財產損失的報導，例如關於明星或名人家園被燒毀的報導
        - 主要報導災後政府或政治人物的反應、決策或行動的新聞
        - 主要報導災害後的公共健康建議、當局指示或預防措施（如防範措施、配戴口罩、N95等）新聞
        - 內文無人員傷亡或是財務損失
        - 農作物產量劇減、減少、損失，搶救動物
        
        3. 特別注意：
        - 如果新聞主要在報導救援、捐助、外交等活動，即使提到災害也應該回答 false
        - 如果新聞只是用災害作為背景，主要報導其他事件，應該回答 false
        - 新聞的核心主題必須是災害事件本身才回答 true
        - 日本山林火災延燒5天 燒毀面積約63座東京巨蛋 true
        - 「借我躲一下！」 為避加州野火 238公斤黑熊「巴里」躲到民宅地板下 false

        """

        for attempt in range(max_retries):
            try:
                response = chat_with_xai(prompt, xai_api_key, model_name, "")
                return 'true' in response.lower()
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # 指數退避
                    print(f"API 錯誤: {str(e)}. 等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    print(f"API 錯誤: {str(e)}. 已達到最大重試次數。")
                    return False  # 或者可以返回其他合適的值來表示失敗

    # 1. 讀取 CSV 檔案
    df = pd.read_csv('w2.csv')

    # 2. 逐行判斷是否為災害新聞，並新增欄位
    df['is_disaster'] = df.apply(lambda row: is_disaster_news(row['標題'], str(row['內文'])), axis=1)

    # 3. 過濾只保留 is_disaster 為 True 的行
    df_true = df[df['is_disaster'] == True]

    # 4. 將結果存儲到新的 CSV 檔案
    print(df_true)
    df_true.to_csv('true_new.csv', index=False, encoding='utf-8-sig')



    #2.水利署＿從新聞內文中提取三個資訊欄位：國家、地點 和 災害
    def extract_information(news_content):
        """
        使用 AI 提取國家、地點和災害三個欄位，根據新聞內文生成。
        """
        prompt = f"""
        請根據以下內文欄位提取所有相關的國家、地點和災害：
        允許的災害類型：大雨、豪雨、暴雨、淹水、洪水、水災、颱風、颶風、風災、地震、海嘯、乾旱、旱災、野火
        
        檢核標準：
        - 國家是否完整，只能有一個國家
        - 地點是否完整(不遺漏任何提到的地點，可以包含多個地點)
        - 災害是否完整，只能有一個，並且必須只能是允許的災害類型。如果無法確定具體類型，請將災害歸類為最相似的允許災害
        - 格式是否一致(每個字串一個項目)
        - 描述是否準確(地理位置準確性)
        
        特別注意：
        - 如果出現像是 火山噴發 等不是允許的災害類型的災害，則依照內文敘述將其歸類到最相似的允許災害，例如野火
        - 如果出現像是 洪水,水災,颱風 多個允許災害出現，則依照內文敘述將其歸類到最相似的允許災害，例如颱風
        - 如果出現像是 法國,馬達加斯加,莫三比克 三個國家，則依照內文敘述將其歸類到一個國家，例如法國
        
        請直接輸出以下格式(用換行區分):
        國家: ["國家1"]
        地點: ["地點1", "地點2"]
        災害: ["災害1"]
        
        新聞內容:
        {news_content}
        """
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # 假設 chat_with_xai 是整合 AI 的函數
                response = chat_with_xai(prompt, xai_api_key, model_name, "")
                
                # 打印 AI 回傳的內容以進行檢查
                print("AI 回傳內容:", response)

                # 分析結果提取
                response_lines = response.strip().split("\n")
                result = {"國家": "", "地點": "", "災害": ""}

                for line in response_lines:
                    key, _, value = line.partition(":")  # 分割出鍵和值
                    if key.strip() == "國家":
                        result["國家"] = value.strip().strip('[]"').replace('\", \"', ',')
                    elif key.strip() == "地點":
                        result["地點"] = value.strip().strip('[]"').replace('\", \"', ',')
                    elif key.strip() == "災害":
                        result["災害"] = value.strip().strip('[]"').replace('\", \"', ',')
                
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # 指數退避
                    print(f"API 錯誤: {str(e)}. 等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    print(f"API 錯誤: {str(e)}. 已達到最大重試次數。")
                    return {"國家": "", "地點": "", "災害": ""}  # 返回空結果表示失敗

    # 讀取資料
    df = pd.read_csv('true_new.csv')  # 這是原始檔案，包含「內文」欄位

    # 根據內文欄位生成國家、地點和災害，並將其存放到新的欄位
    df[['國家', '地點', '災害']] = df['內文'].apply(lambda text: pd.Series(extract_information(text)))

    # 將結果寫入新的 CSV 檔案
    df.to_csv('add_locations.csv', index=False, encoding='utf-8')

    print("資訊生成完成，已儲存為 add_locations.csv")


    #3.水利署_event
    def extract_information(news_title, news_content):
        prompt = f"""
        event欄位根據資料集新聞標題和內文，判斷是否報導相同的災害事件，並分配一致的事件名稱。
        
        檢核標準：
        - 必須同時使用新聞標題和內文來判斷是否為相同的災害事件。
        - 若標題和內文描述的災害事件相同（即涉及相同災害類型、時間範圍），則必須分配相同的事件名稱。
        - 若標題和內文涉及不同的災害事件（例如不同時間或災害類型），則應分配不同的事件名稱。
        - 災害類型包含：大雨、豪雨、暴雨、淹水、洪水、水災、颱風、颶風、風災、地震、海嘯、乾旱、旱災、野火。
        - content欄位根據內文生成50-100字的摘要，需精確反映災害的核心信息。
        - summary欄位根據內文生成損失與災害的統整，需包含具體損失數據（如死亡人數、撤離人數、財產損失）及災害影響範圍。
        - 第一階段：event欄位只生成「國家+災害類型」，不包含地點。
        - 時間範圍的判斷：若災害事件持續多日，應視為同一事件，除非明確提到不同的災害發生。
        - 國家名稱標準化：將「韓國」統一轉為「南韓」，例如「韓國+野火」應輸出為「南韓+野火」；其他國家名稱保持標準化，如「台灣」、「美國」、「日本」等。
        - 災害類型標準化：將「暴雨」統一轉為「大雨」，例如「台灣+暴雨」應輸出為「台灣+大雨」。
        
        生成event時注意：
        - 國家：使用標準國家名稱，並遵循以下標準化規則：
        - 「韓國」轉為「南韓」。
        - 「台灣」、「美國」、「日本」等保持不變。
        - 災害類型：使用檢核標準中的名稱，並將「暴雨」轉為「大雨」，避免使用同義詞或變體。
        
        請直接輸出以下格式(用換行區分):
        event: "國家+災害類型"
        content: "<50-100字摘要>"
        summary: "<損失與災害的統整>"
        
        新聞標題:
        {news_title}
        
        新聞內容:
        {news_content}
        """

        response = chat_with_xai(prompt, xai_api_key, model_name, "")
        print("AI 回傳內容:", response)

        response_lines = response.strip().split("\n")
        result = {
            "event": "",
            "content": "",
            "summary": ""
        }

        for line in response_lines:
            key, _, value = line.partition(":")
            if key == "event":
                event = value.strip().strip('"').replace(" ", "")
                if "+" in event and len(event.split("+")) == 2:
                    country, disaster = event.split("+")
                    # 災害類型標準化：將「暴雨」轉為「大雨」
                    if disaster == "暴雨":
                        disaster = "大雨"
                    result["event"] = f"{country}+{disaster}"
                else:
                    result["event"] = event  # 保留原始值但不處理
            elif key == "content":
                result["content"] = value.strip().strip('"')
            elif key == "summary":
                result["summary"] = value.strip().strip('"')
        
        return result

    # 第一階段：生成初步的 event（只包含國家和災害類型）
    df = pd.read_csv('add_locations.csv')

    # 假設 add_locations.csv 已包含 '地點' 欄位，若無此欄位需額外處理
    if '地點' not in df.columns:
        raise ValueError("輸入檔案 'add_locations.csv' 缺少 '地點' 欄位")

    df['分析結果'] = df.apply(lambda row: extract_information(row['標題'], row['內文']), axis=1)
    df['event'] = df['分析結果'].apply(lambda x: x['event'])
    df['content'] = df['分析結果'].apply(lambda x: x['content'])
    df['summary'] = df['分析結果'].apply(lambda x: x['summary'])
    df = df.drop(columns=['分析結果'])

    # 第二階段：分組並更新 event，選擇單一地點並移除 "+"
    event_groups = defaultdict(list)

    # 將資料按 event 分組
    for index, row in df.iterrows():
        event = row['event']
        if event and "+" in event and len(event.split("+")) == 2:  # 檢查格式為 "國家+災害類型"
            country, disaster = event.split("+")
            # 若 '地點' 欄位包含多個地點（逗號分隔），分割並取第一個
            location = row['地點']
            if pd.notna(location) and ',' in str(location):
                location = str(location).split(',')[0].strip()  # 取第一個地點
            event_groups[(country, disaster)].append((index, location))
        else:
            print(f"警告: 第一階段 event 格式不正確 - {event}")

    # 統計每組中地點的出現次數並更新 event
    for (country, disaster), group in event_groups.items():
        # 統計地點頻率
        loc_count = defaultdict(int)
        for _, location in group:
            if pd.notna(location):  # 確保地點不是 NaN
                loc_count[location] += 1
        
        # 找出出現次數最多的地點
        if loc_count:
            max_count = max(loc_count.values())
            most_common_locations = [loc for loc, count in loc_count.items() if count == max_count]
            chosen_location = most_common_locations[0]  # 選擇第一個出現的地點
        else:
            chosen_location = "未知"  # 若無有效地點，設為 "未知"
        
        # 更新該組的 event，格式為 "國家地點災害類型"
        new_event = f"{country}{chosen_location}{disaster}"
        for index, _ in group:
            df.at[index, 'event'] = new_event

    # 儲存結果
    df.to_csv('add_events.csv', index=False, encoding='utf-8')

    print("資訊生成完成，已儲存為 add_events.csv")

    #4.水利署＿region
    # 國內關鍵字清單
    domestic_keywords = [
        '台灣', '台北', '新北', '基隆', '新竹市', '桃園', '新竹縣', '宜蘭', 
        '台中', '苗栗', '彰化', '南投', '雲林', '高雄', '台南', '嘉義', 
        '屏東', '澎湖', '花東', '花蓮', '台9線', '金門', '馬祖', '綠島', '蘭嶼',
        '臺灣', '台北', '臺中', '臺南', '臺9縣', '全台', '全臺'
    ]

    # 匯入 CSV 檔案
    input_file = 'add_events.csv'  # 替換成你的檔案名稱

    try:
        # 讀取 CSV 檔案
        df = pd.read_csv(input_file)

        # 確保內文欄位存在
        if '地點' not in df.columns:
            raise ValueError("CSV 檔案中沒有 '內文' 欄位")

        # 新增 region 欄位
        def determine_region(content):
            is_domestic = any(keyword in content for keyword in domestic_keywords)
            return '國內' if is_domestic else '國外'

        # 使用 apply 方法對每則新聞進行判斷
        df['region'] = df['地點'].apply(determine_region)

        # 將結果存回新的 CSV 檔案
        output_file = 'region.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"新增欄位 region 完成，結果已儲存到 {output_file}")

    except Exception as e:
        print(f"處理過程中出現錯誤：{str(e)}")

    #7.水利署_overview
    # 解析模糊時間（如「今日」、「昨日」）
    def process_relative_dates(text, reference_date):
        if not isinstance(reference_date, str) or not reference_date.strip():
            return text  # 若無可用的參考日期，則不修改

        try:
            reference_date = datetime.strptime(reference_date, "%Y-%m-%d")  # 轉換為 datetime 物件
        except ValueError:
            return text  # 若日期解析失敗則不修改文本

        replacements = {
            r"\b今日\b": reference_date.strftime("%Y-%m-%d"),
            r"\b今天\b": reference_date.strftime("%Y-%m-%d"),
            r"\b昨日\b": (reference_date - timedelta(days=1)).strftime("%Y-%m-%d"),
            r"\b昨天\b": (reference_date - timedelta(days=1)).strftime("%Y-%m-%d"),
            r"\b前天\b": (reference_date - timedelta(days=2)).strftime("%Y-%m-%d"),
        }

        for pattern, value in replacements.items():
            text = re.sub(pattern, value, text)

        return text

    def extract_explicit_date(text):
        """從內文中提取明確的 YYYY年MM月DD日 格式時間"""
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if date_match:
            year, month, day = date_match.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"
        return None

    def extract_relative_disaster_date(text, reference_date):
        """從內文中提取相對時間並轉換為標準日期，僅針對災害發生時間"""
        try:
            ref_date = datetime.strptime(reference_date, "%Y-%m-%d")
        except ValueError:
            return None

        relative_patterns = {
            r"\b(今日|今天)(凌晨|上午|下午|晚上)?\s*(\d{1,2}時\d{1,2}分)?\s*(發生|有)": ref_date,
            r"\b(昨日|昨天)(凌晨|上午|下午|晚上)?\s*(\d{1,2}時\d{1,2}分)?\s*(發生|有)": ref_date - timedelta(days=1),
            r"\b前天(凌晨|上午|下午|晚上)?\s*(\d{1,2}時\d{1,2}分)?\s*(發生|有)": ref_date - timedelta(days=2),
        }

        for pattern, date in relative_patterns.items():
            if re.search(pattern, text):
                return date.strftime("%Y-%m-%d")
        return None

    def has_disaster_time(text):
        """判斷內文是否包含災害發生的時間（標準格式或相對日期）"""
        # 檢查標準日期格式
        if re.search(r'\d{4}年\d{1,2}月\d{1,2}日', text):
            return True
        # 檢查相對日期關鍵詞並與災害相關
        relative_patterns = [
            r"\b(今日|今天|昨日|昨天|前天)(凌晨|上午|下午|晚上)?\s*(\d{1,2}時\d{1,2}分)?\s*(發生|有)"
        ]
        for pattern in relative_patterns:
            if re.search(pattern, text):
                return True
        return False

    def generate_overview(group):
        """針對 event 群組生成 summary 的總結"""
        reference_date = group['時間'].dropna().astype(str).min()  # 取得最早的時間

        group['summary'] = group['summary'].apply(lambda x: process_relative_dates(x, reference_date) if isinstance(x, str) else x)
        group['內文'] = group['內文'].apply(lambda x: process_relative_dates(x, reference_date) if isinstance(x, str) else x)

        explicit_dates = group['內文'].dropna().apply(extract_explicit_date).dropna()
        relative_dates = group['內文'].dropna().apply(lambda x: extract_relative_disaster_date(x, reference_date)).dropna()
        
        # 優先使用明確日期，若無則使用相對日期，最後用參考日期
        overview_date = explicit_dates.min() if not explicit_dates.empty else \
                        relative_dates.min() if not relative_dates.empty else reference_date

        combined_content = " ".join(group['summary'].dropna()) + " " + " ".join(group['內文'].dropna())

        if not combined_content.strip():
            return "無法生成摘要，資料不足"

        # 檢查內文是否包含災害時間
        has_time = any(group['內文'].dropna().apply(has_disaster_time))

        prompt = f"""
        根據以下所有相關事件的摘要（summary）和內文，生成一個有國家地點災害總整理的災害資訊摘要（overview）。
        
        請遵循以下規則：
        - 若內文明確提到災害發生的時間（如 2025年1月12日），則將該時間放在摘要最前面。
        - 若內文提到相對時間（如「今天凌晨5時30分發生」、「昨日發生」）且與災害相關，則參考 `時間` 欄位（{reference_date}）轉換為標準日期，並放在摘要最前面。
        - 若內文沒有提到災害發生的時間，則不要在摘要前面加入時間。
        - 確保使用的時間是災害發生的時間，而非其他無關時間（如新聞發布時間）。
        
        檢核標準：
        1. 時間準確：若有時間，必須是災害發生的時間。
        2. 內容完整：摘要需包含地點、災害類型、影響範圍及後續發展。
        3. 結構清晰：若涉及多個事件，應按時間順序或重要性整理。
        4. 字數限制：摘要須控制在 100-150 字。
        
        事件參考時間：{reference_date}
        內文是否包含災害時間：{has_time}
        災害發生時間（若有）：{overview_date}
        
        相關事件摘要（summary 和 內文）：
        {combined_content}
        
        範例事件摘要（summary）：
        1. 2024年12月23日，第26號颱風帕布生成，預計朝中南半島方向移動，對台灣無直接影響，但外圍水氣將導致全台轉雨。
        2. 今天凌晨5時30分，南太平洋島國萬那杜發生規模7.4地震，震源深度10公里，隨後發布海嘯警報。
        
        請直接輸出：
        overview: "<災害資訊摘要>"
        """

        response = chat_with_xai(prompt, xai_api_key, model_name, "")
        
        if response:
            overview_line = response.strip().split(":")
            clean_overview = overview_line[1].strip().strip('"').replace("*", "") if len(overview_line) > 1 else "無法生成摘要"
            return clean_overview
        return "無法生成摘要"

    # 讀取 CSV
    df = pd.read_csv('region.csv')

    # 確保 `event` 欄位為分類群組
    df['event'] = df['event'].astype(str)

    # 先生成 overview，再合併回原始 df
    overview_df = df.groupby('event', group_keys=False).apply(generate_overview).reset_index()
    overview_df.columns = ['event', 'overview']

    # 合併回 df，確保 overview 放在正確的 event 上
    df = df.merge(overview_df, on='event', how='left')

    # 儲存結果
    df.to_csv('add_overview.csv', index=False, encoding='utf-8')
    print("修正後的 overview 已存入 add_overview.csv")


    #8.水利署_合併
    #補齊欄位
    # 讀取 CSV 檔案
    df = pd.read_csv('add_overview.csv')  

    # 定義欄位名稱對應關係
    column_mapping = {
        '標題': 'title',
        '連結': 'url',
        '來源': 'publisher',
        '時間': 'date',
        '圖片': 'cover'
    }

    # 執行欄位名稱更改
    df = df.rename(columns=column_mapping)

    # 2. 刪除不要的欄位
    columns_to_drop = ['內文', 'is_disaster', '災害']
    df = df.drop(columns=columns_to_drop, errors='ignore')  # errors='ignore' 確保即使欄位不存在也不會報錯

    # 3. 補上缺失欄位
    # recent_update：選擇 date 欄位中最新的時間
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')  # 確保 date 欄位是日期格式
        df['recent_update'] = df['date'].max()  # 選取最新的時間
    else:
        df['recent_update'] = pd.NaT  # 如果 date 欄位不存在，填入 NaT（缺失值）

    # location：將「國家」和「地點」合併成一個欄位
    if '國家' in df.columns and '地點' in df.columns:
        df['location'] = df['國家'].fillna('') + ' ' + df['地點'].fillna('')  # 合併「國家」和「地點」，並處理缺失值
        df['location'] = df['location'].str.strip()  # 去除多餘的空格
    else:
        df['location'] = ''  # 如果「國家」或「地點」欄位不存在，則新增空的 location 欄位

    # 4. 新增 author 和 publish_date 欄位
    # author：與 publisher 欄位相同
    if 'publisher' in df.columns:
        df['author'] = df['publisher']
    else:
        df['author'] = ''  # 如果 publisher 欄位不存在，則填入空字串

    # publish_date：與 date 欄位相同
    if 'date' in df.columns:
        df['publish_date'] = df['date']
    else:
        df['publish_date'] = pd.NaT  # 如果 date 欄位不存在，則填入 NaT（缺失值）

    # 5. 刪除「國家」和「地點」欄位
    columns_to_drop_after_merge = ['國家', '地點']
    df = df.drop(columns=columns_to_drop_after_merge, errors='ignore')  # errors='ignore' 確保即使欄位不存在也不會報錯

    # 6.新增步驟：移除相同 title 的重複項目，只保留第一個出現的
    if 'title' in df.columns:
        df = df.drop_duplicates(subset='title', keep='first')

    # 7. 輸出到新的 CSV 檔案
    output_file = '補齊欄位.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"處理完成，已輸出到 {output_file}")

    #合併欄位
    # 讀取 CSV 檔案
    df = pd.read_csv('補齊欄位.csv')

    # 初始化一個空的列表，用來存放最終的結構
    result = []

    # 按照 event 進行分組，所有具有相同 'event' 值的行會被分到同一組
    for event, group in df.groupby('event'):
        # 選擇第一個新聞的數據作為基本信息
        first_row = group.iloc[0]
        
        # 處理 cover 欄位，若為 NaN 則設為空字串
        cover = first_row['cover'] if pd.notna(first_row['cover']) else ""
        
        # 找到該 event 組內最新的日期作為 recent_update
        recent_update = group['date'].max()
        
        # 找到該 event 組內最早的日期作為 date
        earliest_date = group['date'].min()
        
        # 初始化當前事件的字典
        event_data = {
            "event": event,
            "region": first_row['region'],
            "cover": cover,
            "date": earliest_date,  # 使用該 event 組內最早的日期
            "recent_update": recent_update,  # 使用該 event 組內最新的日期
            "location": first_row['location'].split(',') if pd.notna(first_row['location']) else [],
            "overview": first_row['overview'],
            "daily_records": [],
            "links": []
        }

        # 處理 daily_records，遍歷所有資料
        unique_daily_records = group[['date', 'content', 'location']].drop_duplicates()
        for _, row in unique_daily_records.iterrows():
            daily_record = {
                "date": row['date'],
                "content": row['content'],
                "location": row['location'].split(',') if pd.notna(row['location']) else []
            }
            event_data["daily_records"].append(daily_record)

        # 排序 daily_records 按照日期由舊到新
        event_data["daily_records"].sort(key=lambda x: x["date"])

        # 去除 links 中 title 重複的資料
        unique_links = group.drop_duplicates(subset=["title"])

        for _, row in unique_links.iterrows():
            link = {
                "source": {
                    "publisher": row['publisher'],
                    "author": row['author']
                },
                "url": row['url'],
                "title": row['title'],
                "publish_date": row['publish_date'],
                "location": row['location'].split(',') if pd.notna(row['location']) else [],
                "summary": row['summary']
            }
            event_data["links"].append(link)

        # 將每個事件的數據添加到結果列表中
        result.append(event_data)

    # 將結果列表轉換為 JSON 格式並寫入檔案
    with open('final.json', 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=2)

    print("JSON 文件已生成並命名為 'final.json'。")
    return JsonResponse({"message": "新聞AI運行完成"})

# 檔案處理
CSV_FILE_PATH = 'w2.csv'
JSON_FILE_PATH = 'final.json'

@require_GET
def view_raw_news(request):
    try:
        # 取得請求格式 (json 或 csv)，預設為 json
        data_format = request.GET.get('format', 'json').lower()

        if data_format == 'csv':
            # 檢查 CSV 檔案是否存在
            if not os.path.exists(CSV_FILE_PATH):
                return JsonResponse({'error': 'CSV 檔案不存在'}, status=404)

            # 讀取 CSV 檔案
            news_df = pd.read_csv(CSV_FILE_PATH)

            # 準備 JSON 格式的新聞列表
            news_list = []
            for _, row in news_df.iterrows():
                content = row.get('內文', '') or ''
                if len(content) > 100:
                    content = content[:100] + '...'

                news_item = {
                    '來源': row.get('來源', '') or '',
                    '作者': row.get('來源', '') or '',
                    '標題': row.get('標題', '') or '',
                    '連結': row.get('連結', '') or '',
                    '內文': content,
                    '時間': row.get('時間', '') or '',
                    '圖片': row.get('圖片', '') or ''
                }
                news_list.append(news_item)

            return JsonResponse(news_list, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})

        else:
            # 檢查 JSON 檔案是否存在
            if not os.path.exists(JSON_FILE_PATH):
                return JsonResponse({'error': 'JSON 檔案不存在'}, status=404)

            # 讀取 JSON 檔案內容
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
                data = json.load(file)

            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    




# 新增函數 run_crawler_and_ai
def run_crawler_and_ai(request):
    print("run_crawler_and_ai 被呼叫")

    # 呼叫第一階段爬蟲
    crawler_response = crawler_first_stage(request)
    if crawler_response.status_code != 200:
        return JsonResponse({'error': 'Crawler failed'}, status=500)

    # 呼叫 AI 處理
    ai_response = news_ai(request)
    if ai_response.status_code != 200:
        return JsonResponse({'error': 'AI failed'}, status=500)

    return JsonResponse({
        'status': 'all done',
        'crawler': crawler_response.content.decode(),
        'ai': ai_response.content.decode(),
    })