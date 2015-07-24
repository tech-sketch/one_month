from django.test import TestCase
from django.contrib.auth.models import User
from datetime import time, datetime
from accounts.models import UserProfile, WorkPlace, WorkStatus, Division
from .models import QuestionDestination, QuestionTag, Question, Reply, ReplyList, Tag, UserTag
from .forms import QuestionEditForm, ReplyEditForm, UserProfileEditForm

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase
from question.views import *
from question import message_definition as m


class HtmlTests(TestCase):
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

        # プロフィール
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
        form = QuestionEditForm(instance=q, initial={'time_limit': datetime.timedelta(minutes=1)})

        response = question_edit(request)
        expected_html = render_to_string('question/question_edit.html',
                                         {'form': form, 'id': id},
                                         context_instance=RequestContext(request))

        self.assertEqual(response.content.decode(), expected_html)

    def test_reply_edit_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        q = self.__create_question(request.user)
        replylist = get_object_or_404(ReplyList, question=q, has_replied=False)

        r = Reply()
        form = ReplyEditForm(instance=r)

        response = reply_edit(request)
        expected_html = render_to_string('question/reply_edit.html',
                                         {'form': form, 'question': q, 'id': id, 'replylist': replylist},
                                         context_instance=RequestContext(request))
        #self.assertEqual(response.content.decode(), expected_html)

    def test_qiestion_detail_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        q = get_object_or_404(Question, pk=id)
        d = QuestionDestination.objects.filter(question=q)
        q_tags = QuestionTag.objects.filter(question=q)

        r = Reply.objects.filter(question=q)
        reply_list = ReplyList.objects.get(question=q, answerer=request.user)

        id=0
        response = question_detail(request, id=id)
        expected_html = render_to_string('question/question_detail.html',
                                  {'question': q, 'destinations':d, 'q_tags': q_tags, 'reply': r, 'reply_list': reply_list},
                                  context_instance=RequestContext(request))
        self.assertEqual(response.content.decode(), expected_html)

    def __create_question(self, user):
        from datetime import datetime

        return Question.objects.get_or_create(questioner=user,
                                       defaults=dict(questioner=user, title='test_title', text='test_text',
                                                     time_limit=None,
                                                     date=datetime.datetime(2012, 4, 18, 6, 29, 28, 538000),
                                                     draft=False, is_closed=False), )

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

    def test_mypage_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        request.user = User.objects.create_user(username='test', email=None, password='a')

        # ユーザのプロファイルを取ってくる
        self.__create_user_profile(request.user)
        p = get_object_or_404(UserProfile, user=request.user)

        # ユーザが登録しているタグを取ってくる
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
