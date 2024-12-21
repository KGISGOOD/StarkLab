from django.shortcuts import render
from django.http import JsonResponse
import requests
import logging
import time

# 現有的視圖
def home(request):
    return render(request, 'index.html')

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


# 新增爬蟲執行的視圖
def run_crawler(request):
    logging.info("爬蟲開始執行...")

    # 先檢查伺服器是否已經啟動
    def check_server():
        try:
            response = requests.get("http://127.0.0.1:8000/api/news/")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    # 等待伺服器啟動並確保可以連接
    while not check_server():
        logging.info("伺服器尚未啟動，等待 3 秒鐘後再試...")
        time.sleep(3)  # 等待 3 秒後重試

    logging.info("伺服器已啟動，開始執行爬蟲...")

    try:
        response = requests.get("http://127.0.0.1:8000/api/news/")
        if response.status_code == 200:
            logging.info("爬蟲完成！數據已保存。")
            return JsonResponse({"message": "爬蟲執行完成！數據已保存。"})
        else:
            logging.error(f"爬蟲失敗，狀態碼：{response.status_code}")
            return JsonResponse({"message": f"爬蟲失敗，狀態碼：{response.status_code}"}, status=500)
    except Exception as e:
        logging.error(f"爬蟲發生錯誤：{e}")
        return JsonResponse({"message": f"爬蟲發生錯誤：{e}"}, status=500)