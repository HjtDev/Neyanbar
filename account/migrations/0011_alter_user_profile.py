# Generated by Django 5.2 on 2025-06-06 07:29

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_alter_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile',
            field=models.ImageField(default='Profiles/default-1.webp', help_text='60*60', upload_to=account.models.profile_directory_path, verbose_name='پروفایل'),
        ),
    ]
