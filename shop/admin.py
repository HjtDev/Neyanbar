from django.contrib import admin
from django.db.models import Count

from main.utilities import send_sms, PRODUCT_NOTIFY_ME
from .models import Product, ProductSmell, Image, Features, Brand, Comment, Volume


class ImageInline(admin.StackedInline):
    model = Image
    extra = 1


class FeaturesInline(admin.StackedInline):
    model = Features
    extra = 1


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pid', 'name', 'brand', 'get_price', 'site_score', 'inventory', 'views', 'get_buy_count', 'is_visible')
    list_filter = (
        'smell', 'season', 'spread',
        'taste', 'nature', 'gender',
        'available_volumes', 'perfume_type', 'is_visible',
        'brand', 'site_score',
        'last_view', 'created_at', 'updated_at'
    )
    list_editable = ('is_visible', 'inventory', 'site_score')
    search_fields = ('pid', 'name', 'name_en', 'short_description', 'description')
    list_per_page = 20
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [
        ImageInline,
        FeaturesInline,
        CommentInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(buy_count=Count('bought_by'))

    def get_buy_count(self, obj):
        return obj.buy_count
    get_buy_count.admin_order_field = 'buy_count'
    get_buy_count.short_description = 'فروش'

    fieldsets = (
        ('اطلاعات محصول', {
            'fields': (
                'name', 'name_en', 'slug', 'pid',
                'short_description', 'description', 'video',
                'is_visible'
            )
        }),
        ('قیمت ها', {
            'fields': ('price', 'discount', 'reset_discount_at'),
        }),
        ('دسته بندی ها', {
            'fields': (
                'smell', 'season', 'spread',
                'brand', 'taste', 'nature',
                'gender', 'durability', 'available_volumes', 'perfume_type'
            ),
        }),
        ('گزارشات', {
            'fields': ('inventory', 'site_score', 'liked_by',
                       'bought_by', 'remind_to', 'views',
                       'last_view', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('views', 'last_view', 'created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'content', 'created_at', 'is_verified')
    list_filter = ('user', 'product', 'created_at', 'is_verified')
    search_fields = ('product__name', 'content')
    ordering = ('-created_at',)
    list_editable = ('is_verified',)
    list_per_page = 15


# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_filter = ('smell', 'season', 'taste', 'nature', 'gender', 'volume', 'perfume_type')


@admin.register(ProductSmell)
class ProductSmellAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ('name',)
