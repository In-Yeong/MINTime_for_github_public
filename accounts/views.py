from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from community.models import Post, Comment_P
from movies.models import Movie, Review
from .models import Premium
from decouple import config
from .my_settings import TMDb_URL
from django.http import HttpResponse 
from .forms import CustomUserNameChangeForm
from .genre_convert import GENRE
import requests


def signup(request):
    if request.user.is_authenticated:
        return redirect('movies:index')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('movies:index')
    else:
        form = UserCreationForm()

    context = {
        'form' : form
    }
    return render(request, 'accounts/signup.html', context)

@login_required
def update_username(request):
    if request.method == 'POST':
        name_change_from = CustomUserNameChangeForm(request.POST, instance=request.user)
        if name_change_from.is_valid():
            name_change_from.save()
            return redirect('accounts:profile', request.user.username, 0)
    
    else:
	    name_change_from = CustomUserNameChangeForm(instance = request.user)

    context = {
        'name_change_from':name_change_from
    }
    return render(request, 'accounts/update_username.html', context)

def login(request):
    if request.user.is_authenticated:
        return redirect('movies:index')
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('movies:index')
    else:
        form = AuthenticationForm()
    context = {
        'form' : form
    }
    return render(request, 'accounts/login.html', context)

def oauth(request):
    code = request.GET.get('code', None)
    # print('이것이 code = ' + str(code))
    client_id = request.session.get('client_id')
    redirect_uri = request.session.get('redirect_uri')

    access_token_request_uri = "https://kauth.kakao.com/oauth/token?grant_type=authorization_code&"
    access_token_request_uri += "client_id=" + client_id
    access_token_request_uri += "&redirect_uri=" + redirect_uri
    access_token_request_uri += "&code=" + code

    access_token_request_uri_data = requests.get(access_token_request_uri)
    json_data = access_token_request_uri_data.json()
    access_token = json_data['access_token']
    # print('이것은 access_token = ' + str(access_token))

    url = 'https://kapi.kakao.com/v2/user/me'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/x-www-form-urlencoded; charset-utf-8',
    }
    kakao_response = requests.get(url, headers=headers).json()
    # print('이것이 결과 = ' + str(kakao_response))

    User = get_user_model()

    try:
        email = kakao_response['kakao_account']['email']
    except:
        email = 'kakao_account' + str(kakao_response['id'])

    if User.objects.filter(email = email).exists():
        user = User.objects.get(email = email)
        
        auth_login(request, user)
        return redirect('movies:index')
        
    
    User(
        username = kakao_response['properties']['nickname'],
        last_name = kakao_response['id'],
        email = email,
    ).save()
    user = User.objects.get(email = email)
    
    auth_login(request, user)
    return redirect('movies:index')
    

def kakao_login(request):
    login_request_uri = 'https://kauth.kakao.com/oauth/authorize?'
    client_id = config('KAKAO_LOGIN_client_id')
    redirect_uri = 'http://13.124.169.106/accounts/oauth'
    login_request_uri += 'client_id=' + client_id
    login_request_uri += '&redirect_uri=' + redirect_uri
    login_request_uri += '&response_type=code'

    request.session['client_id'] = client_id
    request.session['redirect_uri'] = redirect_uri

    return redirect(login_request_uri)

def kakao_logout(request):
    logout_request_url = 'https://kapi.kakao.com/v1/user/logout'
    User = get_user_model()
    user = User.objects.get(id = request.user.id)
    headers = {
        'Authorization': config('ADMIN_KEY'),
    }
    params = {
        'Authorization': config('ADMIN_KEY'),
        'target_id': user.last_name,
        'target_id_type': "user_id"
    }
    result = requests.post(logout_request_url, headers=headers, params=params).json()
    # print(result)
    auth_logout(request)
    return redirect('movies:index')

def kakao_unlink(request):
    unlink_request_url = 'https://kapi.kakao.com/v1/user/unlink'
    User = get_user_model()
    user = User.objects.get(email = request.user.email)
    # print(ADMIN_KEY)
    headers = {
        'Authorization': config('ADMIN_KEY'),
    }
    params = {
        'Authorization': config('ADMIN_KEY'),
        'target_id': user.last_name,
        'target_id_type': "user_id",
    }
    result = requests.post(unlink_request_url, headers=headers, params=params).json()
    # print(result)
    auth_logout(request)
    user.delete()
    return redirect('movies:index')


@login_required
def logout(request):
    auth_logout(request)
    return redirect('movies:index')

@login_required
def profile(request, username, pur_pk):
    person = get_object_or_404(get_user_model(), username=username)
    if pur_pk not in  [0,1,2,3,4]:
        pur_pk = 1
    like_movies = person.like_movies.all()
    like_genres = {}
    for like_movie in like_movies:
        l_gnr = list(map(str, like_movie.genres.split(', ')))
        for gnr in l_gnr:
            if gnr in like_genres:
                like_genres[gnr] += 1
            else:
                like_genres[gnr] = 1
    if like_genres:
        def f(x):
            return x[1]

        like_genres = sorted(like_genres.items(), key=f)

    r_gs = []
    for l_g in like_genres:
        r_gs.append(l_g[0])

    if len(like_genres) >= 2:
        like_genres = like_genres[len(like_genres)-2:]

    recom_genres = []
    for like_genre in like_genres:
        recom_genres.append(like_genre[0])
    
    like_movie_ids = []
    for like_movie in like_movies:
        like_movie_ids.append(like_movie.id)
    
    if recom_genres:
        recom_movies = Movie.objects.all()

        while recom_genres:
            genre = recom_genres.pop()
            recom_movies = recom_movies.filter(genres__icontains=genre)
        
        while like_movie_ids:
            like_movie_id = like_movie_ids.pop()
            recom_movies = recom_movies.exclude(id=like_movie_id)
        
        paginator = Paginator(recom_movies, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if len(recom_movies) == 0:
            situation_code = 0
        else:
            situation_code = 1

    else:
        recom_movies = {}
        page_obj = {}
        situation_code = 0

    premium = False
    is_premium = Premium.objects.filter(user=person)
    if is_premium:
        premium = True

        l_gs = []
        for r_g in r_gs:
            if GENRE[r_g] not in l_gs:
                l_gs.append(GENRE[r_g])

        params = {
            'api_key': config('TMDb_key'),
            'language': 'ko-KR',
            'region': 'KR',
        }
        response = requests.get(TMDb_URL, params=params).json()
        response = response['results']
        recom_response = []
        upcom_response = []
        for res in response:
            for gnr in res['genre_ids']:
                if str(gnr) in l_gs:
                    recom_response.append(res)
                    break
                else:
                    upcom_response.append(res)
                    break
    else:
        recom_response = []
        upcom_response = []
    # print(recom_response)
    # print('-------------')
    # print(upcom_response)

    posts = Post.objects.filter(user=person).order_by('-id')
    paginator1 = Paginator(posts, 10)
    page_number1 = request.GET.get('page')
    page_obj1 = paginator1.get_page(page_number1)
    comments = Comment_P.objects.filter(user=person).order_by('-id')
    paginator2 = Paginator(comments, 10)
    page_number2 = request.GET.get('page')
    page_obj2 = paginator2.get_page(page_number2)
    movies = Movie.objects.filter(like_users=person)
    paginator3 = Paginator(movies, 10)
    page_number3 = request.GET.get('page')
    page_obj3 = paginator3.get_page(page_number3)
    reviews = Review.objects.filter(user=person).order_by('-id')
    paginator4 = Paginator(reviews, 10)
    page_number4 = request.GET.get('page')
    page_obj4 = paginator4.get_page(page_number4)

    context = {
        'person':person,
        'posts':posts,
        'page_obj1': page_obj1,
        'comments':comments,
        'page_obj2': page_obj2,
        'movies':movies,
        'page_obj3': page_obj3,
        'reviews':reviews,
        'page_obj4': page_obj4,
        'pur_pk': pur_pk,
        'premium': premium,
        'like_movies': like_movies,
        'like_genres': like_genres,
        'recom_movies': recom_movies,
        'page_obj': page_obj,
        'like_movie_ids': like_movie_ids,
        'situation_code': situation_code,
        'recom_response': recom_response,
        'upcom_response': upcom_response,
    }
    return render(request, 'accounts/profile.html', context)
