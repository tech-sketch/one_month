#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

"""
    これをやると、objects.filterがうまくはたらかないみたい
    def __str__(self):
        return u'%s(%s %s)' % (self.username, self.first_name, self.last_name)
"""

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

class UserProfile(models.Model):

    user = models.ForeignKey(User)
    avatar = models.ImageField(upload_to='images/icons', default='images/icons/no_image.png')
    work_place = models.ForeignKey(WorkPlace, verbose_name='勤務先', null=True)
    work_status = models.ForeignKey(WorkStatus, verbose_name='勤務形態', null=True)
    division = models.ForeignKey(Division, verbose_name='所属コード', null=True)
    accept_question = models.IntegerField('受信可', default=1) # 0:不可, 1:可

    def __str__(self):
        return u'%s %sのプロフィール' % (self.user.first_name, self.user.last_name)
