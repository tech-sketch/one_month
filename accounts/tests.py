from django.test import TestCase
#from unittest import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile, WorkPlace, WorkStatus, Division
from accounts.views import signup, login
from datetime import time, datetime
from django.http import HttpRequest
from django.test.client import Client
from accounts.forms import UserProfileForm, UserForm


class SignupTestCase(TestCase):

    def setUp(self):
        print('Set up 1')
        print()
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

    def test_signup_create_new_user(self):
        """正常な入力を行えばエラーにならないことを検証"""
        print('Test Case 1')
        print()
        c = Client()
        response = c.post('/accounts/signup/', {'username': 'signup_user', 'password': 'signup_user',
                                                'work_place': self.work_place01.id, 'division': self.division01.id, 'avatar': '', 'work_status': '1'})
        print(Division.objects.all())
        print(WorkPlace.objects.all())
        self.assertTrue(User.objects.filter(username='signup_user'))

    def test_signup_exist_user(self):
        """サインインを行いすでに存在するユーザを作成し失敗することの確認"""
        print('Test Case 2')
        print()
        c = Client()
        response = c.post('/accounts/signup/', {'username': '01', 'password': 'signup_user',
                                                'work_place': self.work_place01.id, 'division': self.division01.id, 'avatar': '', 'work_status': '1'})

        self.assertTrue(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='01'))

    def test_signup_incorrect_input(self):
        """サインインを行いすでに正しくない入力を行い失敗することの確認"""
        print('Test Case 3')
        print()
        c = Client()
        response = c.post('/accounts/signup/', {'username': '', 'password': 'signup_user',
                                                'work_place': self.work_place01.id, 'division': self.division01.id, 'avatar': '', 'work_status': '1'})

        self.assertTrue(response.status_code, 200)

from django.core.urlresolvers import reverse
class LoginTestCase(TestCase):

    def setUp(self):
        print('Set up 2')
        print()
        self.division01 = Division.objects.create(name='総務', code=1)
        self.work_place01 = WorkPlace.objects.create(name='東京')
        self.work_state01 = WorkStatus.objects.create(name='在籍')

        self.user01 = User.objects.create(username='01', last_login=datetime.now(), password='01')
        self.prof01 = UserProfile.objects.create(user=self.user01, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

        self.user02 = User.objects.create(username='02', last_login=datetime.now(), password='02')
        self.prof02 = UserProfile.objects.create(user=self.user02, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

    def test_login_exist_user(self):
        """存在するユーザでログイン画面からログインできるかの確認"""

        print('Test Case 4')
        print()
        c = Client()
        response = c.post('/accounts/login/', {'username':self.user01.username, 'password': self.user01.password})
        print("exist_user")
        print(response.context["user"])
        self.assertEqual(response.status_code, 200)

    def test_login_unknown_user(self):
        """存在しないユーザでログイン画面からログインできないの確認"""

        print('Test Case 5')
        print()
        c = Client()
        response = c.post('/accounts/login/', {'username': '00', 'password': '01'})
        print("unknown_user")
        print(response.context["user"])
        self.assertEqual(response.status_code, 200)