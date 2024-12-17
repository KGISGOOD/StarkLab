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

xai_api_key = os.getenv("API_KEY")
model_name = "grok-beta"

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
            date = datetime.now()

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
            
            # 更新選擇器以只包含四家報社
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

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return "false"  # 如果 API 調用失敗，預設返回 false

    except Exception as e:
        print(f"X.AI API 錯誤: {str(e)}")
        return "false"  # 發生錯誤時預設返回 false

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
    
    response = chat_with_xai(prompt, xai_api_key, model_name, "")
    return 'true' in response.lower()

# 主程式
def main():
    start_time = time.time()
    
    # Google News 搜 URL
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

        # X.AI 的 API Key 和模型名稱
        xai_api_key =os.getenv("API_KEY") # 請填入你的 API 密鑰
        model_name = "grok-beta"

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

            # 提問並取得摘要、地點與災害
            question_summary = f"請簡要總結以下內文，限20字內：{content}"
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
                question_summary = f"請簡要總結以下內文，限20字內：{csv_summary}"
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
                    '內文': content,
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
    return JsonResponse({'message': '聞更新成功！'})


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
        conn.close()

        def safe_process(value):
            return value.replace("\n", " ").replace("-", "").strip() if value else ""

        def parse_location(location_str):
            if not location_str:
                return []
            # 確保 location_str 是字符串
            if isinstance(location_str, (list, dict)):
                location_str = json.dumps(location_str, ensure_ascii=False)
            locations = [loc.strip() for loc in location_str.split(',')]
            return list(filter(None, locations))

        # 用於存儲合併後的新聞
        merged_news = {}
        processed_events = set()

        for row in news_data:
            if row[1] in processed_events:
                continue

            current_event = row[1]
            location = parse_location(row[9])  # 使用數據庫中的 location 欄位
            disaster = safe_process(row[10])
            
            # 根據 location 判斷是否為國內新聞
            is_domestic = any(keyword in ','.join(location) for keyword in domestic_keywords)
            region = '國內' if is_domestic else '國外'

            news_item = {
                "source": row[5] or "",
                "url": row[3] or "",
                "title": row[1] or "",
                "publish_date": row[6] or "",
                "location": location,
                "summary": safe_process(row[11] or "")
            }

            # 尋找相關事件
            event_key = None
            for existing_key in merged_news.keys():
                if (disaster in merged_news[existing_key]["event"] or 
                    disaster in merged_news[existing_key]["overview"]) and \
                   any(loc in merged_news[existing_key]["event"] or 
                       loc in merged_news[existing_key]["overview"] 
                       for loc in location):
                    event_key = existing_key
                    break

            if event_key:
                # 將新聞添加到現有事件
                merged_news[event_key]["links"].append(news_item)
                
                # 更新最近更新日期並添加每日記錄
                current_date = row[7] or row[6] or ""
                if current_date > merged_news[event_key]["recent_update"]:
                    merged_news[event_key]["recent_update"] = current_date
                    merged_news[event_key]["daily_records"].append({
                        "date": current_date,
                        "content": safe_process(row[11] or ""),
                        "location": location
                    })
                
                # 如果當前新聞有圖片且主事件沒有圖片，則更新圖片
                if row[2] and not merged_news[event_key]["cover"]:
                    merged_news[event_key]["cover"] = row[2]
            else:
                # 創建新的事件
                new_key = f"{disaster}_{','.join(sorted(location))}_{len(merged_news)}"
                merged_news[new_key] = {
                    "event": current_event,
                    "region": region,  # 使用根據 location 判斷的結果
                    "cover": row[2] or "",
                    "date": row[6] or "",
                    "recent_update": row[7] or row[6] or "",
                    "location": location,
                    "overview": safe_process(row[11]),
                    "daily_records": [{
                        "date": row[7] or row[6] or "",
                        "content": safe_process(row[11] or ""),
                        "location": location
                    }],
                    "links": [news_item]
                }

            processed_events.add(current_event)

        # 將字典轉換為列表並按日期排序
        news_list = list(merged_news.values())
        news_list.sort(key=lambda x: x["recent_update"], reverse=True)

        return JsonResponse(news_list, safe=False)
    except Exception as e:
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
    