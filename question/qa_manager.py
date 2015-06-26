#-*- coding: utf-8 -*-

from enum import Enum
from django.contrib.auth.models import User
from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag, QuestionDestination
from accounts.models import UserProfile
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned

import random, datetime, pytz



class QuestionState(Enum):
    pending = 0
    solved = 1
    unsolved = 2

class ReplyState(Enum):
    pending = 0
    replied = 1
    passed = 2

class QAManager():
    def __init__(self, user=None):
        self.user = user

    #その質問のQuestionStateを調べるメソッド
    def question_state(self, question_list):

        if isinstance(question_list, Question):
            print('[qa_manager:question_state] Warning: the arg is not a type Question!')
            print('[qa_manager:question_state] Returns None')
            return None

        qa_list = list()
        #自分の質問が解決済みかどうか調べる
        for q in question_list:
            r = Reply.objects.filter(question=q) # いまの仕様では返信は一つのはず
            if not q.is_closed and len(r): #返信が来たが未解決
                pass
            elif q.is_closed and len(r): #解決済み
                qa_list.append([q, QuestionState.solved.name])
            elif q.is_closed and not len(r):
                qa_list.append([q, QuestionState.unsolved.name]) #未解決
            else:
                qa_list.append([q, QuestionState.pending.name]) #回答待ち
        return qa_list

    #その質問のReplyStateを調べるメソッド
    def reply_state(self, reply_list):

        if isinstance(reply_list, ReplyList):
            print('[qa_manager:reply_state] Warning: the arg is not a type Question!')
            print('[qa_manager:reply_state] Returns None')
            return None

        qa_list = list()

        for rl in reply_list:
            if not rl.has_replied:
                qa_list.append([rl, ReplyState.pending.name])
            else:
                r = Reply.objects.filter(question=rl.question, answerer=self.user) #最大一つしか出てこないはず
                if len(r): #自分が回答した
                    qa_list.append([rl, ReplyState.replied.name])
                else: # パスした
                    qa_list.append([rl, ReplyState.passed.name])

        return qa_list

    #全ユーザーの中からランダムに返信ユーザーを決定する。（u:User 対象としたくないユーザー, q:Question）
    def reply_list_update_random(self, u, q):

        candidate_users = User.objects.filter(~Q(username=u)).filter(~Q(username=q.questioner))

        try:
            r_list = ReplyList()
            r_list.answerer = random.choice(candidate_users)
            r_list.question = q
            r_list.time_limit_date = datetime.datetime.now() + datetime.timedelta(hours=q.time_limit.hour, minutes=q.time_limit.minute, seconds=q.time_limit.second)
            return r_list
        except IndexError:
            return None

    def reply_list_update_random_except(self, users, question):
        """
        指定されたユーザリストの中からランダムに次の回答ユーザを決定する。
        """
        if not users:
            return None

        r_list = ReplyList()
        r_list.answerer = random.choice(users)
        r_list.question = question
        r_list.time_limit_date = datetime.datetime.now() + datetime.timedelta(
                                    hours=question.time_limit.hour,
                                    minutes=question.time_limit.minute,
                                    seconds=question.time_limit.second)
        return r_list

    def pass_question(self, passed_question, reply_list_update):
        if passed_question.is_closed:
            return

        try:
            reply_list = ReplyList.objects.get(question=passed_question, has_replied=False)
            reply_list.has_replied = True
            reply_list.save()

            reply_user_list = []

            for qd in QuestionDestination.objects.filter(question=passed_question):
                reply_user_list.extend([up.user for up in UserProfile.objects.filter(accept_question=1).filter(division=qd.tag)])#質問の送信範囲のユーザ
            passed_user_list = [rl.answerer for rl in ReplyList.objects.filter(question=passed_question, has_replied=True)]#質問にすでにパスしたユーザ
            passed_user_list.append(passed_question.questioner)#質問者
            no_login_users = User.objects.exclude(last_login__gte=(datetime.datetime.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)))#ログインしていないユーザ

            reply_user_list = list((set(reply_user_list) - set(passed_user_list)) - set(no_login_users))

            next_reply_list = reply_list_update(reply_user_list, passed_question)
            if next_reply_list != None:
                next_reply_list.save()
                print('{0}からの質問「{1}」を{2}から{3}にパスしました。 タイムリミットは{4}'.format(reply_list.question.questioner, reply_list.question.title, reply_list.answerer, next_reply_list.answerer, reply_list.time_limit_date))
                return True
            else:
                print('パスできませんでした')
                return False

        except MultipleObjectsReturned:
            print("ReplyListの値が不正です")
            return

    def make_reply_list(self, question, reply_list_update):

        reply_user_list = []

        for qd in QuestionDestination.objects.filter(question=question):
            reply_user_list.extend([up.user for up in UserProfile.objects.filter(accept_question=1).filter(division=qd.tag)])#質問の送信範囲のユーザ
        if question.questioner in reply_user_list: reply_user_list.remove(question.questioner)
        no_login_users = User.objects.exclude(last_login__gte=(datetime.datetime.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)))#ログインしていないユーザ

        reply_user_list = list(set(reply_user_list) - set(no_login_users))

        print(reply_user_list)

        return reply_list_update(reply_user_list, question)