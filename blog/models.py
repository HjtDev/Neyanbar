from django.db import models
from account.models import User
import os
from datetime import datetime
import jdatetime
from tinymce.models import HTMLField
from django.shortcuts import reverse



class Tag(models.Model):
    name = models.CharField(max_length=60, verbose_name='تگ')
    slug = models.SlugField(max_length=60, unique=True, verbose_name='اسلاگ')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'تگ'
        verbose_name_plural = 'تگ ها'


class Category(models.Model):
    name = models.CharField(max_length=60, verbose_name='دسته بندی')
    slug = models.SlugField(max_length=60, unique=True, verbose_name='اسلاگ')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'


def user_directory_path(instance, filename):
    gnow = datetime.now()
    jnow = jdatetime.GregorianToJalali(gnow.year, gnow.month, gnow.day)
    return os.path.join(
        'Blog',
        f'user_{instance.user.id}',
        str(jnow.jyear),
        str(jnow.jmonth).zfill(2),
        str(jnow.jday).zfill(2),
        'thumbnail',
        filename
    )


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='posts', verbose_name='نویسنده')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name='دسته بندی', blank=True, null=True, related_name='posts')
    thumbnail = models.ImageField(upload_to=user_directory_path, verbose_name='تصویر تیتر', help_text='880*450')
    title = models.CharField(max_length=255)
    short_content = models.TextField(max_length=320, verbose_name='توضیحات کوتاه', help_text='پیش نمایش متن | حداکثر ۳۲۰ کاراکتر', blank=True)
    content = HTMLField(verbose_name='متن')
    author_comment = HTMLField(verbose_name='نظر نویسنده', blank=True, null=True)
    tags = models.ManyToManyField(Tag, verbose_name='برچسب ها', related_name='posts', blank=True)
    slug = models.SlugField(max_length=255, unique=True, verbose_name='اسلاگ')
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=False, verbose_name='نمایش در سایت')
    views = models.PositiveIntegerField(default=0, verbose_name='بازدید')

    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'پست'
        verbose_name_plural = 'پست ها'
