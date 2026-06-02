from django.urls import path
from django.http import HttpResponse
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-outfits/', views.get_outfits, name='get_outfits'), # 이미지칸 전용 통로 
    path('favicon.ico', lambda request: HttpResponse(status=204)),
]