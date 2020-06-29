from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from decouple import config
import requests
from django.contrib.auth.decorators import login_required
from accounts.models import Premium

@login_required
def approval(request):
    User = get_user_model()
    user = get_object_or_404(User, pk=request.user.pk)

    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        "Authorization": "KakaoAK " + config('KPAY_KEY'),
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",    # 변경불가. 실제로 사용하려면 카카오와 가맹을 맺어야함. 현재 코드는 테스트용 코드
        "tid": request.session['tid'],  # 결제 요청시 세션에 저장한 tid
        "partner_order_id": request.session['order_id'],     # 주문번호
        "partner_user_id": "{}".format(user),    # 유저 아이디
        "pg_token": request.GET.get("pg_token"),     # 쿼리 스트링으로 받은 pg토큰
    }

    res = requests.post(URL, headers=headers, params=params).json()

    Premium.objects.create(
        user=user,
    )

    context = {
        'res': res,
    }
    return render(request, 'kakaopay/approval.html', context)

@login_required
def cancel(request):
    return render(request, 'kakaopay/cancel.html')

@login_required
def fail(request):
    return render(request, 'kakaopay/fail.html')