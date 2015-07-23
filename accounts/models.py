# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

# 勤務先マスタ
class WorkPlace(models.Model):
    CHOICES = (
        ('東京', '東京'),
        ('名古屋', '名古屋'),
        ('大阪', '大阪'),
        ('福岡', '福岡'),
    )
    name = models.CharField('勤務先', max_length=512, choices=CHOICES, default='東京')

    def __str__(self):
        return u'%s' % (self.name)

# 部署マスタ
class Division(models.Model):
    CODE_CHOICES = (
        (1, '総務'),
        (2, '人事'),
        (3, '開発'),
        (4, '研究'),
        (99, 'ロボット'),
    )
    # ロボットは code がもっとも大きな値で設定する。
    name = models.CharField('所属部署名', blank=True, max_length=512)
    code = models.IntegerField('所属コード', choices=CODE_CHOICES, default=3)

    def __str__(self):
        return u'%s' % (self.name)
    class Meta:
        ordering = ["code"]

# 勤務形態マスタ
class WorkStatus(models.Model):
    CHOICES = (
        ('在席', '在席'),
        ('リモート', 'リモート'),
        ('出張中', '出張中' ),
        ('休暇中', '休暇中'),
    )
    name = models.CharField('勤務形態', max_length=512, choices=CHOICES, default='在席')

    def __str__(self):
        return u'%s' % (self.name)

def work_place_default():
    try:
        item, created = WorkPlace.objects.get_or_create(name='東京')
        return item
    except:
        return None

def work_status_default():
    try:
        item, created = WorkStatus.objects.get_or_create(name='在席')
        return item
    except:
        return None

def division_default():
    try:
        item, created = Division.objects.get_or_create(code=2, name='人事')
        return item
    except:
        return None

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    avatar = models.ImageField(upload_to='images/icons', default='images/icons/no_image.png')
    work_place = models.ForeignKey(WorkPlace, verbose_name='勤務先', null=True, default=work_place_default())
    work_status = models.ForeignKey(WorkStatus, verbose_name='勤務形態', null=True, default=work_status_default())
    division = models.ForeignKey(Division, verbose_name='所属コード', null=True,  default=division_default())
    accept_question = models.IntegerField('受信可', default=1) # 0:不可, 1:可

    def __str__(self):
        return u'%sのプロフィール' % (self.user.username)
