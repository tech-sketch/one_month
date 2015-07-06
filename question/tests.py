from django.test import TestCase

# Create your tests here.
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