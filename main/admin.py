from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Setting
from django.shortcuts import redirect


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('دسترسی به سایت'), {
            'fields': ['site_access'],
            'classes': ['collapse', 'tab-site-access'],
        }),
        (_('هزینه ها'), {
            'fields': ['post_fee', 'tax_fee'],
            'classes': ['collapse', 'tab-fee-fields'],
        }),
        (_('پیشنهاد'), {
            'fields': ['show_offer', 'title', 'event', 'products', 'banner'],
            'classes': ['collapse', 'tab-offer-fields'],
        }),
    ]

    def has_add_permission(self, request):
        Setting.objects.count()
        if Setting.objects.count() == 0:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        qs = Setting.objects.all()
        if qs.count() == 1:
            setting = qs.first()
            return redirect(f'/admin/main/setting/{setting.pk}/change/')
        return super().changelist_view(request, extra_context)

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        if Setting.objects.count() == 1:
            perms['add'] = False
        return perms
