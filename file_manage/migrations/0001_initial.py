# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-27 14:52
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('show_index', '查看首页数据'), ('create_dir', '可以创建文件夹'), ('rename_dir', '可以更改文件名'), ('delete_dir', '可以删除文件'), ('add_files', '可以上传文件'), ('mv_dir', '可以移动文件')),
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
