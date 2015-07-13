#-*- coding: utf-8 -*-
# Create your models here.
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from accounts.models import Division
import datetime as t
class Question(models.Model):
    questioner = models.ForeignKey(User, verbose_name='質問者')
    title = models.CharField('タイトル', max_length=512)
    text = models.TextField('質問内容')
    time_limit = models.TimeField('質問のタイムリミット')
    date = models.DateTimeField('質問日時', default=datetime.now)
    draft = models.BooleanField('下書き', default=False)
    is_closed = models.BooleanField('募集終了', default=False)

    def pass_counter(self):
        return ReplyList.objects.filter(question=self, has_replied=True).count()

    """
    def __str__(self):
        return u'%sから%sへ「%s」についての質問' % (self.questioner, self.destination_div, self.title)
    """

class QuestionDestination(models.Model):
    question = models.ForeignKey(Question, verbose_name='質問')
    tag = models.ForeignKey(Division, verbose_name='宛先所属コード')

class Reply(models.Model):
    question = models.ForeignKey(Question, verbose_name='質問')
    answerer = models.ForeignKey(User, verbose_name='返答ユーザ')
    text = models.TextField('返信内容')
    date = models.DateTimeField('返信日時', default=datetime.now)
    draft = models.BooleanField('下書き', default=False)

    def __str__(self):
        return u'%sへ「%s」についての回答' % (self.question.questioner, self.question.title)

class ReplyList(models.Model):
    question = models.ForeignKey(Question, verbose_name='質問')
    answerer = models.ForeignKey(User, verbose_name='返答ユーザ')
    time_limit_date = models.DateTimeField('返信期限', null=True)
    has_replied = models.BooleanField('返信済み', default=False)

    def __str__(self):
        return u'%sへ「%s」についてのリプライリスト' % (self.question.questioner, self.question.title)

class Tag(models.Model):
    name = models.CharField('タグ名', max_length=512)


    def __str__(self):
        return u'%s' % (self.name)

class UserTag(models.Model):
    user = models.ForeignKey(User, verbose_name='ユーザ')
    tag = models.ForeignKey(Tag, verbose_name='タグ')
    def __str__(self):
        return u'%sに%sタグ追加' % (self.user, self.tag)

class QuestionTag(models.Model):
    question = models.ForeignKey(Question, verbose_name='質問')
    tag = models.ForeignKey(Tag, verbose_name='タグ')

    def __str__(self):
        return u'%sに%sタグ追加' % (self.question, self.tag)
