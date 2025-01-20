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
    prompt = """
    
    """
    
    url = 'https://api.x.ai/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {xai_api_key}'
    }

    messages = [
        {"role": "system", "content": "你是一個負責寫新聞稿的員工"},
        {"role": "user", "content": prompt}
    ]

    data = {
        "messages": messages,
        "model": "grok-beta",
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

def train_view(request):
    if request.method == 'POST':
        print("訪問了 train_view")  # 添加調試信息
        try:
            # 初始化 chatbot
            response = setup_chatbot(xai_api_key, model_name)
            if not response:
                request.session['train_message'] = "模型初始化失敗！"
            else:
                request.session['train_message'] = "模型初始化完成！"
                
        except Exception as e:
            print(f"初始化錯誤: {str(e)}")  # 添加錯誤日誌
            request.session['train_message'] = f"初始化過程發生錯誤：{str(e)}"
            
    return redirect('ai_report')  # 重定向回主頁面

def chat_function(message):
    try:
        chat_chain = setup_chatbot()
        if chat_chain is None:
            return "聊天機器人初始化失敗"
            
        response = chat_chain({"input": message})
        result = response["response"]
        return result
    except Exception as e:
        print(f"聊天過程中發生錯誤: {str(e)}")
        return f"發生錯誤: {str(e)}"

def generate_view(request):
    if request.method == 'POST':
        input_text = request.POST.get('inputText')
        if input_text:
            output = chat_function(input_text)
            # 將輸入和輸出存入 session
            request.session['input_text'] = input_text
            request.session['output_text'] = output
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
