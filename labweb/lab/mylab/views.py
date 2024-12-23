from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import logging
from .project3_views import main  # 導入原本的爬蟲主函數

logger = logging.getLogger(__name__)

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
    """
    執行爬蟲的 API 端點
    訪問 /run_crawler/ 時會觸發爬蟲程序
    """
    # try:
    #     logger.info("開始執行爬蟲...")
    #     main()  # 執行爬蟲主程序
    #     logger.info("爬蟲執行完成")
    #     return JsonResponse({
    #         "message": "爬蟲執行成功！"
    #     })
    # except Exception as e:
    #     logger.error(f"爬蟲執行失敗：{str(e)}")
    #     return JsonResponse({
    #         "message": f"爬蟲執行失敗：{str(e)}"
    #     }, status=500)

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>爬蟲狀態</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                text-align: center;
            }
            #status {
                font-size: 18px;
                margin: 20px;
                padding: 10px;
            }
            .running {
                color: blue;
            }
            .success {
                color: green;
            }
            .error {
                color: red;
            }
        </style>
    </head>
    <body>
        <div id="status" class="running">正在執行爬蟲...</div>
        
        <script>
            async function runCrawler() {
                const statusDiv = document.getElementById('status');
                try {
                    statusDiv.className = 'running';
                    statusDiv.textContent = '正在執行爬蟲...';
                    
                    const response = await fetch('/update/');
                    const data = await response.json();
                    
                    if (data.message.includes('成功')) {
                        statusDiv.className = 'success';
                        statusDiv.textContent = data.message;
                    } else {
                        throw new Error(data.message);
                    }
                } catch (error) {
                    statusDiv.className = 'error';
                    statusDiv.textContent = '爬蟲執行失敗：' + error.message;
                }
            }

            // 頁面載入後立即執行爬蟲
            window.onload = runCrawler;
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content)