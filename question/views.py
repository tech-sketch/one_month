from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Q
import random
from question.models import Question, Reply, ReplyList
from accounts.models import User
import datetime


# Create your views here.

class QuestionEditForm(ModelForm):
    """
    質問フォーム
    """
    class Meta:
        model = Question
        fields = ('title', 'date', 'time_limit', 'text', 'draft')
        widgets = {
          'title': forms.TextInput(attrs={'size': '100'}),
          'text': forms.Textarea(attrs={'rows':20, 'cols':100}),
        }

class ReplyEditForm(ModelForm):
    """
    回答フォーム
    """
    class Meta:
        model = Reply
        fields = ('date', 'text', 'draft')
        widgets = {
          'text': forms.Textarea(attrs={'rows':20, 'cols':100}),
        }

@login_required(login_url='/accounts/google/login')
def top_default(request):
    """
    トップページ（デフォルト）
    """
    print(request.user.last_name+request.user.first_name)
    print("top_default called")

    histories = None
    return render_to_response('question/top_default.html',
                              {'histories': histories, 'uname': request.user.last_name+request.user.first_name},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/google/login')
def question_edit(request):
    """
    質問ページ
    """
    q = Question()

    # edit
    if request.method == 'POST':
        form = QuestionEditForm(request.POST, instance=q)

        # 完了がおされたら
        if form.is_valid():
            q = form.save(commit=False)
            q.questioner = request.user
            q.draft = form.cleaned_data['draft']
            q.save()

            r_list = ReplyList()
            rand_user = User.objects.filter(~Q(username=request.user))
            r_list.answerer = random.choice(rand_user)
            r_list.question = q
            print("-------------------------------------------------")
            print(q.time_limit)
            r_list.time_limit_date = datetime.datetime.now() + datetime.timedelta(hours=q.time_limit.hour, minutes=q.time_limit.minute, seconds=q.time_limit.second)
            r_list.save()

            return redirect('question:top')
        pass
    # new
    else:
        form = QuestionEditForm(instance=q)

    return render_to_response('question/question_edit.html',
                              {'form': form, 'id': id},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/google/login')
def reply_edit(request):
    """
    返信ページ
    """
    r = Reply()

    # ランダムに質問取ってくる
    #下書きにチェックがはいっていないもののみ最新のものから順に表示
    question_tmp = Question.objects.filter(~Q(questioner=request.user))#.order_by('-date')[:]
    question = list(filter(lambda x: x.draft==False, question_tmp))
    question = random.choice(question) #ランダムに質問を取ってくる

    # edit
    if request.method == 'POST':
        form = ReplyEditForm(request.POST, instance=r)

        # 完了がおされたら
        if form.is_valid():
            r = form.save(commit=False)
            r.question = question# ランダムに決める
            r.answerer = request.user
            r.draft = form.cleaned_data['draft']
            r.save()
            return redirect('question:top')
        pass
    # new
    else:
        form = ReplyEditForm(instance=r)

    return render_to_response('question/reply_edit.html',
                              {'form': form, 'question':question ,'id': id},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
def question_list(request):

    """
    自分が今までにした質問一覧を表示する
    """

    #最新のものから順に表示（下書きも表示させる）
    questions = Question.objects.filter(questioner=request.user).order_by('-date')[:]

    return render_to_response('question/question_list.html',
                              {'questions': questions, 'uname': request.user.last_name+request.user.first_name},
                              context_instance=RequestContext(request))