# import os
# import sys

# # 設置 PYTHONPATH，讓 Python 知道如何找到 `lab` package
# sys.path.append('/Users/kg/Desktop/StarkLab/labweb/lab')

# # 設置 DJANGO_SETTINGS_MODULE，確保 Django 設定被正確載入
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab.settings")

# import django
# django.setup()

import os
import sys

# 動態取得 lab 專案的根目錄（假設這支檔案在 lab/mylab 底下）
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file))  # 回到 lab/
sys.path.append(project_root)  # 把 lab/ 加進 Python 模組搜尋路徑中

# 設定 Django 環境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab.settings")
import django
django.setup()


from mylab.project3_views import crawler_first_stage, news_ai
from django.test import RequestFactory

def main():
    print("🚀 開始模擬呼叫 crawler + AI")
    factory = RequestFactory() # 用於模擬 HTTP 請求
    request = factory.get('/fake-url') # 模擬 GET 請求

    res1 = crawler_first_stage(request) # 啟動 crawler_first_stage(request)
    print("📦 Crawler Response:", res1.status_code) # 打印爬蟲的回應碼
    print(res1.content.decode()) # 打印爬蟲的回應內容

    res2 = news_ai(request) # 啟動 news_ai(request)
    print("🤖 AI Response:", res2.status_code) # 打印 AI 的回應碼
    print(res2.content.decode()) # 打印 AI 的回應內容

if __name__ == "__main__":
    main()


