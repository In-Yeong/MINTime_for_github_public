from django.urls import path
from . import views

app_name = 'managers'

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.movies, name='movies'),
    path('movies/create/', views.movie_create, name='movie_create'),
    path('movies/<int:movie_pk>/', views.movie_update, name='movie_update'),
    path('movies/<int:movie_pk>/delete/', views.movie_delete, name='movie_delete'),
    path('movies/image/<str:title>', views.image_search, name='image_search'),
    path('movies/image/back/<str:title>', views.image_search_back, name='image_search_back'),
    path('users/', views.users, name='users'),
    path('users/<int:user_pk>/active/', views.active, name='active'),
    path('users/<int:user_pk>/staff/', views.staff, name='staff'),
    path('movies/movies_search/', views.movies_search, name='movies_search'),
]