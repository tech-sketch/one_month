# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=512, verbose_name='タイトル')),
                ('text', models.TextField(verbose_name='質問内容')),
                ('time_limit', models.TimeField(verbose_name='質問のタイムリミット')),
                ('date', models.DateTimeField(verbose_name='質問日時', default=datetime.datetime.now)),
                ('draft', models.BooleanField(verbose_name='下書き', default=False)),
                ('questioner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('text', models.TextField(verbose_name='返信内容')),
                ('date', models.DateTimeField(verbose_name='返信日時', default=datetime.datetime.now)),
                ('draft', models.BooleanField(verbose_name='下書き', default=False)),
                ('answerer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(to='question.Question')),
            ],
        ),
    ]
