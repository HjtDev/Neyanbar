from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from shop.models import Product, Brand


class Setting(models.Model):
    objects = models.Manager()

    site_access = models.BooleanField(default=True, verbose_name='دسترسی به سایت', help_text='دسترسی همه کاربران از سایت قطع می شود.')

    order_waiting_days = models.PositiveIntegerField(default=3, verbose_name='زودترین زمان ثبت سفارش', help_text='تعداد روز های مورد نیاز برای پردازش هر سفارش')
    orders_per_day = models.PositiveIntegerField(default=1, verbose_name='بیشترین تعداد سفارش در یک روز')
    order_days_limit = models.PositiveIntegerField(default=3, verbose_name='تعداد روز های قابل انتخاب برای دریافت سفارش')
    post_fee = models.PositiveIntegerField(default=10, validators=[MinValueValidator(10)], verbose_name='کرایه پست', help_text='به تومان')
    post_fee_max = models.PositiveIntegerField(default=1_000_000, validators=[MinValueValidator(10)], verbose_name='حداکثر هزینه اعمال پست', help_text='در صورتی که هزینه سفارش بیشتر از جداکثر بشه کرایه پست رایگان در نظر گرفته میشه')
    tax_fee = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name='مالیات', help_text='به درصد')

    show_offer = models.BooleanField(default=False, verbose_name='نمایش پیشنهاد')
    title = models.CharField(max_length=50, blank=True, verbose_name='تیتر پیشنهاد')
    event = models.CharField(max_length=100, blank=True, verbose_name='(مناسبت/علت تخفیف) پیشنهاد')
    products = models.CharField(blank=True, verbose_name='محصولات انتخاب شده', help_text='بر اساس لیست پیشنهاد های مجاز')
    banner = models.ImageField(upload_to='offers/', blank=True, verbose_name='بنر')

    video_text = models.CharField(max_length=150, blank=True, verbose_name='متن ویدیو')
    footer_text = models.TextField(blank=True, verbose_name='متن فوتر')

    def get_post_fee(self, order_total):
        return self.post_fee if order_total < self.post_fee_max else 0

    def get_offer_link(self):
        if not self.show_offer or not self.products:
            return ''
        args = self.products.split(':')[1]
        if self.products.startswith('products:'):
            if not ';' in args:
                return reverse('shop:product-detail', kwargs={'slug': args})
            return reverse('shop:product-list') + f'?products={args}'
        elif self.products.startswith('brands:'):
            return reverse('shop:product-list') + f'?brands={args}'
        elif self.products.startswith('volumes:'):
            return reverse('shop:product-list') + f'?volumes={args}'
        elif self.products.startswith('smells'):
            return reverse('shop:product-list') + f'?smells={args}'
        elif self.products.startswith('spreads'):
            return reverse('shop:product-list') + f'?spreads={args}'
        elif self.products.startswith('seasons:'):
            return reverse('shop:product-list') + f'?seasons={args}'
        elif self.products.startswith('tastes:'):
            return reverse('shop:product-list') + f'?tastes={args}'
        elif self.products.startswith('nature'):
            return reverse('shop:product-list') + f'?nature={args}'
        elif self.products.startswith('durability:'):
            return reverse('shop:product-list') + f'?durability={args}'
        elif self.products.startswith('gender'):
            return reverse('shop:product-list') + f'?gender={args}'
        elif self.products.startswith('type:'):
            return reverse('shop:product-list') + f'?type={args}'
        return ''

    def get_offer_products(self):
        if not self.show_offer or not self.products:
            return []
        args = self.products.split(':')[1].split(';')
        if self.products.startswith('products:'):
            return Product.objects.filter(slug__in=args)
        elif self.products.startswith('brands:'):
            return Product.objects.filter(brand__slug__in=args)
        elif self.products.startswith('volumes:'):
            return Product.objects.filter(available_volumes__volume__in=args)
        elif self.products.startswith('smells'):
            return Product.objects.filter(smell__value__in=args)
        elif self.products.startswith('spread'):
            return Product.objects.filter(spread__in=args)
        elif self.products.startswith('seasons:'):
            return Product.objects.filter(season__in=args)
        elif self.products.startswith('tastes:'):
            return Product.objects.filter(taste__in=args)
        elif self.products.startswith('nature'):
            return Product.objects.filter(nature__in=args)
        elif self.products.startswith('durability:'):
            return Product.objects.filter(durability__in=args)
        elif self.products.startswith('gender'):
            return Product.objects.filter(gender__in=args)
        elif self.products.startswith('type:'):
            return Product.objects.filter(type__in=args)
        return []

    def __str__(self):
        return 'تنظیمات'

    class Meta:
        verbose_name = verbose_name_plural = 'تنظیمات'


class PerfumeRequest(models.Model):
    objects = models.Manager()
    text = models.EmailField(max_length=255, unique=True, verbose_name='متن درخواست')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'درخواست عطر'
        verbose_name_plural = 'درخواست عطر'


class FAQ(models.Model):
    objects = models.Manager()
    question = models.CharField(max_length=255, verbose_name='سوال')
    answer = models.TextField(verbose_name='جواب')
    is_visible = models.BooleanField(default=True, verbose_name='نمایش در سایت')
    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'


class AboutUs(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=255, verbose_name='تیتر')
    description = models.TextField(verbose_name='توضیحات')
    image = models.ImageField(upload_to='about_us', verbose_name='تصویر')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'درباره ما'
        verbose_name_plural = 'درباره ما'


class Terms(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=255, verbose_name='تیتر')
    description = models.TextField(verbose_name='توضیحات')
    image = models.ImageField(upload_to='terms', verbose_name='تصویر')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'شرایط و ضوابط'
        verbose_name_plural = 'شرایط و ضوابط'
