import os
import sys

# 取得 lab 資料夾的絕對路徑
current_file = os.path.abspath(__file__)
lab_dir = os.path.dirname(os.path.dirname(current_file))  # /Users/.../labweb/lab

# 設定 PYTHONPATH
sys.path.append(lab_dir)

# 強制設定執行環境的當前工作目錄
os.chdir(lab_dir)

# 印出目前的工作目錄，確認所有檔案都會寫在這裡
# print(f"📁 當前工作目錄：{os.getcwd()}")
# print("📌 所有產出的檔案將會儲存在此資料夾底下\n")

# 設定 Django 環境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab.settings")
import django
django.setup()

# 匯入目標模組
from mylab.project3_views import crawler_first_stage, news_ai
from django.test import RequestFactory

def main():
    print("🚀 開始模擬呼叫 crawler + AI")
    
    factory = RequestFactory()
    request = factory.get('/fake-url')

    # print("\n📡 呼叫 crawler_first_stage()...")
    res1 = crawler_first_stage(request)
    print("📦 Crawler Response:", res1.status_code)
    print(res1.content.decode())

    # print("\n🧠 呼叫 news_ai()...")
    res2 = news_ai(request)
    print("🤖 AI Response:", res2.status_code)
    print(res2.content.decode())

    print("\n✅ 測試完成，請至上方列出的資料夾中確認輸出的檔案。")

if __name__ == "__main__":
    main()