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

def fetch_news(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 使用多個可能的 class 名稱來找到文章區塊
        articles = soup.find_all(['article', 'div'], class_=['IFHyqb', 'xrnccd', 'IBr9hb', 'NiLAwe'])
        print(f"找到 {len(articles)} 個文章區塊")

        news_list = []
        for article in articles:
            try:
                # 尋找標題和連結（增加更多可能的 class）
                title_element = article.find(['a', 'h3', 'h4'], class_=['JtKRv', 'ipQwMb', 'DY5T1d', 'gPFEn'])
                if not title_element:
                    title_element = article.find('a', recursive=True)  # 遞迴搜尋所有 a 標籤
                
                if not title_element:
                    continue

                title = title_element.get_text(strip=True)
                link = title_element.get('href', '')

                # 處理 Google News 的相對 URL
                if link.startswith('./'):
                    link = 'https://news.google.com/' + link[2:]
                elif link.startswith('/'):
                    link = 'https://news.google.com' + link

                # 尋找新聞來源（增加更多可能的 class 和搜尋方式）
                source_element = article.find(['div', 'a'], class_=['vr1PYe', 'wEwyrc', 'SVJrMe', 'NmQAAc'])
                if not source_element:
                    # 嘗試找到包含 "BBC" 的元素
                    source_element = article.find(lambda tag: tag.name in ['div', 'a'] and 'BBC' in tag.get_text())

                if not source_element:
                    continue

                source_name = source_element.get_text(strip=True)
                
                # 特別處理 BBC 來源名稱
                if 'BBC' in source_name:
                    source_name = 'BBC News 中文'

                # 檢查是否為允許的來源
                if source_name not in ALLOWED_SOURCES:
                    continue

                # 尋找時間（增加更多可能的 class）
                time_element = article.find(['time', 'div'], class_=['UOVeFe', 'hvbAAd', 'WW6dff', 'LfVVr'])
                date_str = time_element.get_text(strip=True) if time_element else '未知'
                date = parse_date(date_str)

                news_item = {
                    '標題': title,
                    '連結': link,
                    '來源': source_name,
                    '時間': date
                }

                print(f"\n找到新聞:")
                print(f"標題: {title}")
                print(f"來源: {source_name}")
                print(f"連結: {link}")
                print(f"時間: {date}")

                news_list.append(news_item)

            except Exception as e:
                print(f"處理文章時發生錯誤: {str(e)}")
                continue

        return news_list

    except Exception as e:
        print(f"抓取新聞時發生錯誤: {str(e)}")
        return []
    
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
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_final_url(google_news_url):
    match = re.search(r'(https?://[^&]+)', google_news_url)
    if match:
        return match.group(1)
    return google_news_url

def fetch_article_content(driver, sources_urls):
    results = {}
    summaries = {}
    for source_name, url in sources_urls.items():
        if source_name not in ALLOWED_SOURCES:
            continue
            
        try:
            driver.get(url)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p'))
            )
            
            # 更新選擇器以包含 BBC
            content_selectors = {
                'Newtalk新聞': 'div.articleBody.clearfix p',
                '經濟日報': 'section.article-body__editor p',
                '自由時報': 'div.text p',
                '中時新聞': 'div.article-body p',
                'BBC News 中文': 'div.bbc-1cvxiy9 p'
            }
            
            selector = content_selectors.get(source_name)
            if not selector:  # 如果沒有對應的選擇器，跳過
                continue
                
            # 特別處理 BBC 新聞
            if source_name == 'BBC News 中文':
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    content_div = soup.find('div', class_='bbc-1cvxiy9')
                    if content_div:
                        paragraphs = content_div.find_all('p')
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
                        summary = content[:100] if content else '未找到內容'
                        results[source_name] = content if content else '未找到內容'
                        summaries[source_name] = summary
                        continue
            
            # 其他報社的原有處理邏輯
            paragraphs = driver.find_elements(By.CSS_SELECTOR, selector)
            content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
            
            summary = content[:100] if content else '未找到內容'
            
            results[source_name] = content if content else '未找到內容'
            summaries[source_name] = summary
            
        except Exception as e:
            print(f"抓取內容失敗: {e}")
            results[source_name] = '錯誤'
            summaries[source_name] = '錯誤'
            
    return results, summaries

def extract_image_url(driver, sources_urls):
    results = {}
    for source_name, url in sources_urls.items():
        if source_name not in ALLOWED_SOURCES:
            continue
            
        try:
            driver.get(url)
            # 更新圖片選擇器以包含 BBC
            image_selectors = {
                'Newtalk新聞': "div.news_img img",
                '經濟日報': "section.article-body__editor img",
                '自由時報': "div.image-popup-vertical-fit img",
                '中時新聞': "div.article-body img",
                'BBC News 中文': "div.bbc-1cvxiy9 img"
            }
            
            # 特別處理 BBC 新聞圖片
            if source_name == 'BBC News 中文':
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    content_div = soup.find('div', class_='bbc-1cvxiy9')
                    if content_div:
                        first_image = content_div.find('img')
                        if first_image and 'src' in first_image.attrs:
                            results[source_name] = first_image['src']
                            continue
            
            selector = image_selectors.get(source_name)
            if not selector:  # 如果沒有對應的選擇器，跳過
                continue
                
            try:
                image_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                image_url = image_element.get_attribute('src') or image_element.get_attribute('data-src')
                results[source_name] = image_url or 'null'
            except Exception as e:
                print(f"圖片擷取失敗: {e}")
                results[source_name] = 'null'
                
        except Exception as e:
            print(f"圖片擷取錯誤: {e}")
            results[source_name] = 'null'
            
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
    try:
        url = 'https://api.x.ai/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        messages = [
            {"role": "system", "content": "你是一個新聞分析助手，專門判斷新聞是否屬於同一事件。"},
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
        
        print(f"API 調用失敗 (狀態碼: {response.status_code})")
        return ""  # 返回空字符串而不是 None

    except Exception as e:
        print(f"API 錯誤: {str(e)}")
        return ""  # 返回空字符串而不是 None

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
    day="30"
    # Google News 搜 URL
    urls = [
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%xA8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際大火
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際野火
        #加上bbc關鍵字
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際大火
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'#新增國際野火
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
            請根據以下新聞內容，生成一個簡短的事件描述，格式為「地點+災害類型+規模」。
            例如：「北加州近海7.0地震」、「台灣花蓮6.0地震」、「日本東京暴雨300毫米」。
            請確保描述簡潔且包含關鍵資訊。

            新聞內容：
            {content}
            """
            content_summary = chat_with_xai(content_prompt, xai_api_key, model_name, "").strip() or "無法生成事件描述"

            # 提問並取得摘要、地點與災害
            question_summary = f"""
            請從以下新聞內容中提取災害相關資訊，並以下列格式回覆。
            只列出確實提到的資訊，未提及的項目請勿顯示。
            所有數字前必須加上項目名稱，各項目用逗號分隔。

            必要項目（若有資訊）：
            1. 災害種類（例如：地震、颱風、洪水等）
            2. 災害規模（例如：地震規模、雨量、風速等）
            3. 影響範圍（例如：面積、區域範圍等）
            4. 傷亡統計（死亡、受傷、失蹤、撤離人數等）
            5. 災情描述（建物損毀、交通中斷等）
            6. 時間：{item['時間']}（若新聞中有更精確時間則使用新聞時間）

            範例格式：
            災害種類：地震，地震規模：7.4級，震源深度：10公里，死亡人數：3人，受傷人數：12人，
            建物倒塌：13棟，影響範圍：20公里，發生時間：2024-03-20

            新聞內容：
            {content}
            """
            question_location = f"""
            請從以下新聞內容中提取災害發生的地點資訊，格式為「國家+地區」，限制在10個字以內。
            如果內容提到多個地點，請選擇主要災害發生地點。
            如果只提到國家沒提到地區，則只回覆國家名。

            範例格式：
            日本東京
            美國加州
            智利聖地亞哥

            新聞內容：
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
            """格式化事件標題為：國家主要城市主要災害類型"""
            prompt = f"""
            請從以下資訊中提取一個主要的國家、一個主要城市和災害類型，
            並以「國家主要城市主要災害類型」的格式回傳。
            不要加任何空格、標點符號或換行符號。
            如果有多個城市，只需選擇最主要或最先提到的城市。

            地點：{location}
            內容：{content}
            標題：{title}

            範例格式：
            日本東京地震
            美國加州洪水
            台灣高雄豪雨
            中國浙江颱風
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
               - 火災：「野火」、「森林大火」視為相同類型

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
            """處理地點字符串，移除特殊字符並用空格分隔"""
            if not location_str:
                return []
            
            # 如果是列表或字典，轉換為字符串
            if isinstance(location_str, (list, dict)):
                location_str = json.dumps(location_str, ensure_ascii=False)
            
            # 移除特殊字符和格式
            location_str = location_str.replace('\n', ' ')  # 換行替換為空格
            location_str = location_str.replace('- ', '')   # 移除列表符號
            location_str = location_str.replace('，', ',')  # 統一逗號格式
            
            # 分割並清理每個地點
            locations = []
            for loc in location_str.split(','):
                # 清理並添加非空的地點
                cleaned_loc = loc.strip()
                if cleaned_loc:
                    locations.append(cleaned_loc)
            
            # 移除重複項返回
            return list(dict.fromkeys(locations))

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
                "source": row[5] or "",
                "url": row[3] or "",
                "title": row[1],  # 保留原始標題
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
                "overview": "",
                "summary": "",
                "daily_records": [],
                "links": []
            }

        # 合併 location，確保不重複且排序
        merged_news[event_key]["location"] = sorted(set(merged_news[event_key]["location"]).union(location))

        # 添加新聞連結
        merged_news[event_key]["links"].append(news_item)

        # 更新 recent_update 和 daily_records
        current_date = row[7] or row[6] or ""
        if current_date > merged_news[event_key]["recent_update"]:
            merged_news[event_key]["recent_update"] = current_date
            merged_news[event_key]["daily_records"].append({
                "date": current_date,
                "content": safe_process(row[11] or ""),
                "location": location
            })

        # 更新封面圖片
        if cover != "null" and merged_news[event_key]["cover"] == "null":
            merged_news[event_key]["cover"] = cover

        # 更新概述或生成初始概述
        overview_prompt = f"""
        請整合以下新的資訊到現有的概述中（如果是新事件，請生成新的概述）。請以單一段落呈現，不要使用任何特殊符號（包括但不限於：\n、**、#、-、*、>、`等），不要使用分點符號，不要換行。請直接以流暢的一段文字描述：

        現有概述：{merged_news[event_key]["overview"]}
        新的摘要：{safe_process(row[11] or "")}
        新的內文：{safe_process(row[4] or "")}
        """
        merged_news[event_key]["overview"] = chat_with_xai(overview_prompt, xai_api_key, model_name, "").strip()

        # 更新摘要（僅保留最新的摘要內容）
        merged_news[event_key]["summary"] = safe_process(row[11] or "")

        # 標記該事件已處理
        processed_events.add(row[1])

        news_list = list(merged_news.values())
        news_list.sort(key=lambda x: x["recent_update"], reverse=True)

        # 在處理完資料後，將結果存入新的資料表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            region TEXT,
            cover TEXT,
            date TEXT,
            recent_update TEXT,
            location TEXT,
            overview TEXT,
            summary TEXT,
            daily_records TEXT,
            links TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 清空舊資料
        cursor.execute('DELETE FROM processed_news')
        
        # 儲存處理後的資料
        for news_item in news_list:
            cursor.execute('''
            INSERT INTO processed_news (
                event, region, cover, date, recent_update,
                location, overview, summary, daily_records, links
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_item['event'],
                news_item['region'],
                news_item['cover'],
                news_item['date'],
                news_item['recent_update'],
                json.dumps(news_item['location'], ensure_ascii=False),
                news_item['overview'],
                news_item['summary'],
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
    """
    如果資料表為空，調用 news_api 來處理資料
    否則直接從資料表讀取資料
    """
    try:
        conn = sqlite3.connect('w.db')
        cursor = conn.cursor()
        
        # 確保資料表存在
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            region TEXT,
            cover TEXT,
            date TEXT,
            recent_update TEXT,
            location TEXT,
            overview TEXT,
            summary TEXT,
            daily_records TEXT,
            links TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        
        # 檢查資料表是否為空
        cursor.execute('SELECT COUNT(*) FROM processed_news')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # 如果資料表為空，調用 news_api
            conn.close()  # 先關閉連接
            return news_api(request)  # 直接使用 news_api 的結果

        # 如果資料表有資料，直接讀取
        cursor.execute('''
        SELECT event, region, cover, date, recent_update,
               location, overview, summary, daily_records, links
        FROM processed_news
        ORDER BY date DESC
        ''')
        
        rows = cursor.fetchall()
        
        news_list = []
        for row in rows:
            news_item = {
                "來源": row[0],
                "標題": row[1],
                "連結": row[2],
                "內文": row[3],
                "時間": row[4],
                "圖片": row[5]
            }
            news_list.append(news_item)

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
        
        # 連接資料庫並清空上次的資料
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        
        # 清空資料表（如果存在的話）
        cursor.execute('''
        DROP TABLE IF EXISTS raw_news
        ''')
        
        # 重新建立資料表
        cursor.execute('''
        CREATE TABLE raw_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,           -- 來源
            title TEXT,            -- 標題
            link TEXT,             -- 連結
            content TEXT,          -- 內文
            date TEXT,             -- 時間
            image TEXT,            -- 圖片
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        
        # Google News 搜尋 URL
        urls = [
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%xA8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際大火
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際野火
            #加上bbc關鍵字
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%A8%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            # 'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',#新增國際大火
            'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%87%8E%E7%81%AB%20when%3A'+day+'d%20bbc&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'#新增國際野火
        ]
        
        all_news_items = []
        print("\n=== 開始爬取 Google News ===")
        for url in urls:
            print(f"\n搜尋URL: {url}")
            news_items = fetch_news(url)
            print(f"找到 {len(news_items)} 則新聞:")
            for item in news_items:
                print(f"\n標題: {item['標題']}")
                print(f"來源: {item['來源']}")
                print(f"連結: {item['連結']}")
                print(f"時間: {item['時間']}")
                print("-" * 50)
            all_news_items.extend(news_items)
        print("\n=== Google News 爬取完成 ===\n")

        if all_news_items:
            print(f"總共爬取到 {len(all_news_items)} 則新聞")
            news_df = pd.DataFrame(all_news_items)
            news_df = news_df.drop_duplicates(subset='標題', keep='first')
            print(f"去重後剩餘 {len(news_df)} 則新聞\n")

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

                content = content_results.get(source_name, '未找到內容')
                image_url = image_results.get(source_name, 'null')

                # 準備要存入 CSV 的資料
                result = {
                    '標題': item['標題'],
                    '連結': original_url,
                    '內文': content,
                    '來源': source_name,
                    '時間': item['時間'],
                    '圖片': image_url
                }

                # 儲存資料到 CSV
                output_df = pd.DataFrame([result])
                output_df.to_csv(first_stage_file, mode='a', header=not os.path.exists(first_stage_file), 
                               index=False, encoding='utf-8')

                print(f"已儲存新聞: {result['標題']}")

            driver.quit()

            # 將資料存入資料庫
            conn = sqlite3.connect('news.db')
            cursor = conn.cursor()

            # 修改資料表結構，使用英文欄位名稱
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,           -- 來源
                title TEXT,            -- 標題
                link TEXT,             -- 連結
                content TEXT,          -- 內文
                date TEXT,             -- 時間
                image TEXT,            -- 圖片
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 修改插入語句
            news_df = pd.read_csv(first_stage_file)
            for _, row in news_df.iterrows():
                cursor.execute('''
                INSERT INTO raw_news (source, title, link, content, date, image)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    row['來源'],
                    row['標題'],
                    row['連結'],
                    row['內文'],
                    row['時間'],
                    row['圖片']
                ))
            
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
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        
        # 修改查詢語句，使用英文欄位名稱
        cursor.execute('''
        SELECT source, title, link, content, date, image 
        FROM raw_news 
        ORDER BY date DESC
        ''')
        
        rows = cursor.fetchall()
        
        news_list = []
        for row in rows:
            news_item = {
                '來源': row[0],
                '標題': row[1],
                '連結': row[2],
                '內文': row[3],
                '時間': row[4],
                '圖片': row[5]
            }
            news_list.append(news_item)
            
        conn.close()
        return JsonResponse(news_list, safe=False)
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        print(f"Error in view_raw_news: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    