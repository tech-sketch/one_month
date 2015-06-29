# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from question import views

urlpatterns = patterns('',
        url(r'^$', views.top_default, name='top'),# トップページ（デフォルト）
        url(r'^q_new/$', views.question_edit, name='q_new'),              # 新規質問
        url(r'^r_new/(?P<id>\d+)/$', views.reply_edit, name='r_new'),   # 新規回答
        url(r'^r_list/$', views.reply_list, name='r_list'), # 他のユーザから来た質問リスト
        url(r'^q_list/$', views.question_list, name='q_list'),            # 自分がした質問リスト
        url(r'^q_edit/(?P<id>\d+)/$', views.question_edit, name='q_edit'),  # 質問の編集（下書きの場合）
        url(r'^q_pass/(?P<id>\d+)/$', views.question_pass, name='q_pass'),  # 質問をパス
        url(r'^q_detail/(?P<id>\d+)/$', views.question_detail, name='q_detail'), # 詳細
        url(r'^mypage/$', views.mypage, name='mypage'), # マイページ
        url(r'^search/$', views.search, name='search'), # 検索
        url(r'^network/$', views.network, name='network'), # ネットワーク
        url(r'^pass_network/(?P<id>\d+)/$', views.pass_network, name='pass_network'), # パスのネットワーク
        url(r'^debug/$', views.debug, name='debug'), # デバッグ用ページ
)
