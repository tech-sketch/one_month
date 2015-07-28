#-*- coding: utf-8 -*-
from django.contrib.auth.models import User

from accounts.models import UserProfile, WorkStatus, WorkPlace, Division
from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag, QuestionDestination

# ユーザのプロファイルを取ってくる
work_place, created = WorkPlace.objects.get_or_create(name='東京', defaults=dict(name='東京', ), )
work_status, created = WorkStatus.objects.get_or_create(name='在席', defaults=dict(name='在席', ), )
division, created = Division.objects.get_or_create(code=2, name='人事', defaults=dict(code=2, name='人事'))

users = User.objects.all()

for user in users:
    p, created = UserProfile.objects.get_or_create(user=user,
                                                   defaults=dict(avatar='images/icons/pepper.png',
                                                                 work_place=work_place,
                                                                 work_status=work_status,
                                                                 division=division,
                                                                 accept_question=1, ), )
