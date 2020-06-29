from django.shortcuts import render
from datetime import date, timedelta
from decouple import config
import requests

# Create your views here.

def index(request):

    URL = 'https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json'
    key = config('KOBIS_KEY')
    yesterday = date.today() - timedelta(days=1)
    targetDt = yesterday.strftime("%Y%m%d")
    # print(targetDt)
    codes =[{"fullCd":"0105001","korNm":"서울시","engNm":""},{"fullCd":"0105002","korNm":"경기도","engNm":""},{"fullCd":"0105003","korNm":"강원도","engNm":""},{"fullCd":"0105004","korNm":"충청북도","engNm":""},{"fullCd":"0105005","korNm":"충청남도","engNm":""},{"fullCd":"0105006","korNm":"경상북도","engNm":""},{"fullCd":"0105007","korNm":"경상남도","engNm":""},{"fullCd":"0105008","korNm":"전라북도","engNm":""},{"fullCd":"0105009","korNm":"전라남도","engNm":""},{"fullCd":"0105010","korNm":"제주도","engNm":""},{"fullCd":"0105011","korNm":"부산시","engNm":""},{"fullCd":"0105012","korNm":"대구시","engNm":""},{"fullCd":"0105013","korNm":"대전시","engNm":""},{"fullCd":"0105014","korNm":"울산시","engNm":""},{"fullCd":"0105015","korNm":"인천시","engNm":""},{"fullCd":"0105016","korNm":"광주시","engNm":""},{"fullCd":"0105017","korNm":"세종시","engNm":""}]
    params = {
        'key': key,
        'targetDt': targetDt,
    }
    response = requests.get(URL, params=params).json()
    response = response['boxOfficeResult']['dailyBoxOfficeList']

    URL_N = 'https://openapi.naver.com/v1/search/movie.json'
    headers = {
            'X-Naver-Client-Id': config('Naver_Client_ID'),
            'X-Naver-Client-Secret': config('Naver_Client_Secret')
        }
    Cd_image = {}
    for res in response:  
        params = {
            'query': res['movieNm'],
            'display': 1,
        }
        result = requests.get(URL_N, headers=headers, params=params).json()
        Cd_image[res['movieCd']] = [{'link':result['items'][0]['image'], 'title':res['movieNm']}]
    # print(Cd_image)
    context = {
        'response': response,
        'Cd_image': Cd_image,
    }
    return render(request, 'maps/index.html', context)

def present(request, movieCd):
    URL = 'https://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json'
    key = config('KOBIS_KEY')
    params = {
        'key': key,
        'movieCd': movieCd,
    }
    movies = requests.get(URL, params=params).json()
    movie_info = movies['movieInfoResult']['movieInfo']
    movie_name = movie_info['movieNm']
    # print(movie_info)

    URL_N = 'https://openapi.naver.com/v1/search/movie.json'
    headers = {
        'X-Naver-Client-Id': config('Naver_Client_ID'),
        'X-Naver-Client-Secret': config('Naver_Client_Secret')
    }
    params = {
        'query': movie_name,
        'display': 1,
    }
    response = requests.get(URL_N, headers=headers, params=params).json()
    response = response['items'][0]
    # print(response)

    context = {
        'response': response,
        'movie_info': movie_info,
    }

    return render(request, 'maps/present_movie.html', context)

