from django.shortcuts import render, redirect, get_object_or_404
from movies.models import Movie
from django.core.paginator import Paginator
from django.http import JsonResponse
from decouple import config
import requests

from django.contrib.auth import get_user_model
from .forms import MovieForm
from django.contrib.auth.forms import UserChangeForm

# Create your views here.

def index(request):
    if request.user.is_staff:  
        return render(request, 'managers/index.html')
    else:
        return render(request, 'managers/not_manager.html')

def movies_search(request):
    qs = Movie.objects.all()

    q = request.GET.get('q', '')
    if q: 
        qs = qs.filter(title__icontains=q)
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'movies' : qs,
        'q' : q,
        'page_obj' : page_obj,
    }

    return render(request, 'managers/movies.html', context)


def movies(request):
    if request.user.is_staff:
        movies = Movie.objects.all()
        paginator = Paginator(movies, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'movies' : movies,
            'page_obj' : page_obj,
        }

        return render(request, 'managers/movies.html', context)
    else:
        return render(request, 'managers/not_manager.html')

def movie_create(request):
    if request.user.is_staff:
        if request.method == 'POST':
            form = MovieForm(request.POST)
            if form.is_valid():
                new_movie = form.save(commit=False)
                latest = Movie.objects.latest('id')
                latest_int = int(latest.movieid[5:])
                new_movie.movieid = 'movie{}'.format(latest_int+1)
                if len(new_movie.video) > 11:
                    video_adr = new_movie.video.strip()[-11:]
                    new_movie.video = video_adr
                genres = ''
                for g in new_movie.genres:
                    if g not in "[']":
                        genres += g
                new_movie.genres = genres
                try:
                    new_movie.poster_path = request.COOKIES['selected_img']
                except:
                    new_movie.poster_path = ''
                try:

                    new_movie.backdrop_path = request.COOKIES['selected_back']
                except:
                    pass
                new_movie.save()
                return redirect('movies:detail', new_movie.pk)
        else:
            form = MovieForm()
        context = {
            'form': form,
        }
        return render(request, 'managers/movie_create.html', context)
    else:
        return render(request, 'managers/not_manager.html')       

def movie_update(request, movie_pk):
    if request.user.is_staff:
        movie = get_object_or_404(Movie, pk=movie_pk)
        if request.method == 'POST':
            form = MovieForm(request.POST, instance=movie)
            if form.is_valid():
                new_movie = form.save(commit=False)
                if len(new_movie.video) > 11:
                    video_adr = new_movie.video.strip()[-11:]
                    new_movie.video = video_adr
                genres = ''
                for g in new_movie.genres:
                    if g not in "[']":
                        genres += g
                new_movie.genres = genres
                try:
                    if len(request.COOKIES['selected_img']) > 3:
                        new_movie.poster_path = request.COOKIES['selected_img']
                except:
                    pass
                try:
                    if len(request.COOKIES['selected_back']) > 3:
                        new_movie.backdrop_path = request.COOKIES['selected_back']
                except:
                    pass
                new_movie.save()
                return redirect('movies:detail', movie.pk)
        else:
            form = MovieForm(instance=movie)
            genre_list = list(movie.genres.split(', '))
        context = {
            'form': form,
            'genres': genre_list,
        }
        return render(request, 'managers/movie_update.html', context)
    else:
        return render(request, 'managers/not_manager.html')

def movie_delete(request, movie_pk):
    if request.user.is_staff:
        movie = get_object_or_404(Movie, pk=movie_pk)
        movie.delete()
        return redirect('managers:movies')
    else:
        return render(request, 'managers/not_manager.html')


def users(request):
    if request.user.is_staff:  

        users = get_user_model().objects.all()
        paginator = Paginator(users, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'users' : users,
            'page_obj' : page_obj,
        }

        return render(request, 'managers/users.html', context)
    else:
        return render(request, 'managers/not_manager.html')


def active(request, user_pk):
    if request.user.is_staff:  
        user = get_object_or_404(get_user_model(), pk=user_pk)
        if user.is_active:
            user.is_active = False
            user.save()
        else:
            user.is_active = True
            user.save()
        context = {
            'is_active' : user.is_active,
        }
        return JsonResponse(context)
    else:
        return render(request, 'managers/not_manager.html')

def staff(request, user_pk):
    if request.user.is_staff:
        user = get_object_or_404(get_user_model(), pk=user_pk)
        if user.is_staff:
            user.is_staff = False
            user.save()
        else:
            user.is_staff = True
            user.save()
        context = {
            'is_staff' : user.is_staff,
        }
        return JsonResponse(context)
    else:
        return render(request, 'managers/not_manager.html')

def image_search(request, title):
    URL = 'https://dapi.kakao.com/v2/search/image'
    headers = {
        "Authorization": "KakaoAK " + config('KPAY_KEY'),
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "query": '영화 '+title+' 포스터',
        "page": 1,

    }

    res = requests.get(URL, headers=headers, params=params).json()
    image_list = []
    for r in res['documents']:
        if r['image_url'][-4:] == '.jpg':
            image_list.append(r['image_url'])

    context = {
        'image_list': image_list,
        'kind': 'poster',
    }
    return render(request, 'managers/image_search.html', context)


def image_search_back(request, title):
    URL = 'https://dapi.kakao.com/v2/search/image'
    headers = {
        "Authorization": "KakaoAK " + config('KPAY_KEY'),
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "query": '영화 '+title,
        "page": 1,

    }

    res = requests.get(URL, headers=headers, params=params).json()
    image_list = []
    for r in res['documents']:
        if r['image_url'][-4:] == '.jpg':
            image_list.append(r['image_url'])

    context = {
        'image_list': image_list,
        'kind': 'back',
    }
    return render(request, 'managers/image_search.html', context)
