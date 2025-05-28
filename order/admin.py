from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from main.templatetags.tags import to_jalali_verbose
from main.utilities import send_sms
from .models import Order, OrderItem, Discount, CreditCart, Transaction


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    verbose_name = 'آیتم سفارش'
    verbose_name_plural = 'آیتم‌های سفارش'
    readonly_fields = ('price',)

class TransactionInline(admin.StackedInline):
    model = Transaction
    extra = 0
    verbose_name = 'تراکنش'
    verbose_name_plural = 'تراکنش ها'
    readonly_fields = ('order', 'user')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, TransactionInline]

    list_display = ('order_id', 'name', 'phone', 'status', 'receive_time', 'created_at')
    list_filter = (
        'user',
        'status',
        'receive_type',
        'province',
        'city',
        'receive_time',
        'created_at',
        'not_for_me',
    )
    list_editable = ('status',)
    search_fields = ('order_id', 'name', 'phone', 'email', 'address', 'postal_code')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (_('اطلاعات سفارش'), {
            'fields': ('order_id', 'status', 'description', 'created_at')
        }),
        (_('اطلاعات دریافت'), {
            'fields': ('receive_type', 'receive_time', 'not_for_me', 'province', 'city', 'address', 'postal_code')
        }),
        (_('اطلاعات مشتری'), {
            'fields': ('user', 'name', 'phone', 'email')
        }),
    )


def discount_notify_everyone(modeladmin, request, queryset):
    for item in queryset:
        for user in item.get_selected_users():
            send_sms(user.phone, None, f'تخفیف ویژه برای خرید عطر فقط تا {to_jalali_verbose(item.expire_at)}\nکد تخفیف: {item.token}\nنی عنبر')

discount_notify_everyone.short_description = 'ارسال پیامک'

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('token', 'value', 'expire_at')
    list_filter = ('expire_at', 'users')
    search_fields = ('token', 'selected')
    ordering = ('-expire_at',)
    actions = [discount_notify_everyone]

    fieldsets = (
        (_('اطلاعات تخفیف'), {
            'fields': ('token', 'value', 'selected', 'expire_at')
        }),
        (_('کاربران'), {
            'fields': ('users',)
        }),
    )

@admin.register(CreditCart)
class CreditCartAdmin(admin.ModelAdmin):
    list_display = ('token', 'credit', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('token',)
    ordering = ('-created_at',)

    readonly_fields = ('created_at',)

    fieldsets = (
        (_('اطلاعات کارت اعتباری'), {
            'fields': ('token', 'credit', 'created_by', 'created_at')
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'payment_type', 'paid_amount')
    list_filter = ('payment_type', 'user')
    search_fields = ('order__order_id', 'user__name', 'content')
    ordering = ('-id',)  # order by newest first

    fieldsets = (
        (_('اطلاعات تراکنش'), {
            'fields': ('order', 'user', 'payment_type', 'paid_amount', 'content')
        }),
    )
