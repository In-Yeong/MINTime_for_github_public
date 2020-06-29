from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):

    CHOICES= [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★')
    ]
    star = forms.IntegerField(
        label='별점',
        widget=forms.Select(
            choices = CHOICES,
            attrs={
                'style': 'width: 10rem;'
            }
        )
    )

    content = forms.CharField(
        label='리뷰',
        help_text='200자 이내',
        widget=forms.Textarea(
            attrs={'style': 'height: 10rem;'}
        )
        
    )

    class Meta:
        model = Review
        fields = ['content', 'star']