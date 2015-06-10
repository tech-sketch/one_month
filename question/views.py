from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
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
def reply_edit(request, id=None):
    """
    返信ページ
    """

    # 指定された質問を取ってくる
    q = get_object_or_404(Question, pk=id)

    r =Reply()

    # edit
    if request.method == 'POST':
        form = ReplyEditForm(request.POST, instance=r)

        # 完了がおされたら
        if form.is_valid():
            r = form.save(commit=False)
            r.question = q
            r.answerer = request.user
            r.draft = form.cleaned_data['draft']
            r.save()

            # この質問の自分あての回答リストをもってくる
            r_list = get_object_or_404(ReplyList, question = r.question, answerer=request.user)
            """
            if len(r_list) > 1:
                return HttpResponse("")
          """
            r_list.has_replied = True # 回答済みにしておく
            r_list.save()

            return redirect('question:top')
        pass
    # new
    else:
        form = ReplyEditForm(instance=r)

        return render_to_response('question/reply_edit.html',
                                  {'form': form, 'question': q, 'id': id},
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

@login_required(login_url='/accounts/login')
def question_pass(request, id=None):
    """
    来た質問をパスする
    """

    return HttpResponse("パスしました") # TODO　質問無しページ作る

@login_required(login_url='/accounts/login')
def question_detail(request, id=None):
    """
    自分の質問の詳細を表示する
    """

    # 指定された質問を取ってくる
    q = get_object_or_404(Question, pk=id)

    # 質問に対する回答を取ってくる
    # まだ回答が来てない場合のためにget_object_or_404は使わずにこちらを使う
    try:
        r = Reply.objects.get(question=q)
    except Reply.DoesNotExist:
        r = None

    # user check
    if q.questioner != request.user:
        # 他人の質問は表示できないようにする
        return HttpResponse("他の人の質問は表示できません！") # TODO　表示できないよページ作る

    return render_to_response('question/question_detail.html',
                              {'question': q, 'reply': r},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/google/login')
def reply_list(request):
    """
    回答一覧ページ
    """

    r = Reply()

    """
    # ランダムに質問取ってくる
    #下書きにチェックがはいっていないもののみ最新のものから順に表示
    question_tmp = Question.objects.filter(~Q(questioner=request.user))#.order_by('-date')[:]
    question = list(filter(lambda x: x.draft==False, question_tmp))
    question = random.choice(question) #ランダムに質問を取ってくる
    """

    # 06/09 返信リストの中から自分あて、かつ返信済みでない質問を取ってくる
    # 返信期限が早いものから順に表示
    replylist = ReplyList.objects.filter(answerer=request.user, has_replied=False).order_by('time_limit_date')[:]
    questions = [r.question for r in replylist]

    return render_to_response('question/reply_list.html',
                                {'questions':questions},
                                context_instance=RequestContext(request))

