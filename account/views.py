from django.contrib.auth import login
from django.shortcuts import render
from django.http.response import JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from .forms import validate_phone
from .models import User
from random import randint
from main.utilities import send_sms
from copy import deepcopy


@require_POST
def login_view(request):
    phone = request.POST.get('phone')
    try:
        if phone and validate_phone(phone):
            user = User.objects.get(phone=phone)
            if cache.get(f'login-user-{user.id}'):
                return JsonResponse({'message': 'لطفا حداقل ۲ دقیقه برای دریافت کد جدید صبر کنید.'}, status=403)
            token = randint(1000, 9999)
            cache.set(f'login-user-{user.id}', token, timeout=30)
            send_sms(phone, token)
            return JsonResponse({'token_sent': True}, status=200)
        else:
            return JsonResponse({'message': 'شماره تلفن اشتباه است.'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'message': 'این شماره تلفن وجود ندارد.'}, status=404)


@require_POST
def verify_view(request):
    phone = request.POST.get('phone')
    token = request.POST.get('token')
    print('Recieved', phone, token)
    try:
        if phone and token:
            user = User.objects.get(phone=phone)
            code = cache.get(f'login-user-{user.id}')
            if not code:
                return JsonResponse({'message': 'کد تایید منقضی شده است.'}, status=406)
            elif code == int(token):
                login(request, user)
                cache.delete(f'login-user-{user.id}')
                return JsonResponse({'logged_in': True}, status=200)
            else:
                return JsonResponse({'message': 'کد تایید اشتباه است.'}, status=403)
        else:
            return JsonResponse({'message': 'کد تایید یا شماره تلفن اشتباه می باشد.'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'message': 'این شماره تلفن وجود ندارد.'}, status=404)