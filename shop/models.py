from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Min
from django.urls import reverse
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
    objects = models.Manager()
    name = models.CharField(max_length=100, verbose_name='اسم محصول', help_text='به فارسی')
    name_en = models.CharField(max_length=100, verbose_name='اسم محصول', help_text='به انگلیسی')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='اسلاگ')

    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, related_name='products', blank=True, null=True, verbose_name='برند')
    available_volumes = models.ManyToManyField('Volume', related_name='products', blank=True, verbose_name='حجم های موجود')

    smell = models.ManyToManyField('ProductSmell', verbose_name='گروه بویایی')

    class SpreadChoices(models.TextChoices):
        LOW = 'LOW', 'کم'
        MEDIUM = 'MEDIUM', 'متوسط'
        HIGH = 'HIGH', 'زیاد'
    spread = models.CharField(choices=SpreadChoices.choices, max_length=6, verbose_name='پخش بو')

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

    class DurabilityChoices(models.TextChoices):
        LOW = 'LOW', 'کم'
        MEDIUM = 'MEDIUM', 'متوسط'
        HIGH = 'HIGH', 'زیاد'
    durability = models.CharField(choices=DurabilityChoices.choices, max_length=6, verbose_name='ماندگاری')

    class GenderChoices(models.TextChoices):
        MALE = 'MALE', 'مردانه'
        FEMALE = 'FEMALE', 'زنانه'
        UNISEX = 'UNISEX', 'مشترک'
    gender = models.CharField(choices=GenderChoices.choices, max_length=6, verbose_name='جنسیت')

    class TypeChoices(models.TextChoices):
        PERFUME = 'PERFUME', 'پرفیوم'
        EAU_DE_PARFUM = 'EAU_DE_PARFUM', 'ادوپرفیوم'
        EAU_DE_TOILETTE = 'EAU_DE_TOILETTE', 'ادوتویلت'
        EAU_DE_COLOGNE = 'EAU_DE_COLOGNE', 'ادوکلن'
        BODY_SPLASH = 'BODY_SPLASH', 'بادی اسپلش'
    perfume_type = models.CharField(choices=TypeChoices.choices, max_length=15, verbose_name='نوع')

    pid = models.CharField(max_length=6, unique=True, verbose_name='کد محصول')

    price = models.PositiveIntegerField(default=0, verbose_name='قیمت محصول', help_text='به ازای هر گرم / به تومان')
    discount = models.IntegerField(default=-1, validators=[MinValueValidator(-1)], verbose_name='قیمت پس از تخفیف', help_text='-۱ برای لغو تخفیف')

    inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی انبار')

    short_description = HTMLField(verbose_name='توضیحات کوتاه')
    description = HTMLField(verbose_name='توضیحات اصلی')

    video = models.FileField(upload_to=product_dynamic_path, blank=True, null=True, validators=[video_validator], verbose_name='ویدیو توضیحات', help_text='.mp4')

    site_score = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)], verbose_name='امتیاز سایت')

    views = models.PositiveIntegerField(default=0, verbose_name='بازدید ها')
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_products', verbose_name='کسانی که این محصول را پسندیده اند')
    bought_by = models.ManyToManyField(User, blank=True, related_name='bought_products', verbose_name='کسانی که این محصول را خریده اند')
    remind_to = models.ManyToManyField(User, blank=True, related_name='reminder_products', verbose_name='کسانی که منتظر موجود شدن این محصول هستند')

    is_visible = models.BooleanField(default=False, verbose_name='نمایش در سایت')

    last_view = models.DateTimeField(blank=True, null=True, verbose_name='اخرین بازدید')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین آپدیت')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if any(ch.isupper() for ch in self.slug):
            self.slug = self.slug.lower()
        return super().save(*args, **kwargs)

    def get_raw_price(self):
        return self.price * int(self.available_volumes.aggregate(Min('volume'))['volume__min'] or 1)
    def get_price(self):
        return self.price * int(self.available_volumes.aggregate(Min('volume'))['volume__min'] or 1) if self.discount == -1 else self.discount * int(self.available_volumes.aggregate(Min('volume'))['volume__min'] or 1)

    def get_volume_price(self, volume):
        return self.price * volume if self.discount == -1 else self.discount * volume


    get_price.short_description = 'کمترین قیمت موجود'

    def get_price_difference(self):
        return 100 - int((self.discount / self.price) * 100)

    def get_smell(self):
        return ', '.join([smell.get_value_display() for smell in self.smell.all()])

    def get_volumes(self):
        return ', '.join(list(volume for volume in self.available_volumes.values_list('name', flat=True)))

    def get_absolute_url(self):
        return reverse('shop:product-detail', kwargs={'slug': self.slug})

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
    image = models.ImageField(upload_to=product_dynamic_path, verbose_name='تصویر', help_text='No Background | .png or .webp')
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
    objects = models.Manager()

    class SmellChoices(models.TextChoices):
        GOLFAM = 'GOLFAM', 'گلفام'
        WOODY = 'WOODY', 'چوبی'
        FRUITY = 'FRUITY', 'میوه ای'
        CITRUS = 'CITRUS', 'مرکباتی'
        MARINE = 'MARINE', 'دریایی'
        ORIENTAL = 'EASTERN', 'شرقی'
        SPICY = 'SPICY', 'ادویه ای'
        FOUGERE = 'FOUGERE', 'فوژه'
        LEATHERY = 'LEATHERY', 'چرمی'
        MEDITERRANEAN = 'MEDITERRANEAN', 'مدیترانه ای'
        AROMATIC = 'AROMATIC', 'آروماتیک'
    value = models.CharField(choices=SmellChoices.choices, max_length=15, verbose_name='گروه بویایی')

    def __str__(self):
        return self.get_value_display()

    def get_absolute_url(self):
        return reverse('shop:product-list') + f'?smells={self.value}'

    class Meta:
        verbose_name = 'گروه بویایی'
        verbose_name_plural = 'گروه های بویایی'


class Brand(models.Model):
    objects = models.Manager()

    name = models.CharField(verbose_name='نام برند', unique=True, max_length=100)
    logo = models.ImageField(upload_to='Brands/Logo', verbose_name='لوگو', help_text='45*45 | white BG')
    banner = models.ImageField(upload_to='Brands/Banner', verbose_name='بنر', help_text='285*336')
    slug = models.SlugField(verbose_name='اسلاگ', unique=True, max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product-list') + f'?brands={self.slug}'

    def save(self, *args, **kwargs):
        if any(ch.isupper() for ch in self.slug):
            self.slug = self.slug.lower()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برند ها'


class Comment(models.Model):
    objects = models.Manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_comments', verbose_name='کاربر')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name='محصول')

    score = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز')
    content = models.TextField(max_length=320, verbose_name='متن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    is_verified = models.BooleanField(default=False, verbose_name='نمایش در سایت')

    liked_by = models.ManyToManyField(User, related_name='comment_likes', blank=True, verbose_name='لایک ها')

    def __str__(self):
        return f'{self.user} - {self.product}'

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'


class Volume(models.Model):
    objects = models.Manager()

    name = models.CharField(verbose_name='اسم', unique=True, max_length=100, help_text='مثال: ۱۰ گرم')
    volume = models.PositiveIntegerField(default=1, unique=True, verbose_name='حجم', help_text='به گرم')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product-list') + f'?volumes={self.volume}'

    class Meta:
        verbose_name = 'حجم'
        verbose_name_plural = 'حجم ها'
