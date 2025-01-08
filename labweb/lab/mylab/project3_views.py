# 架構：爬蟲 -> 資料清理 & AI 分析 -> 寫入 CSV -> 從 CSV寫入資料庫 -> Views展示階段

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
from django.http import JsonResponse
from .models import News
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET


xai_api_key = "xai-sEKM3YfLj81l66aMWyXpmasF8Xab7hvpcwtEY4WU0jIeJfEoWDPSjm5VjbH9bq9JDNN5SmAAIrGyjfPN"
model_name = "grok-beta"

'''-------------------------------------------------
                       設定變數
----------------------------------------------------'''

# 修改 ALLOWED_SOURCES 為只包含四家報社
ALLOWED_SOURCES = {
    'Newtalk新聞',
    '經濟日報',
    '自由時報',
    '中時新聞'
}

# 定義允許的自然災害關鍵字
DISASTER_KEYWORDS = {
    '大雨', '豪雨', '暴雨', '淹水', '洪水', '水災',
    '颱風', '颶風', '風災',
    '地震', '海嘯',
    '乾旱', '旱災'
}

# 關鍵字設定 - 用於判斷國內新聞
domestic_keywords = [
    '台灣', '台北', '新北', '基隆', '新竹市', '桃園', '新竹縣', '宜蘭', 
    '台中', '苗栗', '彰化', '南投', '雲林', '高雄', '台南', '嘉義', 
    '屏東', '澎湖', '花東', '花蓮', '台9線', '金門', '馬祖', '綠島', '蘭嶼',
    '臺灣', '台北', '臺中', '臺南', '臺9縣', '全台', '全臺'
]

'''-------------------------------------------------
            爬蟲功能(裡面已經一次性寫入csv檔了)
----------------------------------------------------'''

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
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A'+day+'d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'
    ]
    
    #收集新聞
    all_news_items = []
    for url in urls:
        news_items = fetch_news(url)
        all_news_items.extend(news_items)

    #處理新聞資料
    if all_news_items:
        news_df = pd.DataFrame(all_news_items)
        news_df = news_df.drop_duplicates(subset='標題', keep='first')

        # 設定輸出檔案
        driver = setup_chrome_driver()
        output_file = 'w.csv'
        if os.path.exists(output_file):
            os.remove(output_file)

        # 新增欄位：摘要、地點、災害
        summaries = []
        locations = []
        disasters = []

        # 處理每個新聞項目
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
            請從以下內文中萃取出災害相關資訊。只需顯示有資料的項目，並在數值前加上項目名稱。
            如果某項資訊在內文中未提及，則不要顯示該項目。各項目之間用逗號分隔。
            時間必須是完整的年月日格式（例如：2024-01-15），不要使用「今天」、「昨天」、「前天」等相對時間。
            如果無法從內文中確定完整時間，則使用 {item['時間']} 作為事件時間。

            範例格式：
            災害種類：地震，死亡人數：3人，受傷人數：12人，撤離人數：50人，受困人數：6人，受災人數：180人，經濟損失：3億元，建物受損：52棟，建物倒塌：13棟，特殊事件：建物搖晃，坍塌事件：2處，時間：2024-01-15

            請依照以下順序檢查並提供資訊：
            災害種類、降雨量、死亡人數、受傷人數、撤離人數、失蹤人數、受困人數、受災人數、經濟損失、建物受損、建物倒塌、淹水高度、淹水範圍、特殊事件、坍塌事件、崩塌事件、國家和地區、農業損失、時間

            內文內容：
            {content}
            """
            question_location = f"請從以下內文中提取災害發生的國家和地點，只需顯示國家和地點即可，限10字內：{content}"
            question_disaster = f"請從以下內文中提取所有災害，只需顯示災害即可，若有相同的災害則存一個即可，限10字內：{content}"

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

                # 提問並取得摘要、地點與災害
                question_summary = f"""
                請從以下內文中萃取出災害相關資訊。只需顯示有資料的項目，並在數值前加上項目名稱。
                如果某項資訊在內文中未提及，則不要顯示該項目。各項目之間用逗號分隔。
                時間必須是完整的年月日格式（例如：2024-01-15），不要使用「今天」、「昨天」、「前天」等相對時間。
                如果無法從內文中確定完整時間，則使用 {item['時間']} 作為事件時間。

                範例格式：
                災害種類：地震，死亡人數：3人，受傷人數：12人，撤離人數：50人，受困人數：6人，受災人數：180人，經濟損失：3億元，建物受損：52棟，建物倒塌：13棟，特殊事件：建物搖晃，坍塌事件：2處，時間：2024-01-15

                請依照以下順序檢查並提供資訊：
                災害種類、降雨量、死亡人數、受傷人數、撤離人數、失蹤人數、受困人數、受災人數、經濟損失、建物受損、建物倒塌、淹水高度、淹水範圍、特殊事件、坍塌事件、崩塌事件、國家和地區、農業損失、時間

                內文內容：
                {csv_summary}
                """
                question_location = f"請從以下內文中提取災害發生的國家和地點，只需顯示國家和地點即可，限10字內：{csv_summary}"
                question_disaster = f"請從以下內文中提取所有災害，只需顯示災害即可，若有相同的災害則存一個即可，限10字內：{csv_summary}"

                summary_answer = chat_with_xai(question_summary, xai_api_key, model_name, csv_summary)
                location_answer = chat_with_xai(question_location, xai_api_key, model_name, csv_summary)
                disaster_answer = chat_with_xai(question_disaster, xai_api_key, model_name, csv_summary)

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

                # 儲存資料到 CSV。所有處理完成後，一次性寫入 CSV
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

# 從 Google News 抓取新聞資料的爬蟲功能
def fetch_news(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all('article', class_='IFHyqb')  # 查找所有文章

        news_list = []
        for article in articles:
            title_element = article.find('a', class_='JtKRv')  # 查找標題元素
            title = title_element.get_text(strip=True) if title_element else '未知'
            link = title_element.get('href', '').strip() if title_element else ''
            full_link = requests.compat.urljoin(url, link)  # 獲取完整連結

            news_source = article.find('div', class_='vr1PYe')  # 查找來源元素
            source_name = news_source.get_text(strip=True) if news_source else '未知'

            # 只處理允許的新聞來源
            if source_name not in ALLOWED_SOURCES:
                continue

            time_element = article.find('div', class_='UOVeFe').find('time', class_='hvbAAd') if article.find('div', 'UOVeFe') else None
            date_str = time_element.get_text(strip=True) if time_element else '未知'

            date = parse_date(date_str)  # 解析時間

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

# 解析和標準化新聞的日期格式
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

# 瀏覽器的無頭模式，讓 Chrome 在背景運行而不需要開啟實際的瀏覽器視窗
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

# 從 Google News 的 URL 中提取最終的 URL
def extract_final_url(google_news_url):
    match = re.search(r'(https?://[^&]+)', google_news_url)
    if match:
        return match.group(1)
    return google_news_url

# 從新聞網站中擷取內容和摘要
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
            
            # 只處理這四家報社
            # content_selectors「怎麼抓？」
            content_selectors = {
                'Newtalk新聞': 'div.articleBody.clearfix p',
                '經濟日報': 'section.article-body__editor p',
                '自由時報': 'div.text p',
                '中時新聞': 'div.article-body p'
            }
            
            selector = content_selectors.get(source_name)
            if not selector:  # 如果沒有對應的選擇器，跳過
                continue
                
            paragraphs = driver.find_elements(By.CSS_SELECTOR, selector)
            content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
            
            # 提取摘要（取前100字）
            summary = content[:100] if content else '未找到內容'
            
            results[source_name] = content if content else '未找到內容'
            summaries[source_name] = summary
            
        except Exception as e:
            print(f"抓取內容失敗: {e}")
            results[source_name] = '錯誤'
            summaries[source_name] = '錯誤'
            
    return results, summaries

# 從新聞網站中擷取圖片 URL
def extract_image_url(driver, sources_urls):
    results = {}
    for source_name, url in sources_urls.items():
        if source_name not in ALLOWED_SOURCES:
            continue
            
        try:
            driver.get(url)
            # 更新圖片選擇器以只包含四家報社
            image_selectors = {
                'Newtalk新聞': "div.news_img img",
                '經濟日報': "section.article-body__editor img",
                '自由時報': "div.image-popup-vertical-fit img",
                '中時新聞': "div.article-body img"
            }
            
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
    
'''-------------------------------------------------
                    資料清理 & AI 分析
----------------------------------------------------'''

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
    
    允許的災害類型：大雨、豪雨、暴雨、淹水、洪水、水災、颱風、颶風、風災、地震、海嘯、乾旱、旱災

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
    
    # 呼叫 X.AI API 進行判斷 xai_api_key：API 金鑰 model_name：使用的模型名稱 ""：空的上下文。每次對話都是獨立的，AI 不會記得之前的對話
    response = chat_with_xai(prompt, xai_api_key, model_name, "")
    return 'true' in response.lower()

def news_api(request):
    # 資料庫連接
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
        conn.close()

        # 使用 AI 生成標準格式的標題
        # AI分析階段
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

        def is_pure_disaster_news(title, content):
            """判斷是否為純災害新聞"""
            prompt = f"""
            請判斷以下新聞是否為純災害新聞報導，只需回答 true 或 false。

            新聞標題：{title}
            新聞內容：{content[:500]}

            判斷標準：
            1. 必須主要報導自然災害本身（如地震、颱風、洪水、乾旱等）
            2. 不應包含以下內容：
               - 政治議題或政策討論
               - 經濟影響或金融市場反應
               - 救援或援助活動
               - 災後重建計劃
               - 防災措施或政策
               - 氣候變遷討論
               - 歷史災害回顧
               - 賠償金額討論
               - 保險理賠相關
            3. 內容應集中在：
               - 災害發生的情況
               - 災害的規模（如地震規模、雨量）
               - 受影響的地理範圍
               - 即時災情描述
               - 災害造成的損失金額和財產損失統計
            """
            
            response = chat_with_xai(prompt, xai_api_key, model_name, "")
            return 'true' in response.lower()

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

            判斷標準：
            1. 地震事件的特殊判斷：
               - 如果是同一個國家在5天內發生的地震，視為同一事件
               - 即使地點描述不同（如「近海」、「首都」、「某城市」），只要是同一國家都視為同一事件
               - 餘震也應該歸類在同一事件中
               - 例如：「萬那杜近海地震」和「萬那杜維拉港地震」應該視為同一事件

            2. 其他災害類型判斷：
               - 同一國家3天內的相同類型災害視為同一事件
               - 相鄰區域的相同災害視為同一事件

            3. 特別注意：
               - 地震新聞中的「近海」、「外海」、「城市名」都應視為同一國家的同一事件
               - 日期相近（5天內）的地震通常為同一地震事件的後續報導
               - 規模不同也可能是後續修正或不同機構的測量結果

            請根據以上標準判斷。
            """

            response = chat_with_xai(prompt, xai_api_key, model_name, "")
            return 'true' in response.lower()

        # 資料清理階段
        def safe_process(value):
            """安全處理文字，移除特殊字符"""
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
            if not is_pure_disaster_news(row[1], row[4] or ""):
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

            if event_key:
                # 合併 location，確保不重複且格式正確
                all_locations = set(merged_news[event_key]["location"])
                all_locations.update(location)
                merged_news[event_key]["location"] = sorted(list(all_locations))  # 排序以保持穩定順序
                
                merged_news[event_key]["links"].append(news_item)
                
                current_date = row[7] or row[6] or ""
                if current_date > merged_news[event_key]["recent_update"]:
                    merged_news[event_key]["recent_update"] = current_date
                    merged_news[event_key]["daily_records"].append({
                        "date": current_date,
                        "content": safe_process(row[11] or ""),
                        "location": location
                    })
                
                # 更新 cover
                if cover != "null" and merged_news[event_key]["cover"] == "null":
                    merged_news[event_key]["cover"] = cover
                
                # 更新 overview，加入新的摘要和內文資訊
                overview_prompt = f"""
                請整合以下新的資訊到現有的概述中。請以單一段落呈現，不要使用任何特殊符號（包括但不限於：\n、**、#、-、*、>、`等），不要使用分點符號，不要換行。請直接以流暢的一段文字描述：

                現有概述：{merged_news[event_key]["overview"]}
                新的摘要：{safe_process(row[11] or "")}
                新的內文：{safe_process(row[4] or "")}
                """
                merged_news[event_key]["overview"] = chat_with_xai(overview_prompt, xai_api_key, model_name, "").strip()
            else:
                # 生成初始 overview
                overview_prompt = f"""
                請根據以下資訊生成一個完整的災害事件概述。請以單一段落呈現，不要使用任何特殊符號（包括但不限於：\n、**、#、-、*、>、`等），不要使用分點符號，不要換行。請直接以流暢的一段文字描述：

                事件標題：{formatted_event}
                事件摘要：{safe_process(row[11] or "")}
                詳細內文：{safe_process(row[4] or "")}
                """
                initial_overview = chat_with_xai(overview_prompt, xai_api_key, model_name, "").strip()
                
                new_key = f"{formatted_event}_{len(merged_news)}"
                merged_news[new_key] = {
                    "event": formatted_event,
                    "region": '國內' if any(keyword in ','.join(location) for keyword in domestic_keywords) else '國外',
                    "cover": cover,  # 使用處理過的 cover
                    "date": row[6] or "",
                    "recent_update": row[7] or row[6] or "",
                    "location": location,
                    "overview": initial_overview,
                    "summary": safe_process(row[11] or ""),  # 只保留當前新聞的摘要
                    "daily_records": [{
                        "date": row[7] or row[6] or "",
                        "content": safe_process(row[11] or ""),
                        "location": location
                    }],
                    "links": [news_item]
                }

            processed_events.add(row[1])

        news_list = list(merged_news.values())
        news_list.sort(key=lambda x: x["recent_update"], reverse=True)

        return JsonResponse(news_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
'''-------------------------------------------------
                       從CSV寫入資料庫
----------------------------------------------------'''
# 從 CSV寫入資料庫
@csrf_exempt
def news_create(request):
    if request.method == 'POST': # POST 方法（新增資料）
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
    
#單純抓取資料庫資料
@require_GET
def news_api_sql(request):
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
        conn.close()

        def safe_process(value):
            """移除特殊符號並清理文字"""
            if value:
                value = value.replace("\n", " ").replace("-", "")
                value = " ".join(value.split())
                return value.strip()
            return ""

        news_list = []
        for row in news_data:
            # 處理 daily_records
            default_record = {
                "date": row[6] or "",
                "content": safe_process(row[11] or ""),
                "location": [row[9]] if row[9] else []
            }

            try:
                daily_records = json.loads(row[12]) if row[12] else [default_record]
                processed_records = []
                for record in daily_records:
                    processed_record = {
                        "date": record.get("date", default_record["date"]),
                        "content": safe_process(record.get("content", default_record["content"])),
                        "location": record.get("location", default_record["location"])
                    }
                    processed_records.append(processed_record)
            except (json.JSONDecodeError, TypeError):
                processed_records = [default_record]

            if not processed_records:
                processed_records = [default_record]

            # 處理 links
            try:
                # 創建預設的 link 項目
                default_link = {
                    "source": row[5] or "",
                    "url": row[3] or "",
                    "title": row[1] or "",
                    "publish_date": row[6] or "",
                    "location": row[9] or "",
                    "summary": safe_process(row[11] or "")
                }

                # 嘗試解析資料庫中的 links
                links_data = json.loads(row[13]) if row[13] else []
                
                # 如果沒有其他相關新聞，則返回 null
                if not links_data or (len(links_data) == 1 and links_data[0] == row[3]):
                    processed_links = "null"
                else:
                    # 處理每個 link
                    processed_links = []
                    for link_data in links_data:
                        if isinstance(link_data, dict):
                            # 如果已經是正確格式的 dict
                            processed_link = {
                                "source": link_data.get("source", ""),
                                "url": link_data.get("url", ""),
                                "title": link_data.get("title", ""),
                                "publish_date": link_data.get("publish_date", ""),
                                "location": link_data.get("location", ""),
                                "summary": safe_process(link_data.get("summary", ""))
                            }
                        else:
                            # 如果只是 URL 字符串，使用預設值
                            processed_link = default_link.copy()
                            processed_link["url"] = link_data
                        processed_links.append(processed_link)
            except (json.JSONDecodeError, TypeError):
                processed_links = "null"

            news_item = {
                "event": row[1],
                "cover": row[2] or "null",
                "link": row[3],
                "content": row[4],
                "source": row[5],
                "date": row[6],
                "recent_update": row[7],
                "region": row[8],
                "location": row[9],
                "disaster": safe_process(row[10]),
                "summary": row[11],
                "daily_records": processed_records,
                "links": processed_links
            }
            news_list.append(news_item)

        return JsonResponse(news_list, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

'''-------------------------------------------------
                     Views展示階段
----------------------------------------------------'''

# views.py
# 處理新聞列表及搜尋功能
def news_view(request):
    query = request.GET.get('search', '')

    conn = sqlite3.connect('w.db')  # 連接到 SQLite 資料庫
    cursor = conn.cursor()  # 建立資料庫游標

    if query:
        # 如果有搜尋關鍵字，搜尋事件名稱中包含關鍵字的新聞
        cursor.execute("SELECT * FROM news WHERE event LIKE ?", ('%' + query + '%',))
    else:
        # 如果沒有搜尋關鍵字，取得所有新聞
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
# Views展示階段
def news_list(request):
    if request.method == 'GET': # GET 方法（讀取資料）
        # 查詢所有新聞記錄，並返回標題、連結、內容、來源和日期
        news = News.objects.all().values('title', 'link', 'content', 'source', 'date', 'image', 'region', 'summary', 'location', 'disaster')        
        return JsonResponse(list(news), safe=False)

# 新增更新新聞每日記錄的 API 端點
# @csrf_exempt  # 關閉 CSRF 保護，允許外部 POST 請求
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

def update_news(request):
    main()  # 執行爬取新聞的函數
    return JsonResponse({'message': '新聞更新成功！'})
    