from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
from .models import Setting


class SiteAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_superuser:
            if request.path.startswith('/admin/'):
                if request.user.is_authenticated:
                    return render(request, '404.html', {'message': 'شما اجازه دسترسی به پنل مدیریت را ندارید'}, status=403)
                return None
            if not Setting.objects.first().site_access:
                return render(request, '404.html', {'message': 'سایت در حال بروزرسانی می باشد بعدا تلاش کنید'}, status=503)
        return None
