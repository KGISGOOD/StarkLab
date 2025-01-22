from django.shortcuts import render, redirect

#顯示report.html
def ai_report(request):
    # 從 session 中獲取並清除訊息
    context = {
        'train_message': request.session.pop('train_message', ''),
        'test_message': request.session.pop('test_message', ''),
        'outputText': request.session.pop('output_text', ''),
        'inputText': request.session.pop('input_text', '')
    }
    return render(request, 'report.html', context)

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain

from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt

import pandas as pd
import os
import csv

xai_api_key = "xai-sEKM3YfLj81l66aMWyXpmasF8Xab7hvpcwtEY4WU0jIeJfEoWDPSjm5VjbH9bq9JDNN5SmAAIrGyjfPN"
model_name = "grok-beta"

# 測試 xai API
@csrf_exempt 
def test_groq_api(request):
    if request.method == 'POST':
        print("訪問了 test_groq_api")  # 添加調試信息
        action = request.POST.get('action')
        if action == 'testButton':
            try:
                xai_api_url = "https://api.x.ai/v1/chat/completions"
                
                # 設置請求標頭和數據
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {xai_api_key}'
                }

                messages = [
                    {"role": "system", "content": "你是一個新聞分析助手，專門判斷新聞是否屬於同一事件。"},

                ]

                data = {
                    "messages": messages,
                    "model": model_name,
                    "temperature": 0,
                    "stream": False
                }

                # 發送 POST 請求
                response = requests.post(xai_api_url, headers=headers, json=data)
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.content}")
                # 檢查回應
                if response.status_code == 200:
                    request.session['test_message'] = 'API 測試成功!'
                else:
                    request.session['test_message'] = '錯誤'
            except Exception as e:
                request.session['test_message'] = f'錯誤：{str(e)}'
    return redirect('ai_report')


def setup_chatbot(xai_api_key, model_name):

    url = 'https://api.x.ai/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {xai_api_key}'
    }

    # 從檔案中讀取資料並學習
    initial_messages = []
    
    # 首先加入系統提示
    initial_messages.append({
        "role": "system",
        "content": """
        這是水利署的專案，目標是要就手邊的資訊進行新聞稿撰寫。請根據使用者提供的資訊，自動判斷分類（災害前、災害進行中、災害後），並以繁體中文（UTF-8)進行撰寫。

        新聞稿撰寫格式：
        1. 天氣狀況描述
        2. 事實陳述（現場狀況、應變作為等）
        3. 水利署宣導內容（防災整備、民眾配合事項等）

        日期格式部分：例如2024年11月1日，請參考前後文意，採用「今(1)日」「昨(1)日」等格式撰寫。

        如果資訊來源是會議記錄，請直接轉換為與民眾相關的事實陳述，不要提及任何會議相關內容或機關內部作業細節。

        請依照以上格式撰寫新聞稿，並用對應的語氣與風格。新聞稿長度約五百字，並請附上標題。
        
        請直接輸出內容，不需加入任何標記符號或段落標題。
        """
    })

    # 定義分類對應說明
    category_descriptions = {
        1: "災害前(防汛整備工作、滯洪池、防災管理、抽水機、河道疏濬、智慧防災、氣候變遷應對、洪水預警、防災數位轉型、淹水潛勢圖、防災聯繫)",
        2: "災害進行中（應變小組、豪雨特報、水情監控、抽水機啟用、河川水位、土石流警戒、降雨情勢、災情掌握、緊急疏散、防災聯繫）",
        3: "災害後（移動式抽水機、土壤含水量、坡地滑動、災情復原、供水正常、設施檢查、地震檢查、土石流警戒、疏散撤離、衛生消毒）"
    }

    # 假設檔案的讀取與 pandas DataFrame 相關
    data = pd.read_excel('learn.xlsx')  # 載入你的xlsx檔案

    for _, row in data.iterrows():
        title = row['標題']    # 標題
        content = row['內容']  # 使用的內容
        category = row['分類']

        # 將每個新聞作為示例加入
        initial_messages.append({
            "role": "system", 
            "content": f"以下是{category_descriptions[category]}的新聞稿範例："
        })
        initial_messages.append({
            "role": "assistant", 
            "content": f"標題：{title}\n\n內容：\n{content}"
        })

    data = {
        "messages": initial_messages,
        "model": model_name,
        "temperature": 0,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    if response.status_code == 200:
        return {
            'headers': headers,
            'initial_messages': initial_messages,
            'model': model_name
        }
    
    print(f"API 調用失敗 (狀態碼: {response.status_code})")
    return None

def train_view(request):
    if request.method == 'POST':
        print("訪問了 train_view")
        try:
            # 初始化 chatbot 並保存設置到 session
            model_settings = setup_chatbot(xai_api_key, model_name)
            if not model_settings:
                request.session['train_message'] = "模型初始化失敗！"
            else:
                request.session['model_settings'] = model_settings
                request.session['train_message'] = "模型初始化完成！"
                
        except Exception as e:
            print(f"初始化錯誤: {str(e)}")
            request.session['train_message'] = f"初始化過程發生錯誤：{str(e)}"
            
    return redirect('ai_report')

def chat_function(message, model_settings):
    try:
        if not model_settings:
            return "請先進行模型初始化訓練"
            
        url = 'https://api.x.ai/v1/chat/completions'
        messages = model_settings['initial_messages'].copy()
        messages.append({"role": "user", "content": message})
        
        data = {
            "messages": messages,
            "model": model_settings['model'],
            "temperature": 0,
            "stream": False
        }
        
        response = requests.post(url, headers=model_settings['headers'], json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        return "API 調用失敗"
    except Exception as e:
        print(f"聊天過程中發生錯誤: {str(e)}")
        return f"發生錯誤: {str(e)}"

def generate_view(request):
    if request.method == 'POST':
        input_text = request.POST.get('inputText')
        if input_text:
            # 從 session 中獲取模型設置
            model_settings = request.session.get('model_settings')
            output = chat_function(input_text, model_settings)
            request.session['input_text'] = input_text
            request.session['output_text'] = output
            # 記錄到 CSV 文件
            csv_path = 'chat_records.csv'
            file_exists = os.path.exists(csv_path)
            
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['input', 'output'])  # 寫入標題行
                writer.writerow([input_text, output])
                
    return redirect('ai_report')



import PyPDF2

def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('fileUpload')
        if uploaded_file:
            try:
                # 將上傳的檔案傳給 PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                content = ""

                # 逐頁讀取 PDF 的文字內容
                for page in pdf_reader.pages:
                    content += page.extract_text()

                # 如果成功讀取，將內容儲存到 session
                request.session['input_text'] = content or "錯誤：PDF 內容為空，請檢查檔案。"

            except Exception as e:
                # 捕捉錯誤並回報
                request.session['input_text'] = f"錯誤：無法讀取 PDF 檔案，請確認檔案格式是否正確。({str(e)})"
                return redirect('ai_report')
    
    return redirect('ai_report')
