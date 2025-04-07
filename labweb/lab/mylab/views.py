from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import logging
from .project3_views import crawler_first_stage  # 導入原本的爬蟲主函數
from django.views.decorators.csrf import csrf_exempt  
from .translation import translate_text, save_conversation, get_conversation, clear_conversation 


logger = logging.getLogger(__name__)

# 現有的視圖
# def home(request):
#     return render(request, 'index.html')

def home(request):
    return render(request, 'stark_lab_home.html')



def member(request):
    return render(request, 'stark_lab_member.html')

def professor(request):
    return render(request, 'stark_lab_professor.html')

def project(request):
    return render(request, 'stark_lab_project.html')

def project_linebot(request):
    return render(request, 'stark_lab_project_linebot.html')

def project_stock(request):
    return render(request, 'stark_lab_project_stock.html')

def project_wra(request):
    return render(request, 'stark_lab_project_wra.html')

def project_wra_repoet(request):
    return render(request, 'stark_lab_project_wra_report.html')

def project_financial(request):
    return render(request, 'stark_lab_project_financial.html')

def financial_1(request):
    return render(request, 'financial_1.html')

def financial_2(request):
    return render(request, 'financial_2.html')




def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def gallery(request):
    return render(request, 'gallery.html')

def products(request):
    return render(request, 'products.html')

def project1(request):
    return render(request, 'project1.html')

def project2(request):
    return render(request, 'project2.html')

def project3(request):
    return render(request, 'project3.html')

def project4(request):
    return render(request, 'project4.html')

def project5(request):
    return render(request, 'project5.html')

def project6(request):
    return render(request, 'project6.html')



# 第一階段爬蟲
def crawler_first_stage(request):
    # 用來「顯示目前執行狀況」或「回傳執行結果」
    data = {
        "status": "success",
        "message": "爬蟲執行完畢，已抓取資料"
    }
    return JsonResponse(data)

# 第二階段 AI 處理
def news_ai(request):
    data = {
        "status": "success",
        "message": "AI 處理完成，結果返回"
    }
    return JsonResponse(data)

# 啟動爬蟲和 AI 處理的 API
def run_crawler_and_ai(request):
    # 執行爬蟲階段
    crawler_response = crawler_first_stage(request)
    # 檢查爬蟲是否執行成功
    if crawler_response.status_code == 200:
        # 若爬蟲成功，再執行 AI 處理
        ai_response = news_ai(request)
        return ai_response  # 返回 AI 處理結果
    else:
        # 若爬蟲失敗，返回錯誤訊息
        return JsonResponse({
            "status": "error",
            "message": "爬蟲執行失敗，無法啟動 AI 處理"
        }, status=500)


def trans(request):  
    return render(request, 'stark_lab_trans.html')  

# 自動翻譯器
@csrf_exempt  
# 翻譯文字的函數
def translate_text_view(request): 
    if request.method == 'POST':  
        text = request.POST.get('text', '')  # 從 POST 數據中獲取 'text'，若無則預設為空字串
        target_lang = request.POST.get('target_lang', 'en')  # 從 POST 數據中獲取 'target_lang'，預設為 'en'（英文）
        
        try:  
            translated_text = translate_text(text, target_lang)  # 調用 translate_text 函數進行翻譯
            save_conversation(request.session, text, target_lang, translated_text)  # 儲存對話到 session 中
            return JsonResponse({  
                'status': 'ok',  
                'translated_text': translated_text  # 返回翻譯後的文字
            })
        except Exception as e: 
            return JsonResponse({  
                'status': 'fail',  
                'error': str(e)  # 返回錯誤訊息
            }, status=500) 
    return JsonResponse({ 
        'status': 'fail',  
        'error': 'Only POST method is allowed.'  # 錯誤訊息說明只允許 POST 方法
    }, status=400) 

@csrf_exempt  
# 獲取對話歷史的函數
def get_history(request):  
    if request.method == 'GET': 
        conversation = get_conversation(request.session)  # 從 session 中獲取對話歷史
        return JsonResponse({ 
            'status': 'ok',  
            'conversation': conversation  # 返回對話歷史數據
        })
    elif request.method == 'DELETE':  # 檢查請求方法是否為 DELETE
        clear_conversation(request.session)  # 清除 session 中的對話歷史
        return JsonResponse({  
            'status': 'ok', 
            'message': 'History cleared successfully.'  
        })
    return JsonResponse({  
        'status': 'fail',  
        'error': 'Only GET or DELETE method is allowed.' 
    }, status=400) 