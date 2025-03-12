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

# 修改 ALLOWED_SOURCES 為只包含四家報社
ALLOWED_SOURCES = {
    'Newtalk新聞',
    '經濟日報',
    '自由時報',
    # '中時新聞網',
    'BBC News 中文'
}
 
# 定義允許的自然災害關鍵字
DISASTER_KEYWORDS = {
    '大雨', '豪雨', '暴雨', '淹水', '洪水', '水災',
    '颱風', '颶風', '風災',
    '地震', '海嘯',
    '乾旱', '旱災','大火','野火'
}

# 關鍵字設定 - 用於判斷國內新聞
domestic_keywords = [
    '台灣', '台北', '新北', '基隆', '新竹市', '桃園', '新竹縣', '宜蘭', 
    '台中', '苗栗', '彰化', '南投', '雲林', '高雄', '台南', '嘉義', 
    '屏東', '澎湖', '花東', '花蓮', '台9線', '金門', '馬祖', '綠島', '蘭嶼',
    '臺灣', '台北', '臺中', '臺南', '臺9縣', '全台', '全臺'
]

# 設定ai _api最大重試次數和初始延遲時間
max_retries = 3  # 最大重試次數
retry_delay = 2  # 初始延遲2秒

#從google news抓取資料(標題、新聞來源、時間)
def fetch_news(url):
    try:
        # 設置 HTTP 請求的標頭，模擬瀏覽器行為
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 發送 GET 請求到指定的 url，並包含標頭
        response = requests.get(url, headers=headers)
        # 檢查請求是否成功，若不成功則引發異常
        response.raise_for_status()
        # 使用 BeautifulSoup 解析 HTML 內容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有符合條件的 article 或 div 標籤
        articles = soup.find_all(['article', 'div'], class_=['IFHyqb', 'xrnccd', 'IBr9hb', 'NiLAwe'])
        # 初始化一個空列表，用於存儲抓取到的新聞項目
        news_list = []

        # 將 ALLOWED_SOURCES 轉換為集合，以便於快速查找
        allowed_sources_set = set(ALLOWED_SOURCES)

        # 遍歷每一個抓取到的 article
        for article in articles:
            try:
                # 查找文章中的標題元素
                title_element = article.find(['a', 'h3', 'h4'], class_=['JtKRv', 'ipQwMb', 'DY5T1d', 'gPFEn']) or article.find('a', recursive=True)
                if not title_element:
                    continue  # 如果找不到標題元素，則跳過當前文章

                # 提取標題的文本內容
                title = title_element.get_text(strip=True)
                # 獲取標題元素的 href 屬性，即新聞的連結
                link = title_element.get('href', '')
                # 根據 link 的格式進行處理，將相對路徑轉換為絕對路徑
                link = f'https://news.google.com/{link[2:]}' if link.startswith('./') else f'https://news.google.com{link}' if link.startswith('/') else link

                # 查找新聞來源的元素
                source_element = article.find(['div', 'a'], class_=['vr1PYe', 'wEwyrc', 'SVJrMe', 'NmQAAc']) or article.find(lambda tag: tag.name in ['div', 'a'] and 'BBC' in tag.get_text())
                if not source_element:
                    continue  # 如果找不到來源元素，則跳過當前文章

                # 提取來源的文本內容
                source_name = source_element.get_text(strip=True)
                # 如果來源名稱中包含 'BBC'，則將其標記為 'BBC News 中文'
                source_name = 'BBC News 中文' if 'BBC' in source_name else source_name

                # 檢查來源名稱是否在允許的來源集合中
                if source_name not in allowed_sources_set:
                    continue  # 如果不在，則跳過當前文章

                # 查找文章中的時間元素
                time_element = article.find(['time', 'div'], class_=['UOVeFe', 'hvbAAd', 'WW6dff', 'LfVVr'])
                # 提取時間的文本內容，如果找不到時間元素，則設置為 '未知'
                date_str = time_element.get_text(strip=True) if time_element else '未知'
                # 調用 parse_date 函數解析日期字符串
                date = parse_date(date_str)

                # 創建一個字典，包含標題、連結、來源和時間
                news_item = {
                    '標題': title,
                    '連結': link,
                    '來源': source_name,
                    '時間': date
                }

                # 將 news_item 添加到 news_list 列表中
                news_list.append(news_item)

            except Exception as e:
                print(f"處理文章時發生錯誤: {str(e)}")  # 如果在處理文章的過程中發生異常，則打印錯誤信息
                continue  # 繼續處理下一篇文章

        return news_list  # 返回抓取到的所有新聞項目列表

    except Exception as e:
        print(f"抓取新聞時發生錯誤: {str(e)}")  # 如果在整個 try 區塊中發生異常，則打印錯誤信息
        return []  # 返回空列表

# 解析 google news上的日期字符串
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
            # 如果日期字符串中沒有年份，添加當前年份
            if '年' not in date_str:
                date_str = f'{current_date.year}年{date_str}'
            date = datetime.strptime(date_str, '%Y年%m月%d日')
        except ValueError:
            # 如果解析失敗，使用當前日期
            date = current_date

    return date.strftime('%Y-%m-%d')

def setup_chrome_driver():
    chrome_options = Options()  # 創建一個 ChromeOptions 物件，用於設置 Chrome 瀏覽器的選項
    chrome_options.add_argument('--headless')  # 設置為無頭模式，不顯示瀏覽器界面
    chrome_options.add_argument('--no-sandbox')  # 禁用沙盒模式，通常在 CI/CD 環境中使用
    chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用 /dev/shm 使用，解決資源限制問題
    chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速，避免某些環境中的問題
    chrome_options.add_argument('--disable-software-rasterizer')  # 禁用軟體光柵化器，進一步減少資源使用
    chrome_options.add_argument('--ignore-certificate-errors')  # 新增：忽略憑證錯誤
    chrome_options.add_argument('--ignore-ssl-errors')  # 新增：忽略 SSL 錯誤
    
    service = Service(ChromeDriverManager().install())  # 使用 ChromeDriverManager 安裝 ChromeDriver 並創建服務
    driver = webdriver.Chrome(service=service, options=chrome_options)  # 創建 Chrome 瀏覽器的 WebDriver 實例
    return driver  # 返回創建的 WebDriver 實例


# 函數：獲取最終網址（處理 Google News 跳轉）
def get_final_url(driver, url):
    try:
        # 使用 Selenium 載入 Google News 跳轉頁面
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))  # 等待頁面載入
        )
        # 獲取頁面中所有跳轉連結
        final_url = driver.current_url  # 獲取當前頁面的 URL（跳轉後）
        return final_url
    except Exception as e:
        print(f"獲取最終網址失敗: {e}")
        return url  # 如果失敗，返回原始 URL

# 函數：爬取文章內容
def fetch_article_content(driver, sources_urls):
    # 初始化一個字典，用於存儲每個來源的內容
    results = {}
    # 初始化一個字典，用於存儲每個來源的摘要
    summaries = {}
    # 初始化一個字典，用於存儲最終網址
    final_urls = {}

    # 定義不同新聞來源的內容選擇器
    content_selectors = {
        'Newtalk新聞': 'div.articleBody.clearfix p',
        '經濟日報': 'section.article-body__editor p',
        '自由時報': 'div.text p',
        # '中時新聞網': 'div.article-body p',
        'BBC News 中文': 'div.bbc-1cvxiy9 p'
    }

    # 遍歷每個來源名稱和對應的 URL
    for source_name, url in sources_urls.items():
        # 如果來源不在允許的來源中，則跳過
        if source_name not in ALLOWED_SOURCES:
            continue

        try:
            # 獲取最終網址（處理 Google News 跳轉）
            final_url = get_final_url(driver, url)
            final_urls[source_name] = final_url  # 存儲最終網址

            # 使用最終網址爬取內容
            driver.get(final_url)  # 載入最終網址
            # 等待頁面中出現至少一個段落元素
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p'))
            )

            # 根據來源名稱獲取對應的內容選擇器
            selector = content_selectors.get(source_name)
            if not selector:  # 如果沒有對應的選擇器，則跳過
                continue

            # 獲取所有符合選擇器的段落元素
            paragraphs = driver.find_elements(By.CSS_SELECTOR, selector)
            # 提取段落的文本內容，並將其合併為一個字符串
            content = '\n'.join(p.text.strip() for p in paragraphs if p.text.strip())
            # 獲取內容的前 100 個字符作為摘要
            summary = content[:100] if content else '未找到內容'

            # 存儲內容和摘要
            results[source_name] = content if content else '未找到內容'
            summaries[source_name] = summary

        except Exception as e:
            # 如果抓取內容失敗，打印錯誤信息
            print(f"抓取內容失敗: {e}")
            results[source_name] = '錯誤'  # 設置結果為錯誤
            summaries[source_name] = '錯誤'  # 設置摘要為錯誤
            final_urls[source_name] = url  # 如果失敗，返回原始 URL

    # 返回所有來源的內容、摘要和最終網址
    return results, summaries, final_urls

# 爬取圖片 URL
def extract_image_url(driver, sources_urls):
    # 初始化一個字典，用於存儲每個來源的圖片 URL
    results = {}
    
    # 定義不同新聞來源的圖片選擇器
    image_selectors = {
        'Newtalk新聞': "div.news_img img",
        '經濟日報': "section.article-body__editor img",
        '自由時報': "div.image-popup-vertical-fit img",
        # '中時新聞': "div.article-body img",
        'BBC News 中文': "div.bbc-1cvxiy9 img"
    }

    # 遍歷每個來源名稱和對應的 URL
    for source_name, url in sources_urls.items():
        # 如果來源不在允許的來源中，則跳過
        if source_name not in ALLOWED_SOURCES:
            continue
            
        try:
            # 載入來源的 URL
            driver.get(url)
            # 根據來源名稱獲取對應的圖片選擇器
            selector = image_selectors.get(source_name)
            if not selector:  # 如果沒有對應的選擇器，跳過
                continue
            
            # 特別處理 BBC 新聞圖片
            if source_name == 'BBC News 中文':
                try:
                    # 查找 BBC 新聞的內容區域
                    content_div = driver.find_element(By.CSS_SELECTOR, 'div.bbc-1cvxiy9')
                    if content_div:
                        # 查找該區域中的第一張圖片
                        first_image = content_div.find_element(By.TAG_NAME, 'img')
                        # 如果找到圖片且其外部 HTML 包含 'src'，則提取圖片 URL
                        if first_image and 'src' in first_image.get_attribute('outerHTML'):
                            results[source_name] = first_image.get_attribute('src')
                            continue
                except Exception as e:
                    print(f"無法找到 BBC 新聞圖片: {e}")  # 新增錯誤處理

            # 提取其他來源的圖片
            image_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # 提取圖片的 URL
            image_url = image_element.get_attribute('src') or image_element.get_attribute('data-src')
            results[source_name] = image_url or ''  # 如果沒有找到圖片，則設置為空字串
            
        except Exception as e:
            print(f"圖片擷取錯誤: {e}")  # 如果抓取圖片過程中發生錯誤，則打印錯誤信息
            results[source_name] = ''  # 如果發生錯誤，則設置為空字串
            
    # 返回所有來源的圖片 URL
    return results

# #測試爬蟲：開始爬蟲url http://localhost:8000/api/news/
# #測試爬蟲：ai處理 api http://localhost:8000/api/news/ai/
# #測試爬蟲：開啟後端api http://localhost:8000/api/news/sql/  
@require_GET
def crawler_first_stage(request):
    try:
        start_time = time.time()
        day = "30"
        
        # Google News 搜尋 URL
        urls = [
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%xA8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#國際大雨
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
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際大火＝野火
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際野火
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
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際大火＝野火
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'#新增國際野火      
            ]
        
        # 主程式邏輯
        all_news_items = []  # 初始化一個空列表，用於存儲所有抓取到的新聞項目
        start_crawl_time = time.time()  # 記錄爬取開始的時間
        for url in urls:  # 遍歷每個要抓取的 URL
            news_items = fetch_news(url)  # 使用 fetch_news 函數抓取新聞項目
            all_news_items.extend(news_items)  # 將抓取到的新聞項目添加到 all_news_items 列表中

        if all_news_items:  # 如果抓取到的新聞項目不為空
            news_df = pd.DataFrame(all_news_items)  # 將新聞項目轉換為 DataFrame
            news_df = news_df.drop_duplicates(subset='標題', keep='first')  # 刪除重複的標題，保留第一個

            end_crawl_time = time.time()  # 記錄爬取結束的時間
            crawl_time = int(end_crawl_time - start_crawl_time)  # 計算爬取所花費的時間
            hours, remainder = divmod(crawl_time, 3600)  # 將總秒數轉換為小時和剩餘秒數
            minutes, seconds = divmod(remainder, 60)  # 將剩餘秒數轉換為分鐘和秒數
            
            time_str = ''  # 初始化時間字符串
            if hours > 0:  # 如果有小時數
                time_str += f'{hours}小時'  # 添加小時數到時間字符串
            if minutes > 0 or hours > 0:  # 如果有分鐘數或小時數
                time_str += f'{minutes}分'  # 添加分鐘數到時間字符串
            time_str += f'{seconds}秒'  # 添加秒數到時間字符串
            
            print(f'Google News 爬取完成，耗時：{time_str}')  # 打印爬取完成的消息和耗時

            driver = setup_chrome_driver()  # 設置 Chrome 驅動

            # 刪除舊的 CSV 檔案（如果存在）
            first_stage_file = 'w2.csv'  # 定義要儲存的 CSV 檔案名稱
            if os.path.exists(first_stage_file):  # 如果檔案存在
                os.remove(first_stage_file)  # 刪除舊的 CSV 檔案

            for index, item in news_df.iterrows():  # 遍歷每一行新聞項目
                source_name = item['來源']  # 獲取來源名稱
                original_url = item['連結']  # 獲取原始連結
                sources_urls = {source_name: original_url}  # 將來源名稱和連結組成字典

                # 擷取內容和最終網址
                content_results, _, final_urls = fetch_article_content(driver, sources_urls)  # 獲取內容和最終網址
                image_results = extract_image_url(driver, sources_urls)  # 照片部分保持不變

                content = content_results.get(source_name, '')  # 確保空值為空字串
                final_url = final_urls.get(source_name, original_url)  # 使用最終網址，若無則使用原始 URL
                image_url = image_results.get(source_name, '')  # 確保空值為空字串

                # 準備要存入 CSV 的資料
                result = {
                    '標題': item['標題'],  # 新聞標題
                    '連結': final_url,  # 使用最終網址
                    '內文': content or '',  # 確保空值為空字串
                    '來源': source_name,  # 新聞來源
                    '時間': item['時間'],  # 新聞時間
                    '圖片': image_url or ''  # 確保空值為空字串
                }

                # 儲存資料到 CSV
                output_df = pd.DataFrame([result])  # 將結果轉換為 DataFrame
                output_df.to_csv(first_stage_file, mode='a', header=not os.path.exists(first_stage_file), 
                                index=False, encoding='utf-8')  # 追加寫入 CSV 檔案

                print(f"已儲存新聞: {result['標題']}")  # 打印已儲存的新聞標題

            driver.quit()  # 關閉 Chrome 驅動

            return JsonResponse({  # 返回成功的 JSON 響應
                'status': 'success',
                'message': f'第一階段爬蟲完成！耗時：{time_str}',  # 爬蟲完成的消息
                'csv_file': first_stage_file,  # 返回的 CSV 檔案名稱
                'total_news': len(news_df)  # 返回抓取到的新聞數量
            })

        return JsonResponse({  # 如果沒有找到新聞，返回錯誤的 JSON 響應
            'status': 'error',
            'message': '沒有找到新聞'
        })

    except Exception as e:  # 捕捉任何異常
        return JsonResponse({  # 返回錯誤的 JSON 響應
            'status': 'error',
            'message': f'爬蟲執行失敗：{str(e)}'  # 返回錯誤信息
        }, status=500)  # 設置 HTTP 狀態碼為 500

#ai 處理
xai_api_key = "xai-sEKM3YfLj81l66aMWyXpmasF8Xab7hvpcwtEY4WU0jIeJfEoWDPSjm5VjbH9bq9JDNN5SmAAIrGyjfPN"
model_name = "grok-beta"

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



    #2.水利署＿判斷是否為相同事件
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
        event欄位根據資料集新聞標題和內文，判斷是否報導相同的災害事件，並分配完全一致的事件名稱。需確保事件名稱的唯一性和一致性，避免因地點表述的細微差異（如州、縣、城市等層級不同）導致錯誤的分類。
        
        檢核標準：
        - 必須同時使用新聞標題和內文來判斷是否為相同的災害事件。
        - 若標題和內文描述的災害事件相同（即涉及相同災害類型、時間範圍），則必須分配完全相同的事件名稱，即使地點描述存在差異。
        - 若標題和內文涉及不同的災害事件（例如不同時間或災害類型），則應分配不同的事件名稱。
        - 災害類型包含：大雨、豪雨、暴雨、淹水、洪水、水災、颱風、颶風、風災、地震、海嘯、乾旱、旱災、野火。
        - content欄位根據內文生成50-100字的摘要，需精確反映災害的核心信息。
        - summary欄位根據內文生成損失與災害的統整，需包含具體損失數據（如死亡人數、撤離人數、財產損失）及災害影響範圍。
        - 必須確保標題和內文中的關鍵詞（如災害類型、時間）與事件名稱的高度對應性，避免因表述差異導致誤判。
        - 若多篇新聞報導的是相同災害事件（即相同災害類型和時間範圍），則event欄位必須使用完全相同的名稱，不因地點的具體差異而被分到不同的event。例如：「台灣嘉義地震」與「台灣嘉義縣地震」應視為相同事件；「美國加州野火」與「美國洛杉磯野火」也應視為相同事件。
        - **新增規則：若災害發生在同一國家且為同一災害類型，無論地點如何變化，event欄位應使用相同的名稱，但地點應選擇報導中提到的最多次的地點。例如：「台灣台南地震」、「台灣嘉義地震」如果都是同一災害事件，應統一使用提到次數最多或最具代表性的地點名稱，如「台灣嘉義地震」或「台灣台南地震」。**
        - event欄位應根據「國家+地點+災害類型」組合成一個標準化、唯一的識別名稱。
        - 若多篇新聞報導相同災害事件（例如：同一個野火事件、同一次地震），即使標題或內文描述的具體細節不同，event欄位的名稱也必須完全一致。
        - 時間範圍的判斷：若災害事件持續多日，應視為同一事件，除非明確提到不同的災害發生。
        
        生成event時注意：
        - 國家、地點和災害類型的組合必須簡潔且標準化：
        - 國家：使用標準國家名稱。
        - 地點：選擇報導中提到的最多次的地點名稱，忽略州、縣、市、城市等層級差異。
        - 災害類型：使用檢核標準中的災害類型名稱，避免使用同義詞或變體。
        - 例如：
        - 若多篇新聞提到「嘉義地震」、「台南地震」，應選擇「嘉義」或「台南」中出現次數最多者為代表，統一命名為「台灣嘉義地震」或「台灣台南地震」。
        - 若多篇新聞提到「洛杉磯野火」、「加州野火」，應選擇「洛杉磯」或「加州」中出現次數最多者，統一命名為「美國洛杉磯野火」或「美國加州野火」。
        
        請直接輸出以下格式(用換行區分):
        event: "國家+地點+災害類型"
        content: "<50-100字摘要>"
        summary: "<損失與災害的統整>"
        
        新聞標題:
        {news_title}
        
        新聞內容:
        {news_content}

        """

        for attempt in range(max_retries):
            try:
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
                        result["event"] = value.strip().strip('"').replace(" ", "")  # 移除所有空格
                    elif key == "content":
                        result["content"] = value.strip().strip('"')
                    elif key == "summary":
                        result["summary"] = value.strip().strip('"')
                
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # 指數退避
                    print(f"API 錯誤: {str(e)}. 等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    print(f"API 錯誤: {str(e)}. 已達到最大重試次數。")
                    return {"event": "", "content": "", "summary": ""}  # 返回空結果表示失敗

    df = pd.read_csv('add_locations.csv')

    df['分析結果'] = df.apply(lambda row: extract_information(row['標題'], row['內文']), axis=1)

    df['event'] = df['分析結果'].apply(lambda x: x['event'])
    df['content'] = df['分析結果'].apply(lambda x: x['content'])
    df['summary'] = df['分析結果'].apply(lambda x: x['summary'])

    df = df.drop(columns=['分析結果'])

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
        if '內文' not in df.columns:
            raise ValueError("CSV 檔案中沒有 '內文' 欄位")

        # 新增 region 欄位
        def determine_region(content):
            is_domestic = any(keyword in content for keyword in domestic_keywords)
            return '國內' if is_domestic else '國外'

        # 使用 apply 方法對每則新聞進行判斷
        df['region'] = df['內文'].apply(determine_region)

        # 將結果存回新的 CSV 檔案
        output_file = 'region.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"新增欄位 region 完成，結果已儲存到 {output_file}")

    except Exception as e:
        print(f"處理過程中出現錯誤：{str(e)}")

    #7.水利署_overview
    # 解析模糊時間（如「今日」、「昨日」）
    def generate_overview(group, xai_api_key, model_name, use_summary_only=False):
        """
        使用 AI 生成災害資訊摘要。
        - 預設根據 summary、內文 和 時間
        - 如果 use_summary_only=True，則僅使用 summary 內容
        """
        if use_summary_only:
            combined_content = " ".join(group['summary'].dropna())
        else:
            reference_date = group['時間'].dropna().astype(str).min()
            overview_date = reference_date if pd.notna(reference_date) else "未知時間"

            # 嘗試從內文中提取更準確的日期
            for content in group['內文'].dropna():
                date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', content)
                if date_match:
                    year, month, day = date_match.groups()
                    overview_date = f"{year}-{int(month):02d}-{int(day):02d}"
                    break

            combined_content = " ".join(group['summary'].dropna()) + " " + " ".join(group['內文'].dropna())

        if not combined_content.strip():
            return "無法生成摘要，資料不足"

        prompt = f"""
        根據以下所有相關事件的摘要（summary）和內文，生成一個總整理的災害資訊摘要（overview），不得自行增加不相干的內容。
        請務必從摘要和內文中提取災害發生的時間，並將該時間放在摘要的最前面：
        - 若 `內文` 明確寫出時間（如 2025年1月12日），則直接使用該時間，並放在 `overview` 最前面。
        - 若 `內文` 沒有提及任何時間資訊，則使用 `時間` 欄位內的時間放在 `overview` 最前面。
        檢核標準：
        1. 時間準確：應該是災害發生的時間，而非新聞發布時間。
        2. 內容完整：摘要需包含 時間、地點、災害類型、影響範圍及後續發展。
        3. 結構清晰：若涉及多個事件，應按 時間順序或重要性整理。
        4. 字數限制：摘要須控制在 100-150 字。        
        {"(不包含時間)" if use_summary_only else f"事件發生時間：{overview_date}"}
        
        相關事件摘要：
        {combined_content}
        
        請直接輸出：
        overview: "<災害資訊摘要>"
        """

        response = chat_with_xai(prompt, xai_api_key, model_name, "")
        print("API 回應:", response)

        if response:
            overview_line = response.strip().split(":")
            clean_overview = overview_line[1].strip().strip('"').replace("*", "") if len(overview_line) > 1 else "無法生成摘要"
            return clean_overview
        else:
            return "無法生成摘要"

    # 讀取 CSV
    df = pd.read_csv('region.csv')

    # 確保 'event' 欄位為字符串，避免 groupby 產生問題
    df['event'] = df['event'].astype(str)

    # 只保留需要的欄位
    content_columns = ['summary', '內文', '時間']

    # 針對每個 event 群組生成 overview，確保對應正確
    overview_dict = df.groupby('event')[content_columns].apply(lambda group: generate_overview(group, xai_api_key, model_name)).to_dict()

    # 將生成的 overview 正確映射回原始 DataFrame
    df['overview'] = df['event'].map(overview_dict)

    # 重新檢查，對 NaN 或 "無法生成摘要" 的 overview 進行修正（僅使用 summary）
    df['overview'] = df.apply(
        lambda row: generate_overview(df[df['event'] == row['event']], xai_api_key, model_name, use_summary_only=True)
        if pd.isna(row['overview']) or row['overview'].strip() == "無法生成摘要" else row['overview'],
        axis=1
    )

    # 儲存結果
    df.to_csv('add_overview.csv', index=False, encoding='utf-8')
    print("災害資訊生成完成，已儲存為 add_overview.csv")


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