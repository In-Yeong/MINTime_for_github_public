from django.contrib import admin
from django.urls import path, include
from movies import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('accounts/', include('accounts.urls')),
    path('movies/', include('movies.urls')),
    path('community/', include('community.urls')),
    path('managers/', include('managers.urls')),
    path('premium/', include('premium.urls')),
    path('kakaopay/', include('kakaopay.urls')),
    path('maps/', include('maps.urls')),

]
