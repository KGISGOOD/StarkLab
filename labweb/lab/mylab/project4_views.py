from django.shortcuts import render

def ai_report(request):
    return render(request, 'report.html')

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain_groq import ChatGroq

from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt 
def test_groq_api(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'testButton':
            # Groq API 的金鑰和 URL
            groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
            groq_api_key = "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" 

            # 設置請求標頭和數據
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {groq_api_key}"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "user",
                        "content": "Explain the importance of fast language models"
                    }
                ]
            }

            # 發送 POST 請求
            response = requests.post(groq_api_url, headers=headers, json=data)

            # 檢查回應
            if response.status_code == 200:
                return JsonResponse({'message': 'API 測試成功!'})
            else:
                return JsonResponse({'error': f'錯誤: {response.status_code}'}, status=response.status_code)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def setup_chatbot():
    # 測試groq api_key有無問題
    # groq 官網 https://console.groq.com/keys
    groq_api_key = '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'
    model_name = 'llama-3.1-8b-instant'
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model_name)

    # 測試 Groq API 連線
    groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {groq_api_key}"
    }
    data = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": "Explain the importance of fast language models"
            }
        ]
    }

    # 發送 POST 請求
    response = requests.post(groq_api_url, headers=headers, json=data)

    # 檢查回應
    if response.status_code == 200:
        print("成功!")
    else:
        print(f"錯誤: {response.status_code}")

    memory = ConversationBufferMemory(
        memory_key="history",
        return_messages=True
    )

    template = """
    以下是先前的對話記錄：
    {history}

    使用者的最新提問：
    {input}

    請根據上述內容，給出詳細、準確的回答。
    """
    prompt = PromptTemplate(input_variables=["history", "input"], template=template)

    chat_chain = ConversationChain(
        llm=groq_chat,
        memory=memory,
        prompt=prompt,
        verbose=True
    )

    return chat_chain


def train_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'trainButton':
            # 訓練模型初始化，不需要任何額外的處理
            response_message = "模型初始化完成！"
            return JsonResponse({'message': response_message})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def chat_function(message):
    try:
        chat_chain = setup_chatbot()
        response = chat_chain({"input": message})
        result = response["response"].encode('utf-8').decode('utf-8')
        return result  # 回傳結果
    except Exception as e:
        return f"發生錯誤: {str(e)}"

def generate_view(request):
    if request.method == 'POST':
        input_text = request.POST.get('inputText')
        if input_text:
            output = chat_function(input_text)
            return JsonResponse({'output': output})
        else:
            return JsonResponse({'error': '無效的輸入'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
