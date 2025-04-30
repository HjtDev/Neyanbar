from django.shortcuts import render
from datetime import datetime
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import jdatetime


@csrf_exempt
def editor_upload_handler(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file_obj = request.FILES['file']
        now = datetime.now()
        now = jdatetime.GregorianToJalali(now.year, now.month, now.day)

        upload_path = os.path.join(
            settings.MEDIA_ROOT, 'editor',
            str(now.jyear), str(now.jmonth).zfill(2), str(now.jday).zfill(2)
        )
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, file_obj.name)
        with open(file_path, 'wb+') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        file_url = f"{settings.MEDIA_URL}editor/{now.jyear}/{str(now.jmonth).zfill(2)}/{str(now.jday).zfill(2)}/{file_obj.name}"
        return JsonResponse({'location': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)
