# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from question import views

urlpatterns = patterns('',
        url(r'^$', views.top_default, name='top'),# トップページ（デフォルト）
        url(r'^q_new/$', views.question_edit, name='q_new'),              # 新規質問
        url(r'^r_new/$', views.reply_edit, name='r_new'),              # 新規回答
        url(r'^q_list/$', views.question_list, name='q_list'),            # 質問リスト
        url(r'^q_pass/(?P<id>\d+)/$', views.question_pass, name='q_pass'),  # 質問をパス
        url(r'^q_detail/(?P<id>\d+)/$', views.question_detail, name='q_detail'), # 詳細
)
