from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/<str:username>/<int:pur_pk>/', views.profile, name='profile'),
    path('oauth/', views.oauth, name='oauth'),
    path('kakao_login/', views.kakao_login, name='kakao_login'),
    path('kakao_logout/', views.kakao_logout, name='kakao_logout'),
    path('kakao_unlink/', views.kakao_unlink, name='kakao_unlink'),
    path('update_username/', views.update_username, name='update_username'),
]