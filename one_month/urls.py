# -*- coding: utf-8 -*-
"""one_month URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
from django.contrib import admin

from accounts import views
from one_month import settings, init_application

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', views.login, name='login'),
    url(r'^accounts/signup/$', views.signup, name='signup'),
    url(r'^accounts/', include('allauth.urls')),

    # ルート
    #url(r'^', include('question.urls', namespace='question')),

    # アプリ関係
    url(r'^dotchain/', include('question.urls', namespace='dotchain')),
]


if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}),
    )


init_application.startup()