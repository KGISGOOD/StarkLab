from django.contrib import admin
from django.urls import path, re_path
from mylab import views, project1_views, project2_views, project3_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    # 實驗室
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
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
    path('api/news/', project3_views.news_api, name='news_api'),
    path('api/news/<int:news_id>/daily-records/', project3_views.update_daily_records, name='update_daily_records'),

    # 新增爬蟲執行的 URL 路徑
    path('run_crawler/', views.run_crawler, name='run_crawler'),
]