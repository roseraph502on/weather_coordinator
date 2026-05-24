from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # <-- 루트 주소로 들어오면 views.py의 index 함수를 실행해라
]