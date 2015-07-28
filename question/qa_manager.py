# -*- coding: utf-8 -*-

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

class QAManager:
    def __init__(self, user=None):
        self.user = user

    # その質問のQuestionStateを調べるメソッド
    def question_state(self, question_list):

        qa_list = list()
        # 自分の質問が解決済みかどうか調べる
        for q in question_list:
            r = Reply.objects.filter(question=q)  # いまの仕様では返信は一つのはず
            if not q.is_closed and len(r):  # 返信が来たが未解決
                qa_list.append([q, QuestionState.pending.name])  # 回答待ち
            elif q.is_closed and len(r):
                qa_list.append([q, QuestionState.solved.name])  # 解決済み
            elif q.is_closed and not len(r):
                qa_list.append([q, QuestionState.unsolved.name])  # 未解決
            else:
                qa_list.append([q, QuestionState.pending.name])  # 回答待ち

        #  プロフィールを追加
        self.__append_profile(qa_list)

        return qa_list

    # その質問のReplyStateを調べるメソッド
    def reply_state(self, reply_list):

        qa_list = list()

        for rl in reply_list:
            if not rl.has_replied:
                qa_list.append([rl, ReplyState.pending.name])
            else:
                r = Reply.objects.filter(question=rl.question, answerer=self.user)
                if len(r):
                    qa_list.append([rl, ReplyState.replied.name]) #自分が回答した
                else:
                    qa_list.append([rl, ReplyState.passed.name]) # パスした

        #  プロフィールを追加
        self.__append_profile(qa_list)

        return qa_list

    # 全ユーザーの中からランダムに返信ユーザーを決定する。（u:User 対象としたくないユーザー, q:Question）
    def reply_list_update_random(self, u, q):

        candidate_users = User.objects.filter(~Q(username=u)).filter(~Q(username=q.questioner))

        try:
            r_list = ReplyList()
            r_list.answerer = random.choice(candidate_users)
            r_list.question = q
            r_list.time_limit_date = datetime.datetime.now() + datetime.timedelta(hours=q.time_limit.hour,
                                                                                  minutes=q.time_limit.minute,
                                                                                  seconds=q.time_limit.second)
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
        r_list.time_limit_date = datetime.datetime.now() + datetime.timedelta(hours=question.time_limit.hour,
                                                                              minutes=question.time_limit.minute,
                                                                              seconds=question.time_limit.second)
        return r_list

    def pass_question(self, passed_question, reply_list_update):
        """
        指定された質問の返信リストを指定した返信リスト更新関数で更新する
        """
        if passed_question.is_closed:
            return

        try:
            reply_list = ReplyList.objects.get(question=passed_question, has_replied=False)
            reply_list.has_replied = True
            reply_list.save()

            reply_user_list = []

            for qd in QuestionDestination.objects.filter(question=passed_question):
                reply_user_list.extend([up.user for up in UserProfile.objects.filter(accept_question=1)
                                       .filter(division=qd.tag)])  # 質問の送信範囲のユーザ
            passed_user_list = [rl.answerer for rl in ReplyList.objects.filter(
                question=passed_question, has_replied=True)]  # 質問にすでにパスしたユーザ
            passed_user_list.append(passed_question.questioner)  # 質問者
            no_login_users = User.objects.exclude(last_login__gte=(datetime.datetime.now() - datetime.timedelta(
                hours=23, minutes=59, seconds=59)))  # ログインしていないユーザ

            reply_user_list = list((set(reply_user_list) - set(passed_user_list)) - set(no_login_users))

            next_reply_list = reply_list_update(reply_user_list, passed_question)
            if next_reply_list != None:
                next_reply_list.save()
                print('{0}からの質問「{1}」を{2}から{3}にパスしました。 タイムリミットは{4}'.format(reply_list.question.questioner, reply_list.question.title, reply_list.answerer, next_reply_list.answerer, reply_list.time_limit_date))
                return True
            else:
                passed_question.is_closed = True
                passed_question.save()
                print('パスできませんでした')
                return False

        except MultipleObjectsReturned:
            print("ReplyListの値が不正です")
            return

    def make_reply_list(self, question, reply_list_update):

        reply_user_list = []

        for qd in QuestionDestination.objects.filter(question=question):
            reply_user_list.extend([up.user for up in UserProfile.objects.filter(accept_question=1).filter(
                division=qd.tag)])  # 質問の送信範囲のユーザ
        if question.questioner in reply_user_list: reply_user_list.remove(question.questioner)
        no_login_users = User.objects.exclude(last_login__gte=(datetime.datetime.now() - datetime.timedelta(
            hours=23, minutes=59, seconds=59)))  # ログインしていないユーザ

        reply_user_list = list(set(reply_user_list) - set(no_login_users))

        print(reply_user_list)

        return reply_list_update(reply_user_list, question)

    @staticmethod
    def sort_qa(qa_list, reverse=False):

        if len(qa_list) == 0:
            print('[Warning] QAManager:sort_qa() qa_list length is 0!')
            return None
        elif not isinstance(qa_list, list):
            return sorted(qa_list, reverse=reverse,
                     key=lambda x: x.date if isinstance(x, Question) else x.question.date)
        else:
            return sorted(qa_list, reverse=reverse,
                     key=lambda x: x[0].date if isinstance(x[0], Question) else x[0].question.date)

    @staticmethod
    def search_question_by_keyword(keyword, questioner):
        """
        キーワードに合致するすべての質問のうち、ユーザが投稿した質問を取り出す
        """
        questions = Question.search_by_keyword(keyword=keyword)
        q_list = []
        for q in questions:
            if q.questioner == questioner:
                q_list.append(q)
        return q_list

    @staticmethod
    def search_question_by_tag_keyword(keyword, questioner):
        """
        キーワードに合致するすべてのタグのうち、自分が投稿した質問のタグと一致するもののみ取り出す
        """
        tags = Tag.get_tags_by_name(tagname=keyword)
        q_list = []
        for tag in tags:
            q_tags = QuestionTag.get_questions_by_tag(tag=tag)
            q = [q_tag.question for q_tag in q_tags if q_tag.question.questioner == questioner]
            q_list.extend(q)

        return list(set(q_list))

    @staticmethod
    def search_replylist_by_keyword_extra(keyword, questioner, answerer):
        """
        キーワードに合致する回答のうち、自分の回答、または自分が投稿した質問の回答に関連づいた質問のReplyListのみ取り出す
        """
        replies = Reply.search_by_keyword(keyword=keyword)
        r_list = []
        for r in replies:
            if r.answerer == answerer:
                reply_lists = ReplyList.objects.filter(answerer=answerer)
                rl = [rl for rl in reply_lists if r.question.id == rl.question.id]
                r_list.extend(rl)
            elif r.question.questioner == questioner:
                reply_lists = ReplyList.objects.filter(question=r.question)
                rl = [rl for rl in reply_lists if r.question.id == rl.question.id]
                r_list.extend(rl)

        return list(set(r_list))

    @staticmethod
    def search_replylist_by_keyword(keyword, answerer):
        """
        キーワードに合致するすべての質問のうち、宛先が自分になっているReplyListを取り出す
        """
        questions = Question.search_by_keyword(keyword=keyword)
        reply_lists = ReplyList.objects.filter(answerer=answerer)
        r_list = []
        for q in questions:
            rl = [rl for rl in reply_lists if q.id == rl.question.id]
            r_list.extend(rl)
        return r_list

    @staticmethod
    def search_replylist_by_tag_keyword(keyword, answerer):
        """
        自分に来た（回答したものも含む）質問のタグと一致するもののみ取り出す
        """
        tags = Tag.get_tags_by_name(tagname=keyword)
        r_list = ReplyList.objects.filter(answerer=answerer)
        r_list_tmp = []
        for tag in tags:
            q_tags = QuestionTag.get_questions_by_tag(tag=tag)
            for rl in r_list:
                for q_tag in q_tags:
                    if rl.question.id == q_tag.question.id:
                        r_list_tmp.append(rl)

        return list(set(r_list_tmp))

    def __append_profile(self, qa_list):

        for qa in qa_list:
            if isinstance(qa[0], Question):
                profile = UserProfile.objects.get(user=qa[0].questioner)
            elif isinstance(qa[0], ReplyList):
                profile = UserProfile.objects.get(user=qa[0].question.questioner)
            qa.append(profile)