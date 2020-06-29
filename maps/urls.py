from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    path('', views.index, name='index'),
    path('present_movie/<int:movieCd>/', views.present, name='present'),
]