# Generated by Django 5.2 on 2025-05-05 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.brand', verbose_name='برند'),
        ),
    ]
