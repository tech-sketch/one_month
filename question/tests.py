from django.test import TestCase
from django.contrib.auth.models import User
from datetime import time, datetime
from accounts.models import UserProfile, WorkPlace, WorkStatus, Division
from .models import QuestionDestination, QuestionTag, Question, Reply, ReplyList, Tag, UserTag
from .forms import QuestionEditForm, ReplyEditForm, UserProfileEditForm
from. import views


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