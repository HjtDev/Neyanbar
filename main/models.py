from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

from shop.models import Product, Brand


class Setting(models.Model):
    objects = models.Manager()

    site_access = models.BooleanField(default=True, verbose_name='دسترسی به سایت', help_text='دسترسی همه کاربران از سایت قطع می شود.')

    post_fee = models.PositiveIntegerField(default=10, validators=[MinValueValidator(10)], verbose_name='کرایه پست', help_text='به تومان')
    tax_fee = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name='مالیات', help_text='به درصد')

    show_offer = models.BooleanField(default=False, verbose_name='نمایش پیشنهاد')
    title = models.CharField(max_length=30, blank=True, verbose_name='تیتر پیشنهاد')
    event = models.CharField(max_length=100, blank=True, verbose_name='(مناسبت/علت تخفیف) پیشنهاد')
    products = models.CharField(max_length=50, blank=True, verbose_name='محصولات انتخاب شده', help_text='بر اساس لیست پیشنهاد های مجاز')
    banner = models.ImageField(upload_to='offers/', blank=True, verbose_name='بنر')

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

    def __str__(self):
        return 'تنظیمات'

    class Meta:
        verbose_name = verbose_name_plural = 'تنظیمات'


