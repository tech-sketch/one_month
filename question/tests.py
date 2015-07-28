from datetime import time, datetime
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase
from question.views import *
from question import message_definition as m

class HtmlTests(TestCase):
    """
    各メソッドで正しいHTMLが返されているかテスト。
    """

    def test_top_default_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        questions = Question.objects.filter(questioner=request.user)
        reply_lists = ReplyList.objects.filter(answerer=request.user)

        qa_list = list()
        qa_list.extend(questions)
        qa_list.extend(reply_lists)
        qa_list = sorted(qa_list, reverse=True,
                         key=lambda x: x[0].date if isinstance(x[0], Question) else x[0].question.date)

        for qa in qa_list:
            if isinstance(qa[0], Question):
                profile = UserProfile.objects.get(user=qa[0].questioner)
            elif isinstance(qa[0], ReplyList):
                profile = UserProfile.objects.get(user=qa[0].question.questioner)
            qa.append(profile)

        msg = m.INFO_PASS_FINISH

        response = top_default(request, msg)
        expected_html = render_to_string('question/top_all.html',
                                         {'qa_list': qa_list,
                                          'last_login': request.user.last_login, 'msg': msg},
                                         context_instance=RequestContext(request))

        self.assertEqual(response.content.decode(), expected_html)

    def test_question_list_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        q = Question.objects.filter(questioner=request.user).order_by('date')

        q_manager = QAManager(request.user)
        qa_list = q_manager.question_state(q)
        qa_list = sorted(qa_list, reverse=True,
                         key=lambda x: x[0].date if isinstance(x[0], Question) else x[0].question.date)

        for qa in qa_list:
            if isinstance(qa[0], Question):
                profile = UserProfile.objects.get(user=qa[0].questioner)
            elif isinstance(qa[0], ReplyList):
                profile = UserProfile.objects.get(user=qa[0].question.questioner)
            qa.append(profile)

        response = question_list(request)
        expected_html = render_to_string('question/top_q.html',
                                         {'qa_list': qa_list,
                                          'last_login': request.user.last_login},
                                         context_instance=RequestContext(request))

        self.assertEqual(response.content.decode(), expected_html)

    def test_reply_list_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        reply_list = ReplyList.objects.filter(answerer=request.user, has_replied=False)
        reply_list = sorted(reply_list, reverse=True, key=lambda x: x.question.date)

        q_manager = QAManager(request.user)
        qa_list = q_manager.reply_state(reply_list=reply_list)

        for qa in qa_list:
            if isinstance(qa[0], Question):
                profile = UserProfile.objects.get(user=qa[0].questioner)
            elif isinstance(qa[0], ReplyList):
                profile = UserProfile.objects.get(user=qa[0].question.questioner)
            qa.append(profile)

        from question.views import reply_list as r
        response = r(request)
        expected_html = render_to_string('question/top_r.html',
                                         {'qa_list': qa_list, 'last_login': request.user.last_login},
                                         context_instance=RequestContext(request))

        self.assertEqual(response.content.decode(), expected_html)

    def test_qiestion_edit_returns_correct_html(self):

        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        q = Question()
        form = QuestionEditForm(instance=q, initial={'time_limit': datetime.datetime(2015, 1, 1, 0, 1, 0, 0)})

        response = question_edit(request)
        expected_html = render_to_string('question/question_edit.html',
                                         {'form': form, 'id': id},
                                         context_instance=RequestContext(request))

        self.assertEqual(response.content.decode(), expected_html)

    def test_reply_edit_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        q = self.__create_question(request.user)[0]
        replylist = self.__create_reply_list(question=q, answerer=request.user)

        r = Reply()
        form = ReplyEditForm(instance=r)

        response = reply_edit(request, id=q.id)
        expected_html = render_to_string('question/reply_edit.html',
                                         {'form': form, 'question': q, 'id': id, 'replylist': replylist},
                                         context_instance=RequestContext(request))
        self.assertEqual(response.content.decode(), expected_html)

        print(expected_html)

    def test_qiestion_detail_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        q_created = self.__create_question(request.user)
        q = get_object_or_404(Question, pk=q_created[0].id)
        d = QuestionDestination.objects.filter(question=q)
        q_tags = QuestionTag.objects.filter(question=q)

        r = self.__create_reply(question=q, answerer=request.user)
        reply_list = self.__create_reply_list(question=q, answerer=request.user)[0]

        response = question_detail(request, id=q_created[0].id)
        expected_html = render_to_string('question/question_detail.html',
                                  {'question': q, 'destinations':d, 'q_tags': q_tags, 'reply': r, 'reply_list': reply_list},
                                  context_instance=RequestContext(request))
        self.assertEqual(response.content.decode(), expected_html)

    def test_qiestion_pass_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        q = self.__create_question(request.user)[0]
        reply_list = self.__create_reply_list(question=q, answerer=request.user)[0]

        qa_manager = QAManager()
        pass_success = qa_manager.pass_question(reply_list.question, qa_manager.reply_list_update_random_except)
        reply_list.question.update(is_closed=True)

        self.__create_user_profile(request.user)

        response = question_pass(request, id=reply_list.id)
        expected_html = top_default(request, msg='{0}'.format(m.INFO_QUESTION_ALREADY_AUTO_PASS))
        self.assertEqual(response.content.decode(), expected_html.content.decode())

    def test_mypage_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        self.__create_user_profile(request.user)
        p = get_object_or_404(UserProfile, user=request.user)

        user_tags = UserTag.objects.filter(user=request.user)
        form = UserProfileEditForm(instance=p)

        user_question = Question.objects.filter(questioner=request.user)
        user_reply = Reply.objects.filter(answerer=request.user)

        response = mypage(request)
        expected_html = render_to_string('question/mypage.html',
                                             {'form': form, 'user_tags': user_tags, 'uprof': p,
                                              'uquestion': user_question,
                                              'ureply': user_reply},
                                             context_instance=RequestContext(request))

        self.assertEqual(response.content.decode(), expected_html)

    def test_search_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')
        form = KeywordSearchForm()
        response = search(request)
        expected_html = render_to_string('question/question_search.html',
                                             {'form': form},
                                             context_instance=RequestContext(request))
        self.assertEqual(response.content.decode(), expected_html)

    def __create_question(self, user):
        return Question.objects.get_or_create(questioner=user,
                                       defaults=dict(questioner=user, title='test_title', text='test_text',
                                                     time_limit=datetime.time(6, 29, 28, 538000),
                                                     date=datetime.datetime(2012, 4, 18, 6, 29, 28, 538000),
                                                     draft=False, is_closed=False), )

    def __create_reply(self, question, answerer, text='test_text', date=datetime.datetime(2012, 4, 18, 6, 29, 28, 538000), draft=False):
        return Reply.objects.get_or_create(question=question, answerer=answerer, text=text, date=date, draft=draft)

    def __create_reply_list(self, question, answerer, time_limit_date=datetime.datetime(2015, 1, 1, 0, 0, 0, 0), has_replied=False):
        return ReplyList.objects.get_or_create(question = question, answerer=answerer, time_limit_date=time_limit_date, has_replied=has_replied)

    def __create_user(self):
        return User.objects.create_user(username='test', email=None, password='a')

    def __create_user_profile(self, user):
        # create fields for master DB
        work_place, created = WorkPlace.objects.get_or_create(name='東京', defaults=dict(name='東京', ), )
        work_status, created = WorkStatus.objects.get_or_create(name='在席', defaults=dict(name='在席', ), )
        division, created = Division.objects.get_or_create(code=2, name='人事', defaults=dict(code=2, name='人事'))

        # create user profile
        p, created = UserProfile.objects.get_or_create(user=user,
                                                           defaults=dict(avatar='images/icons/no_image.png',
                                                                         work_place=work_place,
                                                                         work_status=work_status,
                                                                         division=division,
                                                                         accept_question=1, ), )
        return p


from django.test.client import Client
class FormTests(TestCase):
    """
    各フォームのテスト。
    """

    def test_question_edit_form(self):
        c = Client()
        form = self.__crete_question_form()
        User.objects.create_user(username='admin', password='admin')
        response = c.login(username='admin', password='admin')
        response = c.post('/dotchain/q_new/', {'form':form})
        self.assertEqual(response.status_code, 200)

    def test_reply_edit_form(self):
        c = Client()
        user = User.objects.create_user(username='admin', password='admin')
        response = c.login(username='admin', password='admin')
        form = self.__create_reply_form(questioner=user, answerer=user)
        response = c.post('/dotchain/r_new/'+str(2), {'form':form})
        self.assertEqual(response.status_code, 301) # TODO change 301->200 Why 301?

    def test_user_profile_edit_form(self):
        c = Client()
        user = User.objects.create_user(username='admin', password='admin')
        response = c.login(username='admin', password='admin')
        form = self.__create_user_profile(user)
        response = c.post('/dotchain/mypage/', {'form':form})
        self.assertEqual(response.status_code, 200)

    def test_keyword_search_form(self):
        c = Client()
        user = User.objects.create_user(username='admin', password='admin')
        response = c.login(username='admin', password='admin')
        form = self.__create_keyword_search_form(user)
        response = c.get('/dotchain/search/', {'form':form})
        self.assertEqual(response.status_code, 200)

    def __crete_question_form(self):
        q = self.__create_question(self.__create_user(username='question_form_user', password='test'))[0]
        title = 'test_title'
        date = datetime.datetime(2015, 1, 1, 0, 0, 0, 0)
        time_limit = datetime.time(6, 29, 28, 538000)
        text = 'test_text'
        draft = False
        params = {'title':title, 'date':date, 'time_limit':time_limit, 'text':text, 'draft':draft}
        form = QuestionEditForm(params, instance=q)

        return form

    def __create_reply_form(self, questioner, answerer):
        q = self.__create_question(questioner)[0]
        #print("===========")
        #print(q.id)
        #print("===========")
        #q = self.__create_question(self.__create_user(username='reply_form_user', password='test'))[0]
        r = self.__create_reply(question=q, answerer=answerer)[0]
        date = datetime.datetime(2015, 1, 1, 0, 0, 0, 0)
        text = 'test_text'
        draft = False
        params = {'date':date, 'text':text, 'draft':draft}
        form = ReplyEditForm(params, instance=r)
        return form

    def __create_keyword_search_form(self, keyword):
        params = {'keyword':keyword}
        return KeywordSearchForm(params)

    def __create_question(self, user):
        return Question.objects.get_or_create(questioner=user,
                                       defaults=dict(questioner=user, title='test_title', text='test_text',
                                                     time_limit=datetime.time(6, 29, 28, 538000),
                                                     date=datetime.datetime(2012, 4, 18, 6, 29, 28, 538000),
                                                     draft=False, is_closed=False), )

    def __create_reply(self, question, answerer, text='test_text', date=datetime.datetime(2012, 4, 18, 6, 29, 28, 538000), draft=False):
        return Reply.objects.get_or_create(question=question, answerer=answerer, text=text, date=date, draft=draft)

    def __create_user(self, username, password):
        return User.objects.create_user(username=username, email=None, password=password)

    def __create_user_profile(self, user):
        # create fields for master DB
        work_place, created = WorkPlace.objects.get_or_create(name='東京', defaults=dict(name='東京', ), )
        work_status, created = WorkStatus.objects.get_or_create(name='在席', defaults=dict(name='在席', ), )
        division, created = Division.objects.get_or_create(code=2, name='人事', defaults=dict(code=2, name='人事'))

        # create user profile
        p, created = UserProfile.objects.get_or_create(user=user,
                                                           defaults=dict(avatar='images/icons/no_image.png',
                                                                         work_place=work_place,
                                                                         work_status=work_status,
                                                                         division=division,
                                                                         accept_question=1, ), )
        return p

class FormValidationTest(TestCase):
    """
    フォームのバリデーションテスト。
    """

    def setUp(self):
        from datetime import time, datetime
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
    def test_question_form(self):
        """正常な入力を行えばエラーにならないことを検証"""
        from datetime import time, datetime
        question = Question()
        form = QuestionEditForm(data={'destination': [1, 2], 'date':datetime.now(), 'title': 'test', 'time_limit': '11:11:11', 'text': 'test', 'draft': 0}, instance=question)
        print("=====question_edit=====")
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_reply_form(self):
        """正常な入力を行えばエラーにならないことを検証"""
        from datetime import time, datetime
        reply = Reply()
        form = ReplyEditForm(data={'date':datetime.now(), 'text': 'test', 'draft': 0}, instance=reply)
        print("=====reply_edit=====")
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_user_profile_form(self):
        """正常な入力を行えばエラーにならないことを検証"""
        profile = UserProfile()
        print(WorkPlace.objects.all())
        form = UserProfileEditForm(data={'work_place': self.work_place01.id, 'work_status': self.work_state01.id,  'division': self.division01.id, 'accept_question': 1 }, instance=profile)
        print("=====user_profile__edit=====")
        print(form.errors)
        self.assertTrue(form.is_valid())
