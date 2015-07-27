from django.test import TestCase
from django.contrib.auth.models import User
from datetime import time, datetime
from accounts.models import UserProfile, WorkPlace, WorkStatus, Division
from .models import QuestionDestination, QuestionTag, Question, Reply, ReplyList, Tag, UserTag
from .forms import QuestionEditForm, ReplyEditForm, UserProfileEditForm


class Reply_editTest(TestCase):
    def setUp(self):
        self.division01 = Division.objects.create(name='総務', code=1)
        self.work_place01 = WorkPlace.objects.create(name='東京')
        self.work_state01 = WorkStatus.objects.create(name='在籍')

        self.user01 = User.objects.create(username='01', last_login=datetime.now())
        self.prof01 = UserProfile.objects.create(user=self.user01, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

        self.user02 = User.objects.create(username='02', last_login=datetime.now())
        self.prof02 = UserProfile.objects.create(user=self.user02, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

    def test_reply_form(self):
        """正常な入力を行えばエラーにならないことを検証"""
        reply = Reply()
        form = ReplyEditForm(data={'date':datetime.now(), 'text': 'test', 'draft': 0}, instance=reply)
        print("=====reply_edit=====")
        print(form.errors)
        self.assertTrue(form.is_valid())

class Question_editTest(TestCase):
    def setUp(self):
        self.division01 = Division.objects.create(name='人事', code=2)
        self.division02 = Division.objects.create(name='総務', code=1)
        self.work_place01 = WorkPlace.objects.create(name='東京')
        self.work_state01 = WorkStatus.objects.create(name='在籍')

        self.user01 = User.objects.create(username='01', last_login=datetime.now())
        self.prof01 = UserProfile.objects.create(user=self.user01, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

        self.user02 = User.objects.create(username='02', last_login=datetime.now())
        self.prof02 = UserProfile.objects.create(user=self.user02, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

    def test_question_form(self):
        """正常な入力を行えばエラーにならないことを検証"""
        question = Question()
        form = QuestionEditForm(data={'destination': [1, 2], 'date':datetime.now(), 'title': 'test', 'time_limit': '11:11:11', 'text': 'test', 'draft': 0}, instance=question)
        print("=====question_edit=====")
        print(form.errors)
        self.assertTrue(form.is_valid())


class UserProfileEditFormTest(TestCase):
    def setUp(self):
        self.division01 = Division.objects.create(name='人事', code=2)
        self.division02 = Division.objects.create(name='総務', code=1)
        self.work_place01 = WorkPlace.objects.create(name='東京')
        self.work_state01 = WorkStatus.objects.create(name='在籍')

        self.user01 = User.objects.create(username='01', last_login=datetime.now())
        self.prof01 = UserProfile.objects.create(user=self.user01, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

        self.user02 = User.objects.create(username='02', last_login=datetime.now())
        self.prof02 = UserProfile.objects.create(user=self.user02, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

    def test_user_profile_form(self):
        """正常な入力を行えばエラーにならないことを検証"""
        profile = UserProfile()
        print(WorkPlace.objects.all())
        form = UserProfileEditForm(data={'work_place': self.work_place01.id, 'work_status': self.work_state01.id,  'division': self.division01.id, 'accept_question': 1 }, instance=profile)
        print("=====user_profile__edit=====")
        print(form.errors)
        self.assertTrue(form.is_valid())

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase
from question.views import *

class HtmlTests(TestCase):

    def test_show_page_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test',email=None, password='a')

        # 自分の質問を取ってくる
        questions = Question.objects.filter(questioner=request.user)
        # 自分宛の質問リストを取ってくる
        reply_lists = ReplyList.objects.filter(answerer=request.user)

        # 自分と自分宛の質問を結合して時系列に並べる
        qa_list = list()
        qa_list.extend(questions)
        qa_list.extend(reply_lists)
        qa_list = sorted(qa_list, reverse=True, key=lambda x: x[0].date if isinstance(x[0],Question) else x[0].question.date)#OK?


        # プロフィール
        for qa in qa_list:
            if isinstance(qa[0], Question):
                profile = UserProfile.objects.get(user=qa[0].questioner)
            elif isinstance(qa[0], ReplyList):
                profile = UserProfile.objects.get(user=qa[0].question.questioner)
            qa.append(profile)

        histories = None
        msg = None

        response = top_default(request)
        expected_html = render_to_string('question/top_all.html',
                              {'histories': histories, 'qa_list':qa_list,
                               'last_login': request.user.last_login, 'msg':msg},
                              context_instance=RequestContext(request))

        print(response.content.decode())
        print("------")
        print(expected_html)

        self.assertEqual(response.content.decode(), expected_html)
