from django.contrib import admin
from django.urls import path, re_path
from mylab import views, project1_views, project2_views, project3_views, project4_views, project5_views,project51_views
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
    path("project_stock/", views.project_stock, name="project_stock"),
    path("project_wra/", views.project_wra, name="project_wra"),
    path("project_wra_repoet/", views.project_wra_repoet, name="project_wra_repoet"),
    #新增基金優化機器人
    path('project_financial/', views.project_financial, name='project_financial'),
    path('financial_1/', views.financial_1, name='financial_1'),
    path('financial_2/', views.financial_2, name='financial_2'),
    path('financial_3/', views.financial_3, name='financial_3'),




    path("about/", views.about),
    path("contact/", views.contact),
    path("gallery/", views.gallery),
    path("products/", views.products),
    path("project1/", views.project1),
    path("project2/", views.project2),
    path('project3/', views.project3, name='project3'),  # 確保路徑設置正確
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
    
    # 啟動爬蟲
    path('api/news/', project3_views.crawler_first_stage, name='crawler_first_stage'),

    # ai 處理的api
    path('api/news/ai/', project3_views.news_ai, name='news_ai'),

    # 查看爬蟲的原始資料api
    path('api/news/sql/', project3_views.view_raw_news, name='view_raw_news'),

    path('api/run_crawler_and_ai/', project3_views.run_crawler_and_ai, name='run_crawler_and_ai'),



    # project4
    path("ai_report/", project4_views.ai_report, name='ai_report'),
    path('train/', project4_views.train_view, name='train_view'),
    path('test-api/', project4_views.test_groq_api, name='test_groq_api'),
    path('generate/', project4_views.generate_view, name='generate_view'),
    path('upload_file/', project4_views.upload_file, name='upload_file'),

    # project5
    # path('voice_search/', project5_views.voice_search, name='voice_search'),
    # path('ask_ai/', project5_views.ask_ai, name='ask_ai'),

    path("translate/", project51_views.translate, name='translate'),
    path('listen/', project51_views.listen, name='listen'),

    path('trans/', views.trans, name='trans'),
    path('translate/', views.translate_text_view, name='translate_text'),  # 注意函數名已更改
    path('history/', views.get_history, name='get_history'),

    path('alert/', views.emergency_alert),
]