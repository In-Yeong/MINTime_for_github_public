
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models.functions import Length
import requests
import json
import os
import sys
import urllib.request
import datetime

from .models import Movie, Review
from .forms import ReviewForm
from .genre_info import GENRE
from accounts.models import Premium

def search(request):
    qs = Movie.objects.all()

    q = request.GET.get('q', '') # GET request의 인자중에 q 값이 있으면 가져오고, 없으면 빈 문자열 넣기
    if q: 
        qs = qs.filter(title__icontains=q) # 제목에 q가 포함되어 있는 레코드만 필터링
    paginator = Paginator(qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    easterEgg1 = 'no'
    if q in ['박인영', '이종호']:
        easterEgg1 = 'yes1'
    elif q in ['강창현', '강해솔', '김성중', '김희정', '문예은', '박강민', '박도희', '배병준', '엄강우', '엄희관', '이동규', '이예림', '이지은', '전상혁', '정광수', '정무성', '정승희', '조규성', '최수병', '최재익', '한광욱', '허성수']:
        easterEgg1 = 'yes2'
    elif q in ['김도영']:
        easterEgg1 = 'yes3'

    # if easterEgg1 != 'no':
    #     qs = Movie.objects.all()
    #     paginator = Paginator(qs, 6)
    #     page_number = request.GET.get('page')
    #     page_obj = paginator.get_page(page_number)
    context = {
        'movies' : qs,
        'q' : q,
        'page_obj' : page_obj,
        'easterEgg1': easterEgg1,
        'search_page': True,
    }

    return render(request, 'movies/index.html', context)


def index(request):
    pick = request.GET.getlist('list_genre')
    pick_time = request.GET.getlist('list_time')
    pick_date = request.GET.getlist('list_date')
    movies = Movie.objects.all()


    premium = False
    try:
        is_premium = Premium.objects.filter(user=request.user)
    except:
        is_premium = False
    if is_premium:
        premium = True

    if pick:
        while pick:
            genre = pick.pop()
            movies = movies.filter(genres__icontains=genre)
    if pick_time:
        p_time = pick_time[0]
        
        if p_time == '59분 이하':
            movies = movies.annotate(length=Length('runtime')).filter(length=2).filter(runtime__lte=59)
        elif p_time == '60분~89분':
            movies = movies.annotate(length=Length('runtime')).filter(length=2).filter(runtime__lte=89).filter(runtime__gte=60)
        elif p_time == '90분~119분':
            movies = movies.annotate(length=Length('runtime')).filter(length=2).filter(runtime__gte=90)|movies.annotate(length=Length('runtime')).filter(length=3).filter(runtime__lte=119)
        else:
            movies = movies.annotate(length=Length('runtime')).filter(length=3).filter(runtime__gte=120)
    if pick_date:
        p_date = pick_date[0]
        
        if p_date == '8090년대':
            movies = movies.filter(release_date__lte=datetime.date(1999, 12, 31))
        elif p_date == '2000년대':
            movies = movies.filter(release_date__gte=datetime.date(2000, 1, 1)).filter(release_date__lte=datetime.date(2009, 12, 31))
        elif p_date == '2010이후':
            movies = movies.filter(release_date__gte=datetime.date(2010, 1, 1))



    paginator = Paginator(movies, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    genres = []
    times = ['59분 이하', '60분~89분', '90분~119분', '120분 이상']
    dates = ['8090년대', '2000년대', '2010이후']
    for gnr in GENRE:
        genres.append(gnr["name"])
    
    if len(movies) == 0:
        no_movie = 'True'
    else:
        no_movie = 'False'

    context = {
        'movies' : movies,
        'page_obj' : page_obj,
        'genres': genres,
        'times': times,
        'dates': dates,
        'no_movie': no_movie,
        'premium': premium,
    }

    return render(request, 'movies/index.html', context)

def my_pick(request):
    genres = request.get.getlist('list_genre')
    print(genres)
    return redirect('movies:index')

def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            return redirect('movies:detail', movie.pk)
    else:
        form = ReviewForm()
        reviews = Review.objects.filter(movie=movie)
        total = 0
        num = len(reviews) 
        for rev in reviews:
            total += rev.star
        if total != 0:
            avr = round(total / num, 1)
        else:
            avr = 0
    
    lock = 'false'
    for review in reviews:
        if request.user == review.user:
            lock = 'true'

    if movie.backdrop_path[0] == '/':
        backdrop_path = 'https://image.tmdb.org/t/p/w500'+ movie.backdrop_path
    else:
        backdrop_path = movie.backdrop_path

    context = {
        'form': form,
        'movie': movie,
        'reviews': reviews,
        'video': 'https://www.youtube.com/embed/' + movie.video,
        'avr': avr,
        'lock': lock,
        'backdrop_path': backdrop_path,
    }
    return render(request, 'movies/detail.html', context)


@login_required
def update_review(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if movie.backdrop_path[0] == '/':
        backdrop_path = 'https://image.tmdb.org/t/p/w500'+ movie.backdrop_path
    else:
        backdrop_path = movie.backdrop_path
    reviews = Review.objects.filter(movie=movie)
    review = get_object_or_404(Review, pk=review_pk)
    total = 0
    num = len(reviews) 
    for rev in reviews:
        total += rev.star
    if total != 0:
        avr = round(total / num, 1)
    else:
        avr = 0
    if request.user == review.user:
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.save()
                lock = 'true'
                updating = 'false'
                return redirect('movies:detail', movie.pk)
        else:
            form = ReviewForm(instance=review)
            lock = 'false'
            updating = 'true'
        context = {
            'form': form,
            'movie': movie,
            'reviews': reviews,
            'video': 'https://www.youtube.com/embed/' + movie.video,
            'avr': avr,
            'lock': lock,
            'backdrop_path': backdrop_path,
            'updating': updating,
        }
        return render(request, 'movies/detail.html', context)
    else:
        return redirect('movies:detail', movie.pk)

@login_required
def delete_review(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.user and request.method == 'POST':
        review.delete()
    return redirect('movies:detail', movie.pk)

@login_required
def like(request, movie_pk):
    user = request.user
    movies = get_object_or_404(Movie, pk=movie_pk)

    if movies.like_users.filter(pk=user.pk).exists():
        movies.like_users.remove(user)
        liked = False
    else:
        movies.like_users.add(user)
        liked = True



    context = {
        'liked' : liked,
        'count' : movies.like_users.count(),
    }

    return JsonResponse(context)

@login_required
def push(request):
    if request.user.is_staff:
        json_data = open('many_movies.json', 'r', encoding = 'utf-8')
        data1 = json.load(json_data)
        for data in data1:
            genre_list = []
            for genre in data["genres"]:
                genre_list.append(genre["name"])
            genres = ', '.join(genre_list)
            try:
                movie = Movie.objects.create(
                    movieid = data["id"],
                    title = data["title"],
                    genres = genres,
                    original_title = data["original_title"],
                    original_language = data["original_language"],
                    overview = data["overview"],
                    adult = data["adult"],
                    budget = data["budget"],
                    poster_path = data["poster_path"],
                    release_date = data["release_date"],
                    runtime = data["runtime"],
                    vote_average = data["vote_average"],
                    video = data["video"],
                    backdrop_path = data["backdrop_path"]
                )
            except:
                pass
        return render(request, 'movies/push.html')
    else:
        return render(request, 'managers/not_manager.html')


