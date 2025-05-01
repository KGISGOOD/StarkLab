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

# from langchain.memory import ConversationBufferMemory
# from langchain.prompts import PromptTemplate
# from langchain.chains import ConversationChain

from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt

import pandas as pd
import os
import csv

#導入api key
from config import xai_api_key, model_name

# 測試 xai API
@csrf_exempt 
def test_groq_api(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'testButton':
            try:
                xai_api_url = "https://api.x.ai/v1/chat/completions"
                
                # 設置請求標頭和數據
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {xai_api_key}'
                }

                messages = [{"role": "user", "content": "測試"}]

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


def setup_chatbot(xai_api_key, model_name, training_prompt, disaster_phase):

    url = 'https://api.x.ai/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {xai_api_key}'
    }

    # 從檔案中讀取資料並學習
    initial_messages = []
    
    output_prompt = """
    請用剛剛記錄的格式輸出新的一篇新聞稿，新聞稿長度約五百字，並且附上標題。

    第一部分：請描述天氣或災害狀況，例如天氣情況，例如:降雨或地震相關資訊。

    第二部分：請陳述災情的具體事實，包括災害範圍、影響的區域、現場狀況、應變作為及相關數據，確保資訊具體且有條理。

    第三部分：請說明水利署針對災情發出的防災與應對建議，詳細列出防範措施、民眾應配合的事項，以及其他宣導內容。

    日期格式部分：請使用「今(1)日」、「昨(1)日」等方式表示日期，並在新聞稿中提及具體日期時，按照「2024年11月1日」的格式呈現，確保日期表達流暢自然。

    如果資訊來源是會議記錄，請直接轉換為與民眾相關的事實陳述，不要提及任何會議相關內容或機關內部作業細節。

    **格式規則（請嚴格遵守）**：
    1. **嚴禁**使用 Markdown 語法，請**不要**使用 `#`（標題符號）、`*`（星號）、`-`（條列符號）、`>`（引用符號）或其他特殊符號。
    2. **嚴禁**使用條列式寫法（例如「- 颱風來襲」這種格式），請全部用完整敘述句，例如：「根據氣象局資料，颱風已經進入台灣東部海域，並且帶來強風豪雨。」 
    3. 請確保新聞稿內容流暢、易讀，**每一部分的內容應該至少有三句以上**，避免過於簡短。
    4. **請直接輸出新聞稿內容，不要加入任何標記符號或段落標題**，確保格式乾淨。


    """
    # 首先加入系統提示
    initial_messages.append({
        "role": "system",
        "content": training_prompt
    })

    # 讀取和過濾數據
    filtered_data = load_and_filter_data(disaster_phase)

    for _, row in filtered_data.iterrows():
        title = row['標題']
        content = row['內容']
        initial_messages.append({
            "role": "system", 
            "content": f"以下是{disaster_phase}的新聞稿範例："
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
            'model': model_name,
            'output_prompt': output_prompt,
        }
    
    print(f"API 調用失敗 (狀態碼: {response.status_code})")
    return None

def load_and_filter_data(disaster_phase):
    try:
        data = pd.read_excel('learn.xlsx')
        if disaster_phase == '災前':
            return data[data['分類'] == 1]
        elif disaster_phase == '災中':
            return data[data['分類'] == 2]
        elif disaster_phase == '災後':
            return data[data['分類'] == 3]
        else:
            print("無效的災害階段選擇")
            return pd.DataFrame()
    except Exception as e:
        print(f"讀取檔案時發生錯誤: {str(e)}")
        return pd.DataFrame() 

def train_view(request):
    if request.method == 'POST':
        disaster_phase = request.POST.get('disasterPhase')
        
        # 根據選擇的災害階段設置不同的訓練提示
        if disaster_phase == '災前':
            training_prompt = '''
            你是一個新聞稿撰寫助手，專門負責災害前的新聞稿撰寫。你的任務是學習並掌握過去災害前新聞稿的格式、寫作風格與口吻，並根據提供的資料，生成符合此風格的新聞稿。
            '''
        elif disaster_phase == '災中':
            training_prompt = '''
            你是一個新聞稿撰寫助手，專門負責災害進行中的新聞稿撰寫。你的任務是學習並掌握過去災害前新聞稿的格式、寫作風格與口吻，並根據提供的資料，生成符合此風格的新聞稿。
            '''
        elif disaster_phase == '災後':
            training_prompt =  '''
            你是一個新聞稿撰寫助手，專門負責災害後的新聞稿撰寫。你的任務是學習並掌握過去災害前新聞稿的格式、寫作風格與口吻，並根據提供的資料，生成符合此風格的新聞稿。
            '''
            
        else:
            training_prompt = "無效。"

        request.session['disaster_phase'] = disaster_phase

        model_settings = setup_chatbot(xai_api_key, model_name, training_prompt, disaster_phase)
        if not model_settings:
            request.session['train_message'] = "模型初始化失敗！"
        else:
            request.session['model_settings'] = model_settings
            request.session['train_message'] = "模型初始化完成！"
            
    return redirect('ai_report')

def chat_function(message, model_settings):
    try:
        if not model_settings:
            return "請先進行模型初始化訓練"
            
        url = 'https://api.x.ai/v1/chat/completions'
        messages = model_settings['initial_messages'].copy()
        messages.append({"role": "user", "content": message})
        # messages.append({"role": "system", "content": model_settings['output_prompt']})
        messages.append({
            "role": "system",
            "content": f"請**嚴格**依照以下格式產生新聞稿：\n\n{model_settings['output_prompt']}"
        })

        
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
        disaster_phase = request.session.get('disaster_phase')  # 這裡從 session 中取得 disaster_phase

        print(disaster_phase) 
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
                    writer.writerow(['disaster_phase', 'input', 'output'])  # 寫入標題行
                writer.writerow([disaster_phase,input_text, output])
                
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
