from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
import os


class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Users must have a phone number')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)


def profile_directory_path(instance, filename):
    return os.path.join(
        'Profiles',
        f'user_{instance.user.id}',
        filename
    )



class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=11, unique=True, verbose_name='شماره تلفن')
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True, verbose_name='ایمیل')
    name = models.CharField(max_length=60, verbose_name='نام')
    profile = models.ImageField(upload_to=profile_directory_path, null=True, blank=True, verbose_name='پروفایل', help_text='60*60')

    is_active = models.BooleanField(default=True, verbose_name='دسترسی به حساب')
    is_staff = models.BooleanField(default=False, verbose_name='کارمند سایت')
    is_superuser = models.BooleanField(default=False, verbose_name='صاحب سایت')

    date_joined = models.DateTimeField(default=timezone.now, verbose_name='تاریخ ایجاد حساب')

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
