from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Setting, PerfumeRequest, AboutUs, Terms
from django.shortcuts import redirect


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('دسترسی به سایت'), {
            'fields': ['site_access'],
            'classes': ['collapse', 'tab-site-access'],
        }),
        (_('سفارشات'), {
            'fields': ['order_waiting_days', 'orders_per_day', 'order_days_limit'],
            'classes': ['collapse', 'tab-order-fields'],
        }),
        (_('هزینه ها'), {
            'fields': ['post_fee', 'tax_fee'],
            'classes': ['collapse', 'tab-fee-fields'],
        }),
        (_('پیشنهاد'), {
            'fields': ['show_offer', 'title', 'event', 'products', 'banner'],
            'classes': ['collapse', 'tab-offer-fields'],
        }),
        (_('متن ها'), {
            'fields': ['video_text', 'footer_text',],
            'classes': ['collapse', 'tab-text-fields'],
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


@admin.register(PerfumeRequest)
class PerfumeRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    search_fields = ('text',)
    list_per_page = 15


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title', 'description')

@admin.register(Terms)
class TermsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title', 'description')


# @admin.register(FAQ)
# class FAQAdmin(admin.ModelAdmin):
#     list_display = ('id', 'question', 'is_visible')
#     list_filter = ('is_visible',)
#     search_fields = ('question', 'answer')
#     list_editable = ('is_visible',)
#     list_per_page = 15
