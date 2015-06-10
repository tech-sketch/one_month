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

            r_list = reply_list_update_random(request.user, q)
            r_list.save()

            return redirect('question:top')
        pass
    # new
    else:
        form = QuestionEditForm(instance=q)

    return render_to_response('question/question_edit.html',
                              {'form': form, 'id': id},
                              context_instance=RequestContext(request))

#全ユーザーの中からランダムに返信ユーザーを決定する。（u:User 対象としたくないユーザー, q:Question）
def reply_list_update_random(u, q):
    r_list = ReplyList()
    rand_user = User.objects.filter(~Q(username=u))
    r_list.answerer = random.choice(rand_user)
    r_list.question = q
    r_list.time_limit_date = datetime.datetime.now() + datetime.timedelta(hours=q.time_limit.hour, minutes=q.time_limit.minute, seconds=q.time_limit.second)
    return r_list


@login_required(login_url='/accounts/google/login')
def reply_edit(request):
    """
    返信ページ
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
    replylist = ReplyList.objects.filter(Q(answerer=request.user))#.order_by('-date')[:] # 自分宛
    replylist = replylist.filter(Q(has_replied=False))                                  # 返信済みでないもの
    #question = [r.question for r in replylist]

    if len(replylist) > 0:
        replylist = random.choice(replylist)
        question = replylist.question
        #question = random.choice(questions) #ランダムに質問を取ってくる

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
                                  {'form': form, 'question':question ,'id': id, 'replylist':replylist},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse("質問なし") # TODO　質問無しページ作る

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
    if 'replylist_id' in request.POST:
        replylist_id = request.POST['replylist_id']
        replylist = ReplyList.objects.get(id=replylist_id)
        replylist.has_replied = True

        new_replylist = reply_list_update_random(replylist.answerer, replylist.question)
        new_replylist.save()

    print(request.POST)

    return HttpResponse("パスしました。") # TODO　質問無しページ作る
