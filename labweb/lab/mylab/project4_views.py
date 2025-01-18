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
from langchain_groq import ChatGroq

from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt

groq_api_key = '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'
model_name = 'llama-3.3-70b-versatile'

# 測試 Groq API
@csrf_exempt 
def test_groq_api(request):
    if request.method == 'POST':
        print("訪問了 test_groq_api")  # 添加調試信息
        action = request.POST.get('action')
        if action == 'testButton':
            try:
                groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
                
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
                    request.session['test_message'] = 'API 測試成功!'
                else:
                    request.session['test_message'] = '錯誤'
            except Exception as e:
                request.session['test_message'] = f'錯誤：{str(e)}'
    return redirect('ai_report')


def setup_chatbot():
    try:
        groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model_name)
        
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
        如果是中文問題，請用中文回答。
        """
        prompt = PromptTemplate(input_variables=["history", "input"], template=template)

        chat_chain = ConversationChain(
            llm=groq_chat,
            memory=memory,
            prompt=prompt,
            verbose=True
        )

        return chat_chain
    except Exception as e:
        print(f"設置聊天機器人時發生錯誤: {str(e)}")
        return None

def train_view(request):
    if request.method == 'POST':
        print("訪問了 train_view")  # 添加調試信息
        try:
            # 清除舊的對話歷史
            request.session['conversation_history'] = []
            
            # 初始化 chatbot
            chat_chain = setup_chatbot()  # 不再傳入 request
            if chat_chain is None:
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
