#-*- coding: utf-8 -*-
from django.contrib.auth.models import User

from accounts.models import UserProfile, WorkStatus, WorkPlace, Division


def startup():

    # create fields for master DB
    work_place, created = WorkPlace.objects.get_or_create(name='東京', defaults=dict(name='東京', ), )
    WorkPlace.objects.get_or_create(name='大阪', defaults=dict(name='大阪', ), )
    WorkPlace.objects.get_or_create(name='名古屋', defaults=dict(name='名古屋', ), )
    WorkPlace.objects.get_or_create(name='福岡', defaults=dict(name='福岡', ), )

    work_status, created = WorkStatus.objects.get_or_create(name='在席', defaults=dict(name='在席', ), )
    WorkStatus.objects.get_or_create(name='リモート', defaults=dict(name='リモート', ), )
    WorkStatus.objects.get_or_create(name='出張中', defaults=dict(name='出張中', ), )
    WorkStatus.objects.get_or_create(name='休暇中', defaults=dict(name='休暇中', ), )

    division, created = Division.objects.get_or_create(code=2, name='人事', defaults=dict(code=2, name='人事'))
    Division.objects.get_or_create(code=1, name='総務', defaults=dict(code=1, name='総務'))
    Division.objects.get_or_create(code=3, name='開発', defaults=dict(code=3, name='開発'))
    Division.objects.get_or_create(code=4, name='研究', defaults=dict(code=4, name='研究'))
    Division.objects.get_or_create(code=99, name='ロボット', defaults=dict(code=99, name='ロボット'))

    # create user profile
    users = User.objects.all()
    for user in users:
        p, created = UserProfile.objects.get_or_create(user=user,
                                                       defaults=dict(avatar='images/icons/no_image.png',
                                                                     work_place=work_place,
                                                                     work_status=work_status,
                                                                     division=division,
                                                                     accept_question=1, ), )