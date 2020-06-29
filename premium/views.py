from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from decouple import config
import requests

from accounts.models import Premium

# Create your views here.


@login_required
def event(request):

    User = get_user_model()
    user = get_object_or_404(User, pk=request.user.pk)
    current_site = request.build_absolute_uri()[:-14]
    is_premium = Premium.objects.filter(user=user)
    if request.method == "POST":    # 버튼 누르면
  
        if not is_premium:

            URL = 'https://kapi.kakao.com/v1/payment/ready'
            headers = {
                "Authorization": "KakaoAK " + config('PRE_KEY'),
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            }
            params = {
                "cid": "TC0ONETIME",    # 변경불가. 실제로 사용하려면 카카오와 가맹을 맺어야함. 현재 코드는 테스트용 코드
                "partner_order_id": "{}".format(user.pk),
                "partner_user_id": "{}".format(user.username),    # 유저 아이디
                "item_name": "premium",        # 구매 물품 이름
                "quantity": "1",                # 구매 물품 수량
                "total_amount": "2000",  # 구매 물품 가격
                "tax_free_amount": "0",         # 구매 물품 비과세 (0으로 고정)
                "approval_url": "{}kakaopay/approval/".format(current_site),    # 결제 성공 시 이동할 url
                "cancel_url": "{}kakaopay/cancel/".format(current_site),               # 결제 취소 시 이동할 url
                "fail_url": "{}kakaopay/fail/".format(current_site),                 # 결제 실패 시 이동할 url
            }

            res = requests.post(URL, headers=headers, params=params)
            print(res)
            request.session['tid'] = res.json()['tid']  # 결제 승인시 사용할 tid를 세션에 저장
            request.session['order_id'] = "{}".format(user.pk)
            next_url = res.json()['next_redirect_pc_url']  # 결제 페이지로 넘어갈 url을 저장
            return redirect(next_url)

        else:
            return redirect('accounts:profile',user.username ,0)

    context = {
        'is_premium': len(is_premium),
    }

    return render(request, 'premium/event.html', context)