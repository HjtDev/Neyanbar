# Generated by Django 5.2 on 2025-05-29 13:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_alter_creditcart_created_by'),
        ('shop', '0022_alter_productsmell_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='volume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='shop.volume', verbose_name='حجم'),
        ),
    ]
