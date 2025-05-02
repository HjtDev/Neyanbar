from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from tinymce.models import HTMLField
import os
from account.models import User


def product_dynamic_path(instance, filename):
    return os.path.join(
        'Products',
        'content',
        filename
    )

def video_validator(value):
    format = os.path.splitext(value.name)[1]
    if format.lower() != '.mp4':
        raise ValidationError('فقط فایل های ویدیویی mp4 قابل قبول می باشد!')


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='اسم محصول', help_text='به فارسی')
    name_en = models.CharField(max_length=100, verbose_name='اسم محصول', help_text='به انگلیسی')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='اسلاگ')

    smell = models.ManyToManyField('ProductSmell', blank=True, null=True, verbose_name='گروه بویایی')

    class SeasonChoices(models.TextChoices):
        WINTER = 'WINTER', 'زمستانی'
        SUMMER = 'SUMMER', 'تابستانی'
    season = models.CharField(choices=SeasonChoices.choices, max_length=8, verbose_name='فصل')

    class TasteChoices(models.TextChoices):
        SPICY = 'SPICY', 'تند'
        SWEET = 'SWEET', 'شیرین'
        BITTER = 'BITTER', 'تلخ'
        SOUR = 'SOUR', 'ترش'
    taste = models.CharField(choices=TasteChoices.choices, max_length=6, verbose_name='طعم')

    class NatureChoices(models.TextChoices):
        WARM = 'WARM', 'گرم'
        COLD = 'COLD', 'سرد'
    nature = models.CharField(choices=NatureChoices.choices, max_length=4, verbose_name='طبع')

    class GenderChoices(models.TextChoices):
        MALE = 'MALE', 'مردانه'
        FEMALE = 'FEMALE', 'زنانه'
        UNISEX = 'UNISEX', 'مشترک'
    gender = models.CharField(choices=GenderChoices.choices, max_length=6, verbose_name='جنسیت')

    class VolumeChoices(models.TextChoices):
        TEN = '10m', '10m'
        TWENTY = '20m', '20m'
        THIRTY = '30m', '30m'
        FIFTY = '50m', '50m'
        SIXTY = '60m', '60m'
        HUNDRED = '100m', '100m'
        HUNDRED_TWENTY = '120m', '120m'
        HUNDRED_FIFTY = '150m', '150m'
    volume = models.CharField(choices=VolumeChoices.choices, max_length=4, verbose_name='حجم')

    class TypeChoices(models.TextChoices):
        PERFUME = 'PERFUME', 'پرفیوم'
        EAU_DE_PARFUM = 'EAU_DE_PARFUM', 'ادوپرفیوم'
        EAU_DE_TOILETTE = 'EAU_DE_TOILETTE', 'ادوتویلت'
        EAU_DE_COLOGNE = 'EAU_DE_COLOGNE', 'ادوکلن'
        BODY_SPLASH = 'BODY_SPLASH', 'بادی اسپلش'
    perfume_type = models.CharField(choices=TypeChoices.choices, max_length=15, verbose_name='نوع')

    pid = models.CharField(max_length=6, unique=True, verbose_name='کد محصول')

    price = models.PositiveIntegerField(default=0, verbose_name='قیمت محصول')
    discount = models.IntegerField(default=-1, validators=[MinValueValidator(-1)], verbose_name='قیمت پس از تخفیف', help_text='-۱ برای لغو تخفیف')

    inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی انبار')

    short_description = HTMLField(verbose_name='توضیحات کوتاه')
    description = HTMLField(verbose_name='توضیحات اصلی')

    video = models.FileField(upload_to=product_dynamic_path, blank=True, null=True, validators=[video_validator], verbose_name='ویدیو توضیحات', help_text='.mp4')

    views = models.PositiveIntegerField(default=0, verbose_name='بازدید ها')
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_products', verbose_name='کسانی که این محصول را پسندیده اند')
    bought_by = models.ManyToManyField(User, blank=True, related_name='saved_products', verbose_name='کسانی که این محصول را خریده اند')

    is_visible = models.BooleanField(default=False, verbose_name='نمایش در سایت')

    last_view = models.DateTimeField(blank=True, null=True, verbose_name='اخرین بازدید')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین آپدیت')

    def __str__(self):
        return self.name

    def get_price(self):
        return self.price if self.discount == -1 else self.discount

    get_price.short_description = 'قیمت'

    def get_price_difference(self):
        return self.price - self.discount
    def get_smell(self):
        return self.categories.smell.all()

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['-created_at'],
            )
        ]


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='محصولات')
    image = models.ImageField(upload_to=product_dynamic_path, verbose_name='تصویر')
    alt = models.CharField(verbose_name='تیتر', help_text='برای سئو')

    def __str__(self):
        return f'{self.product.name} | {self.image.name}'

    def delete(self, *args, **kwargs):
        os.remove(self.image.path)
        return super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'تصویر'
        verbose_name_plural = 'تصاویر'


class Features(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features', verbose_name='محصول')
    key = models.CharField(max_length=30, verbose_name='ویزگی')
    value = models.CharField(max_length=100, verbose_name='مقدار')

    def __str__(self):
        return f'{self.product.name} | {self.key}: {self.value}'

    class Meta:
        verbose_name = 'ویژگی'
        verbose_name_plural = 'ویژگی ها'


class ProductSmell(models.Model):
    class SmellChoices(models.TextChoices):
        GOLFAM = 'GOLFAM', 'گلفام'
        WOODY = 'WOODY', 'چوبی'
        FRUITY = 'FRUITY', 'میوه ای'
        CITRUS = 'CITRUS', 'مرکباتی'
        MARINE = 'MARINE', 'دریایی'
        ORIENTAL = 'ORIENTAL', 'شرقی'
        SPICY = 'SPICY', 'ادویه ای'
        FOUGERE = 'FOUGERE', 'فوژه'
        LEATHERY = 'LEATHERY', 'چرمی'
        MEDITERRANEAN = 'MEDITERRANEAN', 'مدیترانه ای'
        AROMATIC = 'AROMATIC', 'آروماتیک'
    value = models.CharField(choices=SmellChoices.choices, max_length=15, verbose_name='گروه بویایی')

    def __str__(self):
        return self.get_value_display()

    class Meta:
        verbose_name = 'گروه بویایی'
        verbose_name_plural = 'گروه های بویایی'
