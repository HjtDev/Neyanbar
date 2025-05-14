from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template.context_processors import request

from shop.models import Product, Volume
from main.models import Setting
from account.models import User
from django.utils import timezone


class Order(models.Model):
    objects = models.Manager()

    class ReceiveChoices(models.TextChoices):
        POST = 'POST', 'به صورت پستی'
        IN_PERSON = 'IN_PERSON', 'به صورت حضوری'

    class StatusChoices(models.TextChoices):
        NOT_PAID = 'NOT_PAID', 'پرداخت نشده'
        PENDING = 'PENDING', 'در انتظار تایید'
        CONFIRMED = 'CONFIRMED', 'تایید شد'
        IN_PROGRESS = 'IN_PROGRESS', 'در حال آماده سازی'
        READY_TO_SHIP = 'READY_TO_SHIP', 'آماده تحویل'
        SHIPPED = 'SHIPPED', 'تحویل داده شد'
        FINISHED = 'FINISHED', 'تکمیل شد'
        REJECTED = 'REJECTED', 'لغو شد'

    order_id = models.CharField(max_length=12, unique=True, verbose_name='کد سفارش')
    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='کاربر')
    name = models.CharField(max_length=100, verbose_name='نام و نام خانوادگی')
    phone = models.CharField(max_length=11, verbose_name='شماره تلفن')
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name='ایمیل')
    province = models.CharField(max_length=30, blank=True, verbose_name='استان')
    city = models.CharField(max_length=30, blank=True, verbose_name='شهر')
    address = models.CharField(max_length=300, blank=True, verbose_name='آدرس')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='کد پستی')
    not_for_me = models.BooleanField(default=False, verbose_name='سفارش برای شخص دیگری است')
    receive_type = models.CharField(max_length=13, choices=ReceiveChoices.choices, default=ReceiveChoices.POST, verbose_name='نوع دریافت')
    receive_time = models.DateField(blank=True, null=True, verbose_name='زمان دریافت')
    status = models.CharField(max_length=17, choices=StatusChoices.choices, default=StatusChoices.NOT_PAID, verbose_name='وضعیت')
    description = models.TextField(max_length=500, blank=True, verbose_name='توضیحات سفارش')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت سفارش')

    def __str__(self):
        return f'Order {self.order_id}'

    def save(self, *args, **kwargs):
        if self.user and self.items.exists():
            for item in self.items.all():
                if self.user not in item.product.bought_by.all():
                    item.product.bought_by.add(self.user)


    def get_total_cost(self):
        settings = Setting.objects.first()
        return int(sum(item.price for item in self.items.all()) * (1 + settings.tax_fee / 100) + settings.post_fee)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'


class OrderItem(models.Model):
    objects = models.Manager()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='سفارش')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, verbose_name='حجم')
    quantity = models.PositiveIntegerField(verbose_name='تعداد')
    price = models.PositiveIntegerField(default=0, verbose_name='هزینه', help_text='با در نظر گرفتن حجم و تعداد')

    def calculate_price(self, request):
        if request.session.get('discount'):
            discount = Discount.objects.get(id=request.session.get('discount'))
            if discount.is_valid():
                return discount.get_price(self.product, self.volume) * self.quantity
        return self.product.get_volume_price(self.volume.volume) * self.quantity

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class Discount(models.Model):
    objects = models.Manager()
    token = models.CharField(max_length=10, verbose_name='کد تخقیف')
    value = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(100)],
                                        verbose_name='تخفیف به درصد')
    selected = models.CharField(default='', verbose_name='محصولات و کاربران انتخاب شده',
                                help_text='products:<<slug1;slug2;...> or all>|p_exclude:<slug1;slug2;...>|users:<id1;id2;...> or all|u_exclude:<id1;id2;...>')
    users = models.ManyToManyField(User, related_name='used_discounts', blank=True,
                                   verbose_name='کسانی که از این تخفیف استفاده کرده اند')
    expire_at = models.DateField(verbose_name='زمان انقضا')

    def is_expired(self):
        if timezone.now().date().today() > self.expire_at:
            return True
        return False

    def get_list(self, obj: str):
        return obj.split(':')[1].split(';')

    def get_selected_users(self):
        # users:<id1;id2;...> or all|u_exclude:<id1;id2;...>
        if not self.selected:
            return []
        selected_users = self.selected.split('|')[2:]
        users, excluded_users = selected_users[0], selected_users[1]
        return User.objects.all().exclude(id__in=self.get_list(excluded_users)) if users.split(':')[
                                                                                       1] == 'all' else User.objects.filter(
            id__in=self.get_list(users)).exclude(id__in=self.get_list(excluded_users))

    def is_valid(self, user) -> tuple[bool, str | Product]:
        if self.is_expired():
            return False, 'زمان این تخفیف به پایان رسیده است'

        if user in self.users.all():
            return False, 'شما قبلا از تخفیف استفاده کرده اید'

        if user not in self.get_selected_users():
            return False, 'این تخفیف شامل شما نمی شود'

        selected_products = self.selected.split('|')[:2]
        products, excluded_products = selected_products[0], selected_products[1]
        if products.split(':')[1] == 'all':
            return True, Product.objects.all().exclude(slug__in=self.get_list(excluded_products))
        return True, Product.objects.filter(slug__in=self.get_list(products)).exclude(slug__in=self.get_list(excluded_products))

    def get_price(self, product: Product, volume):
        # products:<<slug1;slug2;...> or all>|p_exclude:<slug1;slug2;...
        selected_products = self.selected.split('|')[:2]
        products, excluded_products = selected_products[0], selected_products[1]
        all_products = None
        if products.split(':')[1] == 'all':
            all_products = Product.objects.all().exclude(slug__in=self.get_list(excluded_products))
        else:
            all_products = Product.objects.filter(slug__in=self.get_list(products)).exclude(
                slug__in=self.get_list(excluded_products))
        discount = 1 - (self.value / 100)
        return int(
            product.get_volume_price(volume) * discount if product in all_products else product.get_volume_price(
                volume))

    class Meta:
        verbose_name = 'تخفیف'
        verbose_name_plural = 'تخفیف ها'


class CreditCart(models.Model):
    objects = models.Manager()
    token = models.CharField(max_length=10, verbose_name='توکن کارت')
    credit = models.PositiveIntegerField(verbose_name='اعتبار کارت')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='ساخته شده توسط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')

    def buy(self, price):
        if self.credit >= price:
            self.credit -= price
            self.save()
            return True
        return False

    def __str__(self):
        return f' {self.token}کارت اعتباری:'

    class Meta:
        verbose_name = 'کارت اعتباری'
        verbose_name_plural = 'کارت های اعتباری'


class Transaction(models.Model):
    objects = models.Manager()

    class PaymentChoices(models.TextChoices):
        GATEWAY = 'GATEWAY', 'از طریق درگاه پرداخت'
        CREDIT = 'CREDIT', 'با کارت اعتباری'

    order = models.ForeignKey(Order, on_delete=models.SET_NULL, related_name='transactions', null=True, verbose_name='برای سفارش')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='توسط')
    payment_type = models.CharField(max_length=21, choices=PaymentChoices.choices, verbose_name='نوع پرداخت')
    paid_amount = models.IntegerField(verbose_name='هزینه دریافتی')
    content = models.TextField(verbose_name='توضیحات', blank=True)

    def __str__(self):
        return f'{self.order} - {self.user}'

    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش ها'
