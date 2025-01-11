import json
import pandas as pd
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings

def voice_search(request):
    return render(request, 'voice_search.html')

@csrf_exempt
def ask_ai(request):
    if request.method == 'POST':
        question = request.POST.get('question', '')
        
        # 更新 CSV 檔案的路徑
        csv_path = os.path.join(settings.BASE_DIR, 'mylab', 'data', 'voice_search.csv')
        df = pd.read_csv(csv_path)
        
        # 準備發送給 Groq 的訊息
        messages = [
            {"role": "system", "content": "你是一個只能回答關於特定主題的 AI 助手。如果問題超出範圍，請回答「抱歉，這個問題超出我的回答範圍。」"},
            {"role": "user", "content": question}
        ]
        
        # Groq API 設定
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer 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"
        }
        
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages
        }
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                answer = ai_response['choices'][0]['message']['content']
            else:
                answer = "抱歉，發生錯誤，請稍後再試。"
                
        except Exception as e:
            answer = f"發生錯誤：{str(e)}"
        
        return JsonResponse({'answer': answer})
    
    return JsonResponse({'error': '只接受 POST 請求'})

