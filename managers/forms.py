from django import forms
from movies.models import Movie
import datetime

now = datetime.datetime.now()

class MovieForm(forms.ModelForm):

    title = forms.CharField(
        label='제목'
    )

    original_title = forms.CharField(
        label='원 제목'
    )

    original_language = forms.CharField(
        max_length= 2,
        label='언어',
        widget=forms.TextInput(
            attrs={
                'style': 'width: 10rem;'
            }
        )
    )

    adult = forms.BooleanField(
        label='성인',
        required=False,
    )


    GENRE_CHOICES = [

        ('액션', '액션'),
        ('모험', '모험'),
        ('애니메이션', '애니메이션'),
        ('코미디', '코미디'),
        ('범죄', '범죄'),
        ('다큐멘터리', '다큐멘터리'),
        ('드라마', '드라마'),
        ('가족', '가족'),
        ('판타지', '판타지'),
        ('역사', '역사'),
        ('공포', '공포'),
        ('음악', '음악'),
        ('미스터리', '미스터리'),
        ('로맨스', '로맨스'),
        ('SF', 'SF'),
        ('TV 영화', 'TV 영화'),
        ('스릴러', '스릴러'),
        ('전쟁', '전쟁'),
        ('서부', '서부'),
    ]

    genres = forms.MultipleChoiceField(
        required=True,
        label='장르',
        widget=forms.CheckboxSelectMultiple,
        choices=GENRE_CHOICES,
    )

    release_date = forms.DateField(
        label='개봉일',
        widget = forms.SelectDateWidget(years=range(now.year, 1900, -1))
    )

    video = forms.CharField(
        label='영상 주소',
        help_text='유튜브 주소를 입력해주세요.',
    )
    overview = forms.CharField(
        label='줄거리',
        widget=forms.Textarea(
            attrs={
                'rows': 10
            }
        )
    )
    budget = forms.IntegerField(
        label='예산',
        widget=forms.NumberInput(
            attrs={
                'style': 'width: 10rem;'
            }
        )
    )

    runtime = forms.IntegerField(
        label='러닝타임',
        widget=forms.NumberInput(
            attrs={
                'style': 'width: 10rem;'
            }
        )
    )
    vote_average = forms.FloatField(
        label='평점',
        help_text='0~10 사이로 입력해주세요.',
        min_value=0.0,
        max_value=10.0,
        widget=forms.NumberInput(
            attrs={
                'style': 'width: 10rem;'
            }
        )
    )

    class Meta:
        model = Movie
        # fields = '__all__'
        exclude = ['movieid', 'like_users', 'poster_path', 'backdrop_path']
