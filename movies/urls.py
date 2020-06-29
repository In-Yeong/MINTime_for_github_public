from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('<int:movie_pk>/', views.detail, name='detail'),
    path('<int:movie_pk>/like/', views.like, name = 'like'),
    path('<int:movie_pk>/<int:review_pk>/delete/', views.delete_review, name='delete_review'),
    path('<int:movie_pk>/<int:review_pk>/update/', views.update_review, name='update_review'),
    path('push_movie/', views.push, name='push'),

]
