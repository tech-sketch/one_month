# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(verbose_name='タイトル', max_length=512)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('text', models.TextField(verbose_name='返信内容')),
                ('date', models.DateTimeField(verbose_name='返信日時', default=datetime.datetime.now)),
                ('draft', models.BooleanField(verbose_name='下書き', default=False)),
                ('answerer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(to='question.Question')),
            ],
        ),
        migrations.CreateModel(
            name='ReplyList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time_limit_date', models.DateTimeField(verbose_name='返信日時', default=datetime.datetime.now)),
                ('has_replied', models.BooleanField(verbose_name='返信済み', default=False)),
                ('answerer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(to='question.Question')),
            ],
        ),
    ]
