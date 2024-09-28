"""
URL configuration for water project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from mywater import views  # 確保 import views 正確

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: redirect("/news/")),  # 根路徑導向 /news/
    path("news/", views.news_view, name='news_list'),  # 新增新聞列表視圖
    path("news/create/", views.news_create, name='news_create'),  # 新增新聞創建視圖 (POST)
    path("update/", views.update_news, name='update_news'),  # 新增更新爬蟲的視圖
    path('api/news/', views.news_api, name='news_api'),

]

