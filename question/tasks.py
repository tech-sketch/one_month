# -*- coding: utf-8 -*-

import time
from django.shortcuts import render_to_response, redirect, get_object_or_404
from question.models import Question, Reply, ReplyList
from accounts.models import User
from django.db.models import Q
import random
import datetime

from celery import task

"""
別ターミナルで

python manage.py celeryd -l info

でceleryを起動してね
"""

@task
def add(a, b):
    time.sleep(10)
    return a + b

@task
def countdown(r_list):
    """
    このメソッドでまだタイムリミット時間内か、もしくはパスされたかわかる
    (1) ready()=False, ならまだカウントダウン中
    (2) ready()=True, result.get()=Trueなら時間内にパスされたor返信があった
    (3) ready()=False, result.get()=Falseなら、タイムリミットが過ぎた
    """
    print("a")
    time_limit_day = r_list.time_limit_date
    id = r_list.id
    #q = get_object_or_404(Question, id=r_list.question.id)
    q = Question.objects.get(id=r_list.question.id)
    print("b")
    while True:
        # この回答リストは更新される可能性があるため毎回取ってくる
        #w = get_object_or_404(ReplyList, question=q, has_replied=False)
        w = ReplyList.objects.get(id=id)
        print("c")
        # 待ちの間にパスになったら
        if w.has_replied:
            print("d")
            # 返信済みをTrueにする
            w.has_replied = True
            w.save()

            # 新しく回答リストを生成
            r_list_new = ReplyList()
            rand_user = User.objects.filter(~Q(username=r_list.answerer)).filter(~Q(username=q.questioner)) #TODO 質問者以外かつ今まで選ばれた人以外の人を選ぶ
            r_list_new.answerer = random.choice(rand_user) #ランダム
            r_list_new.question = r_list.question
            r_list_new.time_limit_date = datetime.datetime.now() + datetime.timedelta(hours=q.time_limit.hour, minutes=q.time_limit.minute, seconds=q.time_limit.second)
            r_list_new.save()

            # 再起
            countdown(r_list_new)

            return True #(2)

        try:
            r = Reply.objects.get(question=w.question)[0]
        except Reply.DoesNotExist:
            r = None

        if r != None:
            return;

        # 負荷軽減のため
        time.sleep(1)
    # whileここまで

    r_list.has_replied = True
    r_list.save()

    # 新しく回答リストを生成
    r_list_new = ReplyList()
    rand_user = User.objects.filter(~Q(username=r_list.answerer)).filter(~Q(username=q.questioner)) #TODO 質問者以外かつ今まで選ばれた人以外の人を選ぶ
    r_list_new.answerer = random.choice(rand_user) #ランダム
    r_list_new.question = r_list.question
    r_list_new.time_limit_date = datetime.datetime.now() + datetime.timedelta(hours=q.time_limit.hour, minutes=q.time_limit.minute, seconds=q.time_limit.second)
    r_list_new.save()

    countdown(r_list_new)

    return False # (3)