from django.contrib import admin
from .models import Product, ProductSmell, Image, Features


class ImageInline(admin.StackedInline):
    model = Image
    extra = 1


class FeaturesInline(admin.StackedInline):
    model = Features
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pid', 'name', 'get_price', 'inventory', 'views', 'is_visible')
    list_filter = (
        'smell', 'season',  'taste',
        'nature', 'gender', 'volume',
        'perfume_type', 'is_visible',
        'last_view', 'created_at','updated_at'
    )
    list_editable = ('is_visible',)
    search_fields = ('pid', 'name', 'name_en', 'short_description', 'description')
    list_per_page = 20
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [
        ImageInline,
        FeaturesInline,
    ]

    fieldsets = (
        ('اطلاعات محصول', {
            'fields': (
                'name', 'name_en', 'slug', 'pid',
                'short_description', 'description', 'video',
                'is_visible'
            )
        }),
        ('قیمت ها', {
            'fields': ('price', 'discount'),
        }),
        ('دسته بندی ها', {
            'fields': (
                'smell', 'season', 'taste',
                'nature', 'gender', 'volume',
                'perfume_type'
            ),
        }),
        ('گزارشات', {
            'fields': ('inventory', 'liked_by', 'bought_by', 'views', 'last_view', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('views', 'last_view', 'created_at', 'updated_at')


# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_filter = ('smell', 'season', 'taste', 'nature', 'gender', 'volume', 'perfume_type')


@admin.register(ProductSmell)
class ProductSmellAdmin(admin.ModelAdmin):
    list_display = ('value',)
    list_filter = ('value',)
