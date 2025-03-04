from django.contrib import admin
from django.urls import path, re_path
from mylab import views, project1_views, project2_views, project3_views, project4_views, project5_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    # 實驗室

    
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("member/", views.member, name="member"),
    path("professor/", views.professor, name="professor"),
    path("project/", views.project, name="project"),
    path("project_linebot/", views.project_linebot, name="project_linebot"),



    path("about/", views.about),
    path("contact/", views.contact),
    path("gallery/", views.gallery),
    path("products/", views.products),
    path("project1/", views.project1),
    path("project2/", views.project2),
    path("project3/", views.project3),
    path("project4/", views.project4),
    path("project5/", views.project5),
    path("project6/", views.project6),

    # project1
    path('fund/', project1_views.fund, name='fund'),
    path('bonds/', project1_views.bonds, name='bonds'),
    path('stock/', project1_views.stock, name='stock'),
    path('etf/', project1_views.etf, name='etf'),
    path('report/', project1_views.Report, name='report'),

    # project2 基本面爬蟲
    re_path(r'^callback/$', project2_views.callback),
    path('query/', project2_views.query_report, name='query_report'),
    path('update_reports/', project2_views.update_reports, name='update_reports'),

    # project3
    path("news", lambda request: redirect("/news/")),  # 根路徑導向 /news/
    path("news/", project3_views.news_view, name='news_list'),  # 新增新聞列表視圖
    path("news/create/", project3_views.news_create, name='news_create'),  # 新增新聞創建視圖 (POST)
    path("update/", project3_views.update_news, name='update_news'),  # 新增更新爬蟲的視圖
    # 新增新聞 API 端點 ，讀取（GET）新聞資料 。對應的視圖函數：@require_GET  
    # path('api/news/', project3_views.news_api, name='news_api'),
    # path('api/news/sql/', project3_views.news_api_sql, name='news_api_sql'),
    # 更新特定新聞每日記錄的 API 端點。對應的視圖函數：@csrf_exempt
    path('api/news/<int:news_id>/daily-records/', project3_views.update_daily_records, name='update_daily_records'),
        # 新增爬蟲執行的 URL 路徑(啟動爬蟲用的)
    path('run_crawler/', views.run_crawler, name='run_crawler'),
   
    # 測試爬蟲執行的 URL 路徑(啟動爬蟲用的)
    path('api/news/', project3_views.crawler_first_stage, name='crawler_first_stage'),
    # # 查看爬蟲的原始資料api
    path('api/news/sql/', project3_views.view_raw_news, name='view_raw_news'),



    # project4
    path("ai_report/", project4_views.ai_report, name='ai_report'),
    path('train/', project4_views.train_view, name='train_view'),
    path('test-api/', project4_views.test_groq_api, name='test_groq_api'),
    path('generate/', project4_views.generate_view, name='generate_view'),
    path('upload_file/', project4_views.upload_file, name='upload_file'),

    # project5
    # path('voice_search/', project5_views.voice_search, name='voice_search'),
    # path('ask_ai/', project5_views.ask_ai, name='ask_ai'),



]