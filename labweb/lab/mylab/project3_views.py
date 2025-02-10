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

# API 調用頻率控制
class RateLimiter:
    def __init__(self, calls_per_second=1):
        self.calls_per_second = calls_per_second
        self.last_call = 0
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            current_time = time.time()
            time_since_last_call = current_time - self.last_call
            if time_since_last_call < 1.0 / self.calls_per_second:
                time.sleep(1.0 / self.calls_per_second - time_since_last_call)
            self.last_call = time.time()

# 建立全域的 rate limiter 實例
rate_limiter = RateLimiter(calls_per_second=0.5)  # 每2秒最多一次調用

xai_api_key = "xai-sEKM3YfLj81l66aMWyXpmasF8Xab7hvpcwtEY4WU0jIeJfEoWDPSjm5VjbH9bq9JDNN5SmAAIrGyjfPN"
model_name = "grok-beta"

# 修改 ALLOWED_SOURCES 為只包含四家報社
ALLOWED_SOURCES = {
    'Newtalk新聞',
    '經濟日報',
    '自由時報',
    '中時新聞',
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

#自動化從新聞網站抓取新聞資料
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

        allowed_sources_set = set(ALLOWED_SOURCES)  # 將 ALLOWED_SOURCES 轉換為集合

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

                if source_name not in allowed_sources_set:  # 使用集合進行查找
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
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--ignore-certificate-errors')  # 新增：忽略憑證錯誤
    chrome_options.add_argument('--ignore-ssl-errors')         # 新增：忽略 SSL 錯誤
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

#從 Google News 的 URL 中提取出最終的 URL
def extract_final_url(google_news_url):
    match = re.search(r'(https?://[^&]+)', google_news_url)
    if match:
        return match.group(1)
    return google_news_url

# 從指定的新聞來源 URL 中抓取文章的內容
def fetch_article_content(driver, sources_urls):
    results = {}
    summaries = {}
    
    content_selectors = {
        'Newtalk新聞': 'div.articleBody.clearfix p',
        '經濟日報': 'section.article-body__editor p',
        '自由時報': 'div.text p',
        '中時新聞': 'div.article-body p',
        'BBC News 中文': 'div.bbc-1cvxiy9 p'  # 確保選擇器正確
    }

    for source_name, url in sources_urls.items():
        if source_name not in ALLOWED_SOURCES:
            continue
            
        try:
            driver.get(url)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p'))
            )
            
            selector = content_selectors.get(source_name)
            if not selector:  # 如果沒有對應的選擇器，跳過
                continue
            
            # 提取內容
            paragraphs = driver.find_elements(By.CSS_SELECTOR, selector)
            content = '\n'.join(p.text.strip() for p in paragraphs if p.text.strip())
            summary = content[:100] if content else '未找到內容'
            
            # 特別處理 BBC 新聞
            if source_name == 'BBC News 中文':
                # 確保選擇器正確，並提取內容
                bbc_paragraphs = driver.find_elements(By.CSS_SELECTOR, 'div.bbc-1cvxiy9 p')
                content = '\n'.join(p.text.strip() for p in bbc_paragraphs if p.text.strip())
            
            results[source_name] = content if content else '未找到內容'
            summaries[source_name] = summary
            
        except Exception as e:
            print(f"抓取內容失敗: {e}")
            results[source_name] = '錯誤'
            summaries[source_name] = '錯誤'
            
    return results, summaries

def extract_image_url(driver, sources_urls):
    results = {}
    
    image_selectors = {
        'Newtalk新聞': "div.news_img img",
        '經濟日報': "section.article-body__editor img",
        '自由時報': "div.image-popup-vertical-fit img",
        '中時新聞': "div.article-body img",
        'BBC News 中文': "div.bbc-1cvxiy9 img"
    }

    for source_name, url in sources_urls.items():
        if source_name not in ALLOWED_SOURCES:
            continue
            
        try:
            driver.get(url)
            selector = image_selectors.get(source_name)
            if not selector:  # 如果沒有對應的選擇器，跳過
                continue
            
            # 特別處理 BBC 新聞圖片
            if source_name == 'BBC News 中文':
                try:
                    content_div = driver.find_element(By.CSS_SELECTOR, 'div.bbc-1cvxiy9')
                    if content_div:
                        first_image = content_div.find_element(By.TAG_NAME, 'img')
                        if first_image and 'src' in first_image.get_attribute('outerHTML'):
                            results[source_name] = first_image.get_attribute('src')
                            continue
                except Exception as e:
                    print(f"無法找到 BBC 新聞圖片: {e}")  # 新增錯誤處理

            # 提取其他來源的圖片
            image_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # 提取圖片
            image_url = image_element.get_attribute('src') or image_element.get_attribute('data-src')
            results[source_name] = image_url or ''  # 改為空字串
            
        except Exception as e:
            print(f"圖片擷取錯誤: {e}")
            results[source_name] = ''  # 改為空字串
            
    return results


# 加載並摘要 CSV 資料
def load_and_summarize_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        if "內文" in data.columns:
            return data  # 成功讀取時返回資料
        else:
            raise ValueError("CSV 檔案中缺少必要的欄位：內文")  # 若缺少必要欄位則拋出錯誤
    except Exception as e:
        return str(e)  # 返回錯誤訊息

# X.AI 聊天功能
def chat_with_xai(prompt, api_key, model_name, context=""):
    max_retries = 3
    retry_delay = 2  # 初始延遲2秒
    
    for attempt in range(max_retries):
        try:
            url = 'https://api.x.ai/v1/chat/completions'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            messages = [
                {"role": "system", "content": "你是一個新聞分析助手。"},
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

def is_disaster_news(title, content):
    """
    使用 X.AI 判斷新聞是否主要報導自然災害事件
    """
    prompt = f"""
    請判斷以下新聞是否主要在報導自然災害事件本身，只需回答 true 或 false：
    
    允許的災害類型：大雨、豪雨、暴雨、淹水、洪水、水災、颱風、颶風、風災、地震、海嘯、乾旱、旱災、大火、野火

    新聞標題：{title}
    新聞內容：{content[:500]}

    判斷標準：
    1. 新聞必須主要描述災害事件本身，包括：
       - 災害的發生過程
       - 災害造成的直接影響和損失
       - 災害現場的情況描述
       
    2. 必須排除以下類型的新聞：
       - 災後援助或捐贈活動的報導
       - 國際救援行動的新聞
       - 災後重建相關報導
       - 防災政策討論
       - 氣候變遷議題
       - 歷史災害回顧
       - 以災害為背景但主要報導其他事件的新聞
       
    3. 特別注意：
       - 如果新聞主要在報導救援、捐助、外交等活動，即使提到災害也應該回答 false
       - 如果新聞只是用災害作為背景，主要報導其他事件，應該回答 false
       - 新聞的核心主題必須是災害事件本身才回答 true
    """
    
    response = chat_with_xai(prompt, xai_api_key, model_name, "")
    return 'true' in response.lower()

# 主程式
def main():
    start_time = time.time()
    day="3"
    # Google News 搜 URL
    urls = [
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%xA8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#地震
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際大火
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際野火
        #加上bbc關鍵字
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際大火
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'#新增國際野火
    ]
    
    all_news_items = []
    for url in urls:
        news_items = fetch_news(url)
        all_news_items.extend(news_items)

    if all_news_items:
        news_df = pd.DataFrame(all_news_items)
        news_df = news_df.drop_duplicates(subset='標題', keep='first')

        driver = setup_chrome_driver()

        output_file = 'w.csv'
        if os.path.exists(output_file):
            os.remove(output_file)

        # 新增欄位：摘要、地點、災害
        summaries = []
        locations = []
        disasters = []

        for index, item in news_df.iterrows():
            source_name = item['來源']
            original_url = item['連結']
            final_url = extract_final_url(original_url)
            sources_urls = {source_name: final_url}

            # 擷取內容和圖片
            content_results, summary_results = fetch_article_content(driver, sources_urls)
            image_results = extract_image_url(driver, sources_urls)

            content = content_results.get(source_name, '未找到內容')
            image_url = image_results.get(source_name, 'null')

            # 生成簡短的事件描述
            content_prompt = f"""
            請根據以下新聞內容，生成一段災害事件描述。描述應包含以下要素（如新聞中有提及）：

            1. 對於颱風事件：
               - 颱風編號和名稱
               - 目前位置和強度
               - 移動方向和速度
               - 預計影響範圍
               - 可能造成的影響（如降雨、強風等）

            2. 對於地震事件：
               - 發生地點
               - 地震規模和震源深度
               - 是否發布海嘯警報
               - 如果是群震，需說明發生頻率和最大震級
               - 災情和民眾反應

            3. 對於其他災害：
               - 災害類型和規模
               - 影響範圍
               - 災情描述
               - 人員傷亡或撤離情況
               - 救援或應對措施

            請確保資訊準確且前後連貫。
            不要加入新聞中未提及的推測性內容。

            範例格式：
            颱風：「第26號颱風帕布生成，預計朝中南半島方向移動，對台灣無直接影響，外圍水氣將導致全台降雨機率增加」
            地震：「萬那杜發生規模7.4的淺層地震，震源深度10公里，發布海嘯警報」
            群震：「銀川市在17小時內共發生9次地震，最大震級為2.6級。居民擔心更大地震來襲，部分人選擇在車內或空曠區域過夜」

            新聞內容：
            {content}
            """
            content_summary = chat_with_xai(content_prompt, xai_api_key, model_name, "").strip() or "無法生成事件描述"

            # 提問並取得摘要、地點與災害
            question_summary = f"""
            請根據以下新聞內容，生成一段事件摘要。摘要應包含以下要素（如新聞中有提及）：

            1. 對於地震事件：
            - 發生時間（含時區說明）
            - 具體地點（含國家/地區名）
            - 地震規模和震源深度
            - 發布單位（如地質調查所、氣象部門等）
            - 是否發布海嘯警報
            - 影響範圍和預警情況
            - 傷亡和損失情況（如有）

            2. 對於颱風事件：
            - 颱風編號、名稱和等級
            - 目前位置和強度
            - 移動方向和速度
            - 預計路徑
            - 各地警報發布情況
            - 可能帶來的影響（降雨量、風速等）
            - 防災應變措施

            3. 對於水災/洪災事件：
            - 發生時間和地點
            - 降雨量或洪水規模
            - 淹水範圍和深度
            - 受災情況（含人員傷亡、財產損失）
            - 救援行動和疏散情況
            - 相關單位應變措施

            4. 對於其他災害事件：
            - 災害類型和規模
            - 發生時間和地點
            - 影響範圍
            - 傷亡和損失統計
            - 救援行動進展
            - 相關單位回應

            摘要格式要求：
            1. 使用完整句子描述
            2. 按時間順序陳述
            3. 確保資訊準確性
            4. 重要數據需包含單位
            5. 避免主觀評論

            範例格式：
            地震：「台灣時間12月17日上午9點47分，太平洋島國萬那杜發生規模7.4強震，震源深度僅10公里，可能引發海嘯。氣象署與太平洋海嘯警報中心已發布警報，提醒可能面臨海嘯威脅。」
            颱風：「第16號颱風小犬持續增強，中心位置在台灣東南方海面，以每小時15公里速度向西北移動。預計48小時內暴風圈可能籠罩台灣東部海域，氣象局已發布海上颱風警報。」
            {content}
            """
            
            question_location = f"""
            請根據以下新聞內容提取所有相關地點：

            檢核標準：
            - 地點是否完整（不遺漏任何提到的地點）
            - 格式是否一致（每個字串一個地點）
            - 描述是否準確（地理位置準確性）
            - 層級是否合適（行政區劃準確性）

            範例格式：
            颱風新聞：["南沙島海面", "中南半島", "台灣"]
            地震新聞：["日本福島縣", "宮城縣", "東京都"]
            水災新聞：["泰國曼谷", "大城府", "巴吞他尼府"]

            {content}
            """
            question_disaster = f"""
            請從以下新聞內容中提取主要的災害類型，只需列出災害名稱，限制在10個字以內。
            如果有多個災害，只列出最主要或最嚴重的災害。
            相同類型的災害只需列出一次。

            範例格式：
            地震
            颱風
            洪水
            土石流

            新聞內容：
            {content}
            """

            summary_answer = chat_with_xai(question_summary, xai_api_key, model_name, content)
            location_answer = chat_with_xai(question_location, xai_api_key, model_name, content)
            disaster_answer = chat_with_xai(question_disaster, xai_api_key, model_name, content)

            # 使用災害新聞判斷
            is_disaster = is_disaster_news(item['標題'], content)

            if not is_disaster:
                print(f"非災害相關新聞，跳過: {item['標題']}")
                continue

            # 根據地點判斷是否為國內新聞
            is_domestic = any(keyword in location_answer for keyword in domestic_keywords)
            region = '國內' if is_domestic else '國外'

            if content != '未找到內容':
                csv_summary = content

                # 收集結果
                summaries.append(summary_answer)
                locations.append(location_answer)
                disasters.append(disaster_answer)

                result = {
                    '標題': item['標題'],
                    '連結': original_url,
                    '內文': content_summary,  # 使用新生成的簡短描述
                    '來源': source_name,
                    '時間': item['時間'],
                    '圖片': image_url,
                    '地區': region,
                    '摘要': summary_answer,
                    '地點': location_answer,
                    '災害': disaster_answer
                }

                # 儲存資料到 CSV
                output_df = pd.DataFrame([result])
                output_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False, encoding='utf-8')

                print(f"標題: {result['標題']}")
                print(f"連結: {result['連結']}")
                print(f"內文: {result['內文'][:50]}...")
                print(f"來源: {result['來源']}")
                print(f"時間: {result['時間']}")
                print(f"圖片: {result['圖片']}")
                print(f"地區: {result['地區']}")
                print(f"摘要: {result['摘要']}")
                print(f"地點: {result['地點']}")
                print(f"災害: {result['災害']}")
                print('-' * 80)

        driver.quit()

        # 儲存資料到 SQLite
        db_name = 'w.db'
        table_name = 'news'

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,                  -- 事件名稱
            image TEXT,                  -- 事件圖片URL
            link TEXT,                   -- 相關新聞連結
            content TEXT,                -- 新聞內容
            source TEXT,                 -- 新聞來源
            date DATE,                   -- 事件日期
            recent_update DATE,          -- 最新更新日期
            region TEXT,                 -- 地理範圍
            location TEXT,               -- 地點
            disaster TEXT,               -- 災害類型
            summary TEXT,                -- 事件摘要
            daily_records TEXT,          -- 每日進展記錄 (JSON)
            links TEXT                   -- 新聞連結資料 (JSON)
        )
        ''')

        cursor.execute(f'DELETE FROM {table_name}')
        conn.commit()

        w_df = pd.read_csv('w.csv')
        w_df['時間'] = pd.to_datetime(w_df['時間'], format='%Y-%m-%d', errors='coerce')
        w_df = w_df.sort_values(by='時間', ascending=False)

        for _, row in w_df.iterrows():
            cursor.execute(f'''
            SELECT COUNT(*) FROM {table_name} WHERE event = ? AND link = ?
            ''', (row['標題'], row['連結']))
            exists = cursor.fetchone()[0]
            print(f"Checking existence for: {row['標題']} - {row['連結']}, Exists: {exists}")

            if exists == 0:
                cursor.execute(f'''
                INSERT INTO {table_name} (
                    event, image, link, content, source, date, recent_update,
                    region, location, disaster, summary, daily_records, links
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['標題'],                # event
                    row['圖片'],                # image
                    row['連結'],                # link
                    row['內文'],                # content
                    row['來源'],                # source
                    row['時間'].strftime('%Y-%m-%d'),  # date
                    row['時間'].strftime('%Y-%m-%d'),  # recent_update (使用相同日期)
                    row['地區'],                # region
                    row['地點'],                # location
                    row['災害'],                # disaster
                    row['摘要'],                # summary
                    json.dumps([]),             # daily_records (空陣列)
                    json.dumps([row['連結']])   # links (包含原始連結)
                ))
                print(f"Inserted: {row['標題']}")

        conn.commit()
        conn.close()

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

        print(f'爬取新聞並儲存資料共耗時 {time_str}')
        print('新聞更新已完成！')
        print('爬取後的內容已成功儲存到 CSV 和 SQLite 資料庫中')

if __name__ == "__main__":
    main()


def fetch_news_data():
    db_name = 'w.db'
    table_name = 'news'

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f'SELECT id, title, link, content, source, date, image, region, summary, location, disaster FROM {table_name}')    
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
            'image': row[6],
            'region': row[7],
            "summary": row[8].replace("\n", " ").replace("-", "").strip(),
            "location": row[9].replace("\n", " ").replace("-", "").strip(),
            "disaster": row[10].replace("\n", " ").replace("-", "").strip()
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
    query = request.GET.get('search', '')

    conn = sqlite3.connect('w.db')
    cursor = conn.cursor()

    if query:
        cursor.execute("SELECT * FROM news WHERE event LIKE ?", ('%' + query + '%',))
    else:
        cursor.execute("SELECT * FROM news")

    news_data = cursor.fetchall()
    conn.close()

    news_list = []
    for row in news_data:
        # 安全地處理可能為 None 的值
        def safe_process(value):
            return value.replace("\n", " ").replace("-", "").strip() if value else ""

        news_list.append({
            'id': row[0],
            'event': safe_process(row[1]),
            'image': row[2] or "",
            'link': row[3] or "",
            'content': safe_process(row[4])[:50] + '...' if row[4] and len(row[4]) > 50 else safe_process(row[4]),
            'source': row[5] or "",
            'date': row[6] or "",
            'region': row[8] or "未知",
            'summary': safe_process(row[11]),
            'location': safe_process(row[9]),
            'disaster': safe_process(row[10])
        })

    return render(request, 'news.html', {'news_list': news_list})


# RESTful API 查詢所有新聞資料並以JSON格式返回
def news_list(request):
    if request.method == 'GET':
        # 查詢所有新聞記錄，並返回標題、連結、內容、來源和日期
        news = News.objects.all().values('title', 'link', 'content', 'source', 'date', 'image', 'region', 'summary', 'location', 'disaster')        
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
            image=data.get('image', 'null'),
            region=data.get('region', '未知'),
            summary=data.get('summary', ''),  # 新增 summary 欄位，預設值為空字串
            location=data.get('location', ''),  # 新增 location 欄位，預設值為空字串
            disaster=data.get('disaster', '')  # 新增 disaster 欄位，預設值為空字串
        )
        return JsonResponse({"message": "News created", "news_id": news.id}, status=201)
    
from django.views.decorators.http import require_GET

@require_GET
def news_api(request):
    try:
        conn = sqlite3.connect('w.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, event, image, link, content, source, date, 
                   recent_update, region, location, disaster, 
                   summary, daily_records, links 
            FROM news
            ORDER BY date DESC
        """)
        news_data = cursor.fetchall()
        
        def format_event_title(location, content, title):
            """格式化事件標題，根據不同災害類型生成對應格式"""
            prompt = f"""
            請從以下資訊中提取關鍵資訊，並根據災害類型生成對應格式的事件名稱。
            不要加任何空格、標點符號或換行符號。
            
            對於不同類型的災害，請遵循以下格式規則：

            1. 颱風事件：
               格式：「地理位置+颱風名稱+狀態」
               例如：南沙島海域颱風帕布生成
               例如：菲律賓海面颱風蘇拉增強
               
            2. 地震事件：
               A. 單次地震：
                  格式：「地點+震級+地震」
                  例如：萬那杜7.4級地震
                  例如：阿富汗6.3級地震
                  
               B. 頻發地震：
                  格式：「地點+地震頻發」
                  例如：中國寧夏銀川地震頻發
                  例如：土耳其敘利亞地震頻發
                  
            3. 水災/洪水事件：
               格式：「國家地區+災情描述」
               例如：利比亞東部特大洪災
               例如：希臘中部嚴重水患
               
            4. 火災事件：
               格式：「地點+火災規模描述」
               例如：夏威夷毛伊島大規模野火
               例如：加拿大林區森林大火
               
            5. 其他災害：
               格式：「地點+災害類型+嚴重程度」
               例如：日本福島核污水排放
               例如：西非尼日爾嚴重乾旱

            請根據以下資訊生成事件名稱：
            地點：{location}
            內容：{content}
            標題：{title}
            """
            
            response = chat_with_xai(prompt, xai_api_key, model_name, "")
            return response.strip()

        def is_same_event(event1, event2, date1, date2, location1, location2):
            """判斷是否為同一事件"""
            prompt = f"""
            請判斷以下兩則新聞是否報導同一個災害事件，只需回答 true 或 false：

            新聞1：
            事件：{event1}
            日期：{date1}
            地點：{location1}

            新聞2：
            事件：{event2}
            日期：{date2}
            地點：{location2}

            判斷標準（必須同時符合以下三項條件）：
            1. 時間範圍一致：
               - 地震事件：同一國家2天內的地震視為同一事件（含餘震）
               - 其他災害：同一地區2天內的相同災害視為同一事件

            2. 地理範圍重疊：
               - 必須是同一國家或相鄰區域
               - 地震事件：同一國家的「近海」、「外海」、「城市名」均視為重疊區域
               - 水災/颱風：影響範圍重疊或相連的區域視為同一事件
               - 野火/森林大火：相連的受災區域視為同一事件

            3. 災害類型與核心描述一致：
               - 災害類型必須相同（如同為地震、同為洪水等）
               - 核心描述要一致（如災害規模、影響程度的描述）
               - 地震事件：不同規模的報導可能是後續修正，仍視為同一事件
               - 水災：「淹水」、「洪水」、「水災」視為相同類型
               - 火災：「野火」、「森林大火」、「大火」視為相同類型

            特別注意：
            - 三個條件必須同時滿足才能判定為同一事件
            - 如果任何一個條件不符合，就不能視為同一事件
            - 即使地點描述方式不同，只要確實指涉同一區域就視為符合地理條件
            - 災害規模的差異若是來自不同機構的測量或後續修正，仍可視為同一事件

            請根據以上標準判斷，必須同時符合三項條件才回答 true，否則回答 false。
            """

            response = chat_with_xai(prompt, xai_api_key, model_name, "")
            return 'true' in response.lower()

        def safe_process(value):
            return value.replace("\n", " ").replace("-", "").strip() if value else ""

        def parse_location(location_str):
            """使用 X.AI 處理地點字符串，只保留有效地名，並添加國家名稱"""
            if not location_str:
                return []
            
            try:
                # 如果是 JSON 字符串，先嘗試解析
                if isinstance(location_str, str):
                    try:
                        location_list = json.loads(location_str)
                        if isinstance(location_list, list):
                            location_str = ' '.join(location_list)
                    except json.JSONDecodeError:
                        pass

                # 使用 X.AI 清理和提取地點，並添加國家名稱
                clean_location_prompt = f"""
                請從以下文字中提取所有地點，並以 JSON 數組格式返回。
                
                要求：
                1. 必須包含國家名稱
                2. 如果提到台灣的地點（如台北市、新北市等），則在數組開頭加上"台灣"
                3. 如果是國外地點，確保每個地點都有對應的國家名稱
                4. 如果同一個國家有多個地點，國家名稱只需出現一次
                5. 移除所有說明文字、標點符號和格式標記
                
                範例格式：
                台灣地點：["台灣", "台北市", "新北市", "基隆市"]
                日本地點：["日本", "東京都", "大阪府", "福島縣"]
                多國地點：["日本", "東京都", "大阪府", "韓國", "首爾市", "釜山市"]
                
                輸入文字：
                {location_str}
                """
                
                # 獲取 X.AI 的回應並清理
                response = chat_with_xai(clean_location_prompt, xai_api_key, model_name, "").strip()
                
                # 清理回應中的 ```json 和 ``` 標記
                response = response.replace('```json', '').replace('```', '').strip()
                
                try:
                    # 嘗試解析 JSON 回應
                    cleaned_locations = json.loads(response)
                    if isinstance(cleaned_locations, list):
                        # 確保所有項目都是字符串，並移除空項目
                        cleaned_locations = [str(loc).strip() for loc in cleaned_locations if str(loc).strip()]
                        # 移除重複項並排序，但保持國家名稱在前
                        return sorted(list(dict.fromkeys(cleaned_locations)), 
                                   key=lambda x: (x not in ['台灣', '日本', '韓國', '中國', '美國'], x))
                except json.JSONDecodeError as e:
                    print(f"JSON 解析錯誤，嘗試其他方式處理: {str(e)}")
                    # 如果 JSON 解析失敗，嘗試直接處理文字
                    locations = response.replace('[', '').replace(']', '').replace('"', '').split(',')
                    cleaned_locations = [loc.strip() for loc in locations if loc.strip()]
                    return sorted(list(dict.fromkeys(cleaned_locations)),
                                key=lambda x: (x not in ['台灣', '日本', '韓國', '中國', '美國'], x))
                
            except Exception as e:
                print(f"解析地點時發生錯誤: {str(e)}")
                return []

        merged_news = {}
        processed_events = set()

        for row in news_data:
            # 先判斷是否為純災害新聞
            if not is_disaster_news(row[1], row[4] or ""):
                continue

            if row[1] in processed_events:
                continue

            location = parse_location(row[9])
            
            # 處理 cover 欄位
            cover = "null"
            if row[2] and isinstance(row[2], str) and row[2].strip():
                cover = row[2]
            
            formatted_event = format_event_title(
                ','.join(location), 
                safe_process(row[4] or ""),
                row[1]
            )

            # 尋找相關事件
            event_key = None
            for existing_key in merged_news.keys():
                if is_same_event(
                    formatted_event,
                    merged_news[existing_key]["event"],
                    row[6] or row[7] or "",
                    merged_news[existing_key]["date"],
                    ', '.join(location),
                    ', '.join(merged_news[existing_key]["location"])
                ):
                    event_key = existing_key
                    break

            news_item = {
                "source": {
                    "publisher": row[5] or "",  # 發布媒體
                    "author": row[5] or ""      # 作者（與發布媒體相同）
                },
                "url": row[3] or "",
                "title": row[1],
                "publish_date": row[6] or "",
                "location": location,
                "summary": safe_process(row[11] or "")
            }

# 檢查是否為新事件
        is_new_event = event_key is None

        # 如果是新事件，生成新 key 和基礎結構
        if is_new_event:
            event_key = f"{formatted_event}_{len(merged_news)}"
            merged_news[event_key] = {
                "event": formatted_event,
                "region": '國內' if any(keyword in ','.join(location) for keyword in domestic_keywords) else '國外',
                "cover": cover,
                "date": row[6] or "",
                "recent_update": row[7] or row[6] or "",
                "location": [],
                "overview": "",  # 只在事件層級保留 overview
                "daily_records": [],
                "links": []  # links 中會包含每篇新聞的 summary
            }

        # 合併 location，確保不重複且排序
        merged_news[event_key]["location"] = sorted(set(merged_news[event_key]["location"]).union(location))

        # 添加新聞連結
        merged_news[event_key]["links"].append(news_item)

        # 更新 recent_update 和 daily_records
        current_date = row[7] or row[6] or ""
        if current_date > merged_news[event_key]["recent_update"]:
            merged_news[event_key]["recent_update"] = current_date

        # 生成每日記錄的內容
        daily_record_prompt = f"""
        請根據以下新聞內容生成一段簡短的災情記錄，描述當天的主要災情發展。
        內容應包含：災害類型、影響範圍、傷亡或損失情況（如有）。
        請用精簡的方式描述，限制在100字以內。

        新聞內容：
        {safe_process(row[4] or "")}
        """
        
        daily_content = chat_with_xai(daily_record_prompt, xai_api_key, model_name, "").strip()
        
        # 清理格式
        daily_content = daily_content.replace('\n', ' ')
        daily_content = daily_content.replace('- ', '')
        daily_content = daily_content.replace('*', '')
        daily_content = ' '.join(daily_content.split())
        
        # 添加新的每日記錄
        daily_record = {
            "date": current_date,
            "content": daily_content,
            "location": location
        }
        
        # 檢查是否已存在相同日期的記錄
        existing_record = None
        for record in merged_news[event_key]["daily_records"]:
            if record["date"] == current_date:
                existing_record = record
                break
        
        if existing_record:
            # 更新現有記錄
            existing_record["content"] = daily_content
            existing_record["location"] = location
        else:
            # 添加新記錄
            merged_news[event_key]["daily_records"].append(daily_record)
        
        # 按日期排序 daily_records
        merged_news[event_key]["daily_records"].sort(key=lambda x: x["date"], reverse=True)

        # 更新封面圖片
        if cover != "null" and merged_news[event_key]["cover"] == "null":
            merged_news[event_key]["cover"] = cover

        # 更新事件概述（整合所有相關新聞的內容）
        overview_prompt = f"""
        請整合以下所有相關新聞的內容，生成一個完整的事件概述。請用完整的段落描述，不要使用任何符號標記（如-、*等）。
        
        概述內容應包含：
        1. 事件的整體發展過程
        2. 主要影響和損失情況
        3. 各方回應和應對措施
        4. 後續發展和影響評估

        請以流暢的文字敘述呈現，避免使用項目符號，直接以完整句子描述。
        確保各個面向的資訊能自然地串連在一起，形成連貫的敘事。

        現有概述：{merged_news[event_key]["overview"]}
        新的新聞內容：{safe_process(row[4] or "")}
        所有相關新聞摘要：{[link.get('summary', '') for link in merged_news[event_key]["links"]]}
        """

        # 取得 overview 回應並清理格式
        overview_response = chat_with_xai(overview_prompt, xai_api_key, model_name, "").strip()
        # 清理可能的符號和格式
        overview_response = overview_response.replace('\n- ', ' ')
        overview_response = overview_response.replace('- ', '')
        overview_response = overview_response.replace('\n*', ' ')
        overview_response = overview_response.replace('*', '')
        overview_response = overview_response.replace('\n1.', ' ')
        overview_response = overview_response.replace('\n2.', ' ')
        overview_response = overview_response.replace('\n3.', ' ')
        overview_response = overview_response.replace('\n4.', ' ')
        overview_response = ' '.join(overview_response.split())  # 移除多餘的空格和換行
        
        merged_news[event_key]["overview"] = overview_response

        # 為新的新聞生成摘要並添加到 links 中
        summary_prompt = f"""
        請針對這篇新聞生成簡短摘要，只需摘要這篇新聞的重點：
        {safe_process(row[4] or "")}
        """
        current_summary = chat_with_xai(summary_prompt, xai_api_key, model_name, "").strip()

        # 檢查是否已存在相同標題和來源的新聞
        existing_news = None
        for link in merged_news[event_key]["links"]:
            if (link["title"] == row[1] and 
                link["source"]["publisher"] == row[5]):
                existing_news = link
                break

        # 只有在不存在相同新聞時才添加
        if not existing_news:
            # 添加新聞連結和其摘要到 links 中
            news_item = {
                "source": {
                    "publisher": row[5] or "",  # 發布媒體
                    "author": row[5] or ""      # 作者（與發布媒體相同）
                },
                "url": row[3] or "",
                "title": row[1],
                "publish_date": row[6] or "",
                "location": location,
                "summary": current_summary  # 每篇新聞的個別摘要
            }
            merged_news[event_key]["links"].append(news_item)

        # 標記該事件已處理
        processed_events.add(row[1])

        news_list = list(merged_news.values())
        news_list.sort(key=lambda x: x["recent_update"], reverse=True)

        # 在處理完資料後，將結果存入新的資料表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_cache (
            prompt TEXT PRIMARY KEY,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 清空舊資料
        cursor.execute('DELETE FROM processed_news')
        
        # 儲存處理後的資料
        for news_item in news_list:
            cursor.execute('''
            INSERT INTO processed_news (
                event, region, cover, date, recent_update,
                location, overview, daily_records, links
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_item['event'],
                news_item['region'],
                news_item['cover'],
                news_item['date'],
                news_item['recent_update'],
                json.dumps(news_item['location'], ensure_ascii=False),
                news_item['overview'],
                json.dumps(news_item['daily_records'], ensure_ascii=False),
                json.dumps(news_item['links'], ensure_ascii=False)
            ))

        # 確保所有更改都已提交
        conn.commit()
        
        # 在返回結果之前關閉連接
        conn.close()

        return JsonResponse(news_list, safe=False)
    except Exception as e:
        # 確保在發生錯誤時也關閉連接
        if 'conn' in locals():
            conn.close()
        return JsonResponse({'error': str(e)}, status=500)
    
@require_GET
def news_api_sql(request):
    """直接從 processed_news 資料表讀取已經整理好的資料"""
    try:
        conn = sqlite3.connect('w.db')
        cursor = conn.cursor()
        
        # 檢查資料表是否存在
        cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='processed_news'
        ''')
        
        if not cursor.fetchone():
            return JsonResponse({'error': '資料尚未處理完成'}, status=404)

        # 直接從 processed_news 讀取資料
        cursor.execute('''
        SELECT 
            event, region, cover, date, recent_update,
            location, overview, daily_records, links
        FROM processed_news
        ORDER BY recent_update DESC
        ''')
        
        rows = cursor.fetchall()
        
        news_list = []
        for row in rows:
            try:
                location = json.loads(row[5]) if row[5] else []
                daily_records = json.loads(row[7]) if row[7] else []
                links = json.loads(row[8]) if row[8] else []
                
                news_item = {
                    "event": row[0],
                    "region": row[1],
                    "cover": row[2],
                    "date": row[3],
                    "recent_update": row[4],
                    "location": location,
                    "overview": row[6],
                    "daily_records": daily_records,
                    "links": links
                }
                news_list.append(news_item)
            except json.JSONDecodeError as e:
                print(f"JSON 解析錯誤: {str(e)}")
                continue

        conn.close()
        return JsonResponse(news_list, safe=False)
    
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return JsonResponse({'error': str(e)}, status=500)
    
# 新增更新每日記錄的函數
@csrf_exempt
def update_daily_records(request, news_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            conn = sqlite3.connect('w.db')
            cursor = conn.cursor()
            
            # 獲取現有記錄
            cursor.execute("SELECT daily_records FROM news WHERE id = ?", (news_id,))
            result = cursor.fetchone()
            
            if result:
                current_records = json.loads(result[0]) if result[0] else []
                # 添加新記錄
                current_records.append({
                    "date": data.get("date"),
                    "content": data.get("content"),
                    "location": data.get("location", [])
                })
                
                # 更新資料庫
                cursor.execute(
                    "UPDATE news SET daily_records = ?, recent_update = ? WHERE id = ?",
                    (json.dumps(current_records), data.get("date"), news_id)
                )
                conn.commit()
                conn.close()
                
                return JsonResponse({"message": "Daily record updated successfully"})
            else:
                return JsonResponse({"error": "News not found"}, status=404)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)


#測試爬蟲：開始爬蟲url http://localhost:8000/api/crawler/first-stage/
#測試爬蟲：開啟後端api http://localhost:8000/api/raw-news/    
@require_GET
def crawler_first_stage(request):
    try:
        start_time = time.time()
        day = "30"
        
        # Google News 搜尋 URL
        urls = [
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%xA8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#地震
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際野火           
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'#新增國際野火        
            ]
        
        all_news_items = []
        start_crawl_time = time.time()
        for url in urls:
            news_items = fetch_news(url)
            all_news_items.extend(news_items)
        
        if all_news_items:
            news_df = pd.DataFrame(all_news_items)
            news_df = news_df.drop_duplicates(subset='標題', keep='first')
            
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

            driver = setup_chrome_driver()

            # 刪除舊的 CSV 檔案（如果存在）
            first_stage_file = 'w2.csv'
            if os.path.exists(first_stage_file):
                os.remove(first_stage_file)

            for index, item in news_df.iterrows():
                source_name = item['來源']
                original_url = item['連結']
                final_url = extract_final_url(original_url)
                sources_urls = {source_name: final_url}

                # 擷取內容和圖片
                content_results, _ = fetch_article_content(driver, sources_urls)
                image_results = extract_image_url(driver, sources_urls)

                content = content_results.get(source_name, '')  # 確保空值為空字串
                image_url = image_results.get(source_name, '')  # 確保空值為空字串

                # 準備要存入 CSV 的資料
                result = {
                    '標題': item['標題'],
                    '連結': original_url,
                    '內文': content or '',  # 確保空值為空字串
                    '來源': source_name,
                    '時間': item['時間'],
                    '圖片': image_url or ''  # 確保空值為空字串
                }

                # 儲存資料到 CSV
                output_df = pd.DataFrame([result])
                output_df.to_csv(first_stage_file, mode='a', header=not os.path.exists(first_stage_file), 
                               index=False, encoding='utf-8')

                print(f"已儲存新聞: {result['標題']}")

            driver.quit()

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

            return JsonResponse({
                'status': 'success',
                'message': f'第一階段爬蟲完成！耗時：{time_str}',
                'csv_file': first_stage_file,
                'total_news': len(news_df)
            })

        return JsonResponse({
            'status': 'error',
            'message': '沒有找到新聞'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'爬蟲執行失敗：{str(e)}'
        }, status=500)

    
@require_GET
def view_raw_news(request):
    try:
        # 定義 CSV 檔案名稱
        csv_file = 'w2.csv'
        
        # 檢查 CSV 檔案是否存在
        if not os.path.exists(csv_file):
            return JsonResponse({'error': 'CSV 檔案不存在'}, status=404)

        # 從 CSV 檔案讀取資料
        news_df = pd.read_csv(csv_file)

        # 準備 JSON 格式的新聞列表
        news_list = []
        for _, row in news_df.iterrows():
            # 限制內文長度為 100 字
            content = row.get('內文', '') or ''
            if len(content) > 100:
                content = content[:100] + '...'

            news_item = {
                '來源': row.get('來源', '') or '',  # 確保空值為空字串
                '作者': row.get('來源', '') or '',  # 假設作者與來源相同
                '標題': row.get('標題', '') or '',
                '連結': row.get('連結', '') or '',
                '內文': content,  # 限制後的內文
                '時間': row.get('時間', '') or '',
                '圖片': row.get('圖片', '') or ''
            }
            news_list.append(news_item)

        # 使用 json_dumps_params 進行美化
        return JsonResponse(news_list, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})
        
    except Exception as e:
        print(f"Error in view_raw_news: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)