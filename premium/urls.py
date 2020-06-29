from django.urls import path
from . import views

app_name = 'premium'

urlpatterns = [
    path('event/', views.event, name='event'),
]