from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('posts/', views.posts, name='posts'),
    path('<int:purpose_pk>/posts/', views.pur_posts, name='pur_posts'),
    path('posts/post_search/', views.post_search, name='post_search'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:post_pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_pk>/update/', views.post_update, name='post_update'),
    path('posts/<int:post_pk>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_pk>/comments/', views.com_p_create, name='com_p_create'),
    path('posts/<int:post_pk>/comments/<int:comment_pk>/delete/ ', views.com_p_delete, name='com_p_delete'),
]
