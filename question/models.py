#-*- coding: utf-8 -*-
# Create your models here.
from django.db import models
from datetime import datetime
#from django.contrib.auth.models import User
from accounts import models as m

class Question(models.Model):
    questioner = models.ForeignKey(m.User)
    title = models.CharField('タイトル', max_length=512)
    text = models.TextField('質問内容')
    time_limit = models.TimeField('質問のタイムリミット')
    date = models.DateTimeField('質問日時', default=datetime.now)
    draft = models.BooleanField('下書き', default=False)

class Reply(models.Model):
    question = models.ForeignKey(Question)
    answerer = models.ForeignKey(m.User)
    text = models.TextField('返信内容')
    date = models.DateTimeField('返信日時', default=datetime.now)
    draft = models.BooleanField('下書き', default=False)

class ReplyList(models.Model):
    question = models.ForeignKey(Question)
    answerer = models.ForeignKey(m.User)
    time_limit_date = models.DateTimeField('返信期限')
    has_replied = models.BooleanField('返信済み', default=False)

class Tag(models.Model):
    name = models.CharField('タグ名', max_length=512)

class UserTag(models.Model):
    user = models.ForeignKey(m.User)
    tag = models.ForeignKey(Tag)

class QuestionTag(models.Model):
    question = models.ForeignKey(Question)
    tag = models.ForeignKey(Tag)
