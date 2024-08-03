from django.urls import path
from .views import add_person, person_list, index, achievements, team

urlpatterns = [
    path('', index, name='index'),  # 主頁
    path('achievements/', achievements, name='achievements'),  # 戰績頁
    path('team/', team, name='team'),  # 人員頁
    path('add/', add_person, name='add_person'),  # 新增人員頁
    path('persons/', person_list, name='person_list'),  # 人員列表頁
]
