from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import logging
from .project3_views import crawler_first_stage  # 導入原本的爬蟲主函數


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
