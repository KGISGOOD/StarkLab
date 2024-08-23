from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path('products/', views.products, name='products'),
    path('project1/', views.project1, name='project1'),
    path('project2/', views.project2, name='project2'),
    path('project3/', views.project3, name='project3'),
    path('project4/', views.project4, name='project4'),
    path('project5/', views.project5, name='project5'),
    path('project6/', views.project6, name='project6'),
]