# Generated by Django 5.2 on 2025-05-07 05:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_alter_product_available_volumes_alter_product_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='site_score',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='امتیاز سایت'),
        ),
    ]
