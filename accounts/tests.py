from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile, WorkPlace, WorkStatus, Division
from accounts.forms import UserProfileForm, UserForm
from django.test.client import Client


class SignupTestCase(TestCase):

    def setUp(self):
        print('Set up 1')
        print()
        self.division01 = Division.objects.create(name='総務', code=1)
        self.work_place01 = WorkPlace.objects.create(name='東京')
        self.work_state01 = WorkStatus.objects.create(name='在籍')

        self.user01 = User.objects.create_user('01', '01@01.com', '01')
        self.prof01 = UserProfile.objects.create(user=self.user01, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

    def test_signup_create_new_user(self):
        """正常な入力を行えばエラーにならないことを検証"""
        print('Test Case 1')
        print()
        c = Client()
        response = c.post('/accounts/signup/', {'username': 'signup_user', 'password': 'signup_user',
                                                'work_place': self.work_place01.id, 'division': self.division01.id,
                                                'avatar': '', 'work_status': '1'})
        self.assertRedirects(response, '/accounts/login/', status_code=302, target_status_code=200)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='signup_user'))

    def test_signup_exist_user(self):
        """サインインを行いすでに存在するユーザを作成し失敗することの確認"""
        print('Test Case 2')
        print()
        c = Client()
        response = c.post('/accounts/signup/', {'username': '01', 'password': 'signup_user',
                                                'work_place': self.work_place01.id, 'division': self.division01.id,
                                                'avatar': '', 'work_status': '1'})
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertTrue(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='01'))

    def test_signup_incorrect_input(self):
        """サインインを行いすでに正しくない入力を行い失敗することの確認"""
        print('Test Case 3')
        print()
        c = Client()
        response = c.post('/accounts/signup/', {'username': '', 'password': 'signup_user',
                                                'work_place': self.work_place01.id, 'division': self.division01.id,
                                                'avatar': '', 'work_status': '1'})
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertTrue(response.status_code, 200)


class LoginTestCase(TestCase):

    def setUp(self):
        print('Set up 2')
        print()
        self.division01 = Division.objects.create(name='総務', code=1)
        self.work_place01 = WorkPlace.objects.create(name='東京')
        self.work_state01 = WorkStatus.objects.create(name='在籍')

        self.user01 = User.objects.create_user('01', '01@01.com', '01')
        self.prof01 = UserProfile.objects.create(user=self.user01, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

    def test_login_exist_user(self):
        """ 存在するユーザでログイン画面からログインできるかの確認 """

        print('Test Case 4')
        print()
        c = Client()
        response = c.post('/accounts/login/', {'username': '01', 'password': '01'})
        self.assertRedirects(response, '/dotchain/', status_code=302, target_status_code=200)

    def test_login_unknown_user(self):
        """ 存在しないユーザでログイン画面からログインできないの確認 """
        print('Test Case 5')
        print()
        c = Client()
        response = c.post('/accounts/login/', {'username': '00', 'password': '01'})
        m = list(response.context['messages'])
        self.assertEqual(str(m[0]), '正しいユーザ名・パスワードを入力してください。')


class UserProfileFormTest(TestCase):
    def setUp(self):
        print('Set up 3')
        print()
        self.division01 = Division.objects.create(name='総務', code=1)
        self.work_place01 = WorkPlace.objects.create(name='東京')
        self.work_state01 = WorkStatus.objects.create(name='在籍')

        self.user01 = User.objects.create_user('01', '01@01.com', '01')
        self.prof01 = UserProfile.objects.create(user=self.user01, work_place=self.work_place01,
                                                 work_status=self.work_state01, division=self.division01,
                                                 accept_question=1)

    def test_success_user_profile_form(self):
        """正常な入力を行いエラーにならないことを検証"""
        print('Test Case 3-1')
        print()
        profile = UserProfile()
        form = UserProfileForm(data={'work_place': self.work_place01.id, 'work_status': self.work_state01.id,  'division': self.division01.id}, instance=profile)
        self.assertTrue(form.is_valid())

    def test_failure_user_profile_form(self):
        """正常ではない入力を行いエラーになることを検証"""
        print('Test Case 3-2')
        print()
        profile = UserProfile()
        form = UserProfileForm(data={'work_place': '', 'work_status': self.work_state01.id,  'division': self.division01.id}, instance=profile)
        self.assertTrue(not(form.is_valid()))
