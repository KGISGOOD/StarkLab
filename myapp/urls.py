from django.urls import path
from .views import index, about, contact, gallery, products,project1,project2,project3,project4,project5,project6

urlpatterns = [
    path('', index, name='index'),  # 主頁
    path('about/', about, name='about'),  # 戰績頁
    path('contact/', contact, name='contact'),  # 人員頁
    path('gallery/', gallery, name='gallery'),  # 新增人員頁
    path('products/', products, name='products'),  # 人員列表頁
    path('project1/', project1, name='project1'),
    path('project2/', project2, name='project2'),
    path('project3/', project3, name='project3'),
    path('project4/', project4, name='project4'),
    path('project5/', project5, name='project5'),
    path('project6/', project6, name='project6'),
]
