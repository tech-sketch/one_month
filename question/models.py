# -*- coding: utf-8 -*-
# Create your models here.
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from accounts.models import Division

import datetime as t
from datetime import datetime

class Question(models.Model):
    questioner = models.ForeignKey(User, verbose_name='質問者')
    title = models.CharField('タイトル', max_length=512)
    text = models.TextField('質問内容')
    time_limit = models.TimeField('質問のタイムリミット')
    date = models.DateTimeField('質問日時', default=datetime.now)
    draft = models.BooleanField('下書き', default=False)
    is_closed = models.BooleanField('募集終了', default=False)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()

    def pass_counter(self):
        return ReplyList.objects.filter(question=self, has_replied=True).count()

    def get_tags_name(self):
        return [x.tag.name for x in QuestionTag.objects.filter(question=self)]

    @staticmethod
    def search_by_keyword(keyword):
        return list(Question.objects.filter(Q(title__contains=keyword) | Q(text__contains=keyword)))

    def has_reply(self):
        return len(Reply.objects.filter(question=self)) != 0
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

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()

    @staticmethod
    def search_by_keyword(keyword):
        return list(Reply.objects.filter(Q(text__contains=keyword)))

class ReplyList(models.Model):
    question = models.ForeignKey(Question, verbose_name='質問')
    answerer = models.ForeignKey(User, verbose_name='返答ユーザ')
    time_limit_date = models.DateTimeField('返信期限', null=True)
    has_replied = models.BooleanField('返信済み', default=False)

    def __str__(self):
        return u'%sへ「%s」についてのリプライリスト' % (self.question.questioner, self.question.title)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()

class Tag(models.Model):
    name = models.CharField('タグ名', max_length=512)

    def __str__(self):
        return u'{}'.format(self.name)

    @staticmethod
    def get_all_tags_name():
        tags = Tag.objects.all()
        return [t.name for t in tags]

    @staticmethod
    def get_tags_by_name(tagname):
        return Tag.objects.filter(Q(name__contains=tagname))

class UserTag(models.Model):
    user = models.ForeignKey(User, verbose_name='ユーザ')
    tag = models.ForeignKey(Tag, verbose_name='タグ')

    def __str__(self):
        return u'{}に{}タグ追加'.format(self.user, self.tag)

    @staticmethod
    def get_user_all_tags_name(user):
        utags = UserTag.objects.filter(user=user)
        return [t.tag.name for t in utags]

class QuestionTag(models.Model):
    question = models.ForeignKey(Question, verbose_name='質問')
    tag = models.ForeignKey(Tag, verbose_name='タグ')

    def __str__(self):
        return u'{}に{}タグ追加'.format(self.question, self.tag)

    @staticmethod
    def get_question_all_tags_name(question):
        qtags = QuestionTag.objects.filter(question=question)
        return [t.tag.name for t in qtags]

    @staticmethod
    def get_questions_by_tag(tag):
        return QuestionTag.objects.filter(tag=tag)