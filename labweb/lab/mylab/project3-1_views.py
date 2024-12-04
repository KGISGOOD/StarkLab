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

# 定義允許的新聞來源
ALLOWED_SOURCES = {
    'Newtalk新聞',
    #'Yahoo奇摩新聞',
    '經濟日報',
    '自由時報',
    '中時新聞'
}

def fetch_article_content(driver, sources_urls):
    results = {}
    for source_name, url in sources_urls.items():
        if source_name not in ALLOWED_SOURCES:
            continue
            
        try:
            driver.get(url)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p'))
            )
            
            content_selectors = {
                'Newtalk新聞': 'div.articleBody.clearfix p',
                # 'Yahoo奇摩新聞': 'div.caas-body p',
                '經濟日報': 'section.article-body__editor p',
                '自由時報': 'div.text p',
                '中時新聞': 'div.article-body p'
            }
            
            selector = content_selectors.get(source_name, 'p')
            paragraphs = driver.find_elements(By.CSS_SELECTOR, selector)
            content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
            
            results[source_name] = content if content else '未找到內容'
            
        except Exception as e:
            print(f"抓取內容失敗: {e}")
            results[source_name] = '錯誤'
            
    return results

def extract_image_url(driver, sources_urls):
    results = {}
    for source_name, url in sources_urls.items():
        if source_name not in ALLOWED_SOURCES:
            continue
            
        try:
            driver.get(url)
            image_selectors = {
                'Newtalk新聞': "div.news_img img",
                # 'Yahoo奇摩新聞': "div.caas-img-container img",
                '經濟日報': "section.article-body__editor img",
                '自由時報': "div.image-popup-vertical-fit img",
                '中時新聞': "div.article-body img"
            }
            
            if source_name in image_selectors:
                try:
                    image_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, image_selectors[source_name]))
                    )
                    image_url = image_element.get_attribute('src') or image_element.get_attribute('data-src')
                    results[source_name] = image_url or 'null'
                except Exception as e:
                    print(f"圖片擷取失敗: {e}")
                    results[source_name] = 'null'
            else:
                results[source_name] = 'null'
                
        except Exception as e:
            print(f"圖片擷取錯誤: {e}")
            results[source_name] = 'null'
            
    return results


# 加載 CSV 資料
def load_csv():
    file_path = "w.csv"
    try:
        data = pd.read_csv(file_path)
        if "標題" in data.columns and "內文" in data.columns:
            return data  # 成功讀取時返回資料
        else:
            raise ValueError("CSV 檔案中缺少必要的欄位：標題或內文。")
    except Exception as e:
        return str(e)  # 返回錯誤訊息

# 與 X.AI 聊天功能互動
def chat_with_xai(message, api_key, model_name, csv_summary):
    try:
        url = 'https://api.x.ai/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        messages = [
            {"role": "system", "content": "You are a disaster analysis assistant."},
            {"role": "user", "content": f"使用者提問：{message}\n\n摘要資料：\n{csv_summary}"}
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
            return f"發生錯誤: {response.status_code} - {response.text}"

    except Exception as e:
        return f"發生錯誤: {str(e)}"

# 問問題並獲得回應的通用函數
def get_xai_responses(title, content, xai_api_key, model_name):
    # 將標題和內文組合成一個訊息
    combined_content = f"標題：{title}\n內文：{content}"

    question_summary = f"請簡要總結以下內文，限20字內：\n{combined_content}"
    question_location = f"請從以下內文中提取災害發生的國家和地點，只需顯示國家和地點即可，限10字內：\n{combined_content}"
    question_disaster = f"請從以下內文中提取所有災害，只需顯示災害即可，限10字內：\n{combined_content}"

    summary_answer = chat_with_xai(question_summary, xai_api_key, model_name, combined_content)
    location_answer = chat_with_xai(question_location, xai_api_key, model_name, combined_content)
    disaster_answer = chat_with_xai(question_disaster, xai_api_key, model_name, combined_content)

    return summary_answer, location_answer, disaster_answer

# 更新 CSV 資料並儲存
def update_and_save_csv(data):
    file_path = "w.csv"
    try:
        data.to_csv(file_path, index=False, encoding='utf-8-sig')
        print("摘要、地點和災害已成功儲存到 CSV 檔案中。")
    except Exception as e:
        print(f"儲存 CSV 檔案時發生錯誤：{str(e)}")


def main():
    start_time = time.time()
    urls = [
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%A4%A7%E9%9B%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E8%B1%AA%E9%9B%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%9A%B4%E9%9B%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B7%B9%E6%B0%B4%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B4%AA%E6%B0%B4%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B0%B4%E7%81%BD%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B1%E9%A2%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B6%E9%A2%A8%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E9%A2%B8%E7%81%BD%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%B5%B7%E5%98%AF%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E5%9C%B0%E9%9C%87%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E4%B9%BE%E6%97%B1%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant',
        'https://news.google.com/search?q=%E5%9C%8B%E9%9A%9B%E6%97%B1%E7%81%BD%20when%3A7d&hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'
    ]

    # 定義關鍵字
    domestic_keywords = [
        '台灣', '台北', '新北', '基隆', '新竹市', '桃園', '新竹縣', '宜蘭', 
        '台中', '苗栗', '彰化', '南投', '雲林', '高雄', '台南', '嘉義', 
        '屏東', '澎湖', '花東', '花蓮', '台9線', '金門', '馬祖', '綠島', '蘭嶼',
        '臺灣', '台北', '臺中', '臺南', '臺9縣', '全台', '全臺']

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

        for index, item in news_df.iterrows():
            source_name = item['來源']
            original_url = item['連結']
            final_url = extract_final_url(original_url)

            # 創建包含單一來源和URL的字典
            sources_urls = {source_name: final_url}

            # 使用新的函數格式來獲取內容和圖片
            content_results = fetch_article_content(driver, sources_urls)
            image_results = extract_image_url(driver, sources_urls)

            # 從結果字典中獲取內容和圖片URL
            content = content_results.get(source_name, '未找到內容')
            image_url = image_results.get(source_name, 'null')

            region = '國內' if any(keyword in item['標題'] or keyword in content for keyword in domestic_keywords) else '國外'

            if content != '未找到內容' and content != '錯誤':
                result = {
                    '標題': item['標題'],
                    '連結': original_url,
                    '內文': content,
                    '來源': source_name,
                    '時間': item['時間'],
                    '圖片': image_url,
                    '地區': region
                }

                skip_keywords = ['票', '戰爭', 'GDP']
                
                desired_keywords = ['大雨', '豪雨', '暴雨', '淹水', '洪水', '水災', 
                                    '颱風', '颶風', '風災', '海嘯', '地震', '乾旱', '旱災']

                if any(keyword in result['標題'] or keyword in result['內文'] for keyword in skip_keywords):
                    print(f"跳過包含指定關鍵字的文章: {result['標題']}")
                    continue

                if not any(keyword in result['標題'] or keyword in result['內文'] for keyword in desired_keywords):
                    print(f"文章不包含所需的關鍵字: {result['標題']}")
                    continue

                # 從標題和內文獲得模型分析結果
                summary_answer, location_answer, disaster_answer = get_xai_responses(result['標題'], result['內文'], "your_api_key", "your_model_name")

                # 把結果新增到資料框中
                result['摘要'] = summary_answer
                result['災害地點'] = location_answer
                result['災害類型'] = disaster_answer

                # 儲存結果到 CSV
                output_df = pd.DataFrame([result])
                output_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False, encoding='utf-8')

                print(f"標題: {result['標題']}")
                print(f"連結: {result['連結']}")
                print(f"內文: {result['內文'][:50]}...")  # 顯示前50字
                print(f"摘要: {result['摘要']}")
                print(f"災害地點: {result['災害地點']}")
                print(f"災害類型: {result['災害類型']}")
                print(f"來源: {result['來源']}")
                print(f"時間: {result['時間']}")
                print(f"圖片: {result['圖片']}")
                print(f"地區: {result['地區']}")
                print('-' * 80)

        driver.quit()

    end_time = time.time()
    elapsed_time = int(end_time - start_time)
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"爬蟲程式執行完成，總共花費時間: {hours}小時{minutes}分鐘{seconds}秒")



import sqlite3
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import json

def fetch_news_data():
    db_name = 'w.db'
    table_name = 'news'

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(f'SELECT id, title, link, content, source, date, image, region, location FROM {table_name}')
    news_data = cursor.fetchall()

    conn.close()

    news_list = []
    for row in news_data:
        # 摘要：取 content 的前50個字
        summary = row[3][:50] + '...' if len(row[3]) > 50 else row[3]
        disaster_type = '災害類型待補充'  # 假設災害類型，根據實際情況進行更改

        news_list.append({
            'id': row[0],
            'title': row[1],
            'link': row[2],
            'content': row[3],
            'summary': summary,  # 新增摘要欄位
            'source': row[4],
            'date': row[5],
            'image': row[6],
            'region': row[7],  # 地區
            'location': row[8],  # 新增地點欄位
            'disaster': disaster_type  # 假設災害類型
        })

    return news_list

def update_news(request):
    main()  # 執行爬取新聞的函數
    return JsonResponse({'message': '新聞更新成功！'})

# views.py
from django.shortcuts import render
from .models import News

# 處理新聞列表及搜尋功能
def news_view(request):
    query = request.GET.get('search', '')  # 取得搜尋關鍵字

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
        summary = row[3][:50] + '...' if len(row[3]) > 50 else row[3]  # 摘要：前50個字
        disaster_type = '災害類型待補充'  # 假設災害類型，根據實際情況可進行更改
        
        news_list.append({
            'id': row[0],
            'title': row[1],
            'link': row[2],
            'content': row[3],
            'summary': summary,  # 摘要
            'source': row[4],
            'date': row[5],
            'image': row[6],
            'region': row[7],  # 地區
            'location': row[8],  # 地點
            'disaster': disaster_type  # 災害類型
        })

    return render(request, 'news.html', {'news_list': news_list})

# RESTful API 查詢所有新聞資料並以JSON格式返回
def news_list(request):
    if request.method == 'GET':
        news = News.objects.all().values('title', 'link', 'content', 'source', 'date', 'image', 'region', 'location') 
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
            location=data.get('location', '未知')  # 新增地點欄位
        )
        return JsonResponse({"message": "News created", "news_id": news.id}, status=201)

@require_GET
def news_api(request):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect('w.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, link, content, source, date, image, region, location FROM news")
        news_data = cursor.fetchall()

        # 關閉資料庫連接
        conn.close()

        # 將結果轉換為字典列表
        news_list = []
        for row in news_data:
            summary = row[3][:50] + '...' if len(row[3]) > 50 else row[3]  # 摘要：前50個字
            disaster_type = '災害類型待補充'  # 假設災害類型，根據實際情況可進行更改
            
            news_list.append({
                'id': row[0],
                'title': row[1],
                'link': row[2],
                'content': row[3],
                'summary': summary,  # 摘要
                'source': row[4],
                'date': row[5],
                'image': row[6],
                'region': row[7],
                'location': row[8],  # 地點
                'disaster': disaster_type  # 災害類型
            })

        return JsonResponse(news_list, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
