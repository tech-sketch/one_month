from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Q
import random
from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag
from accounts.models import User, UserProfile
import datetime, pytz
from question.tasks import add, countdown


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

class UserProfileEditForm(ModelForm):
    """
    ユーザプロファイル編集フォーム
    """
    class Meta:
        model = UserProfile
        fields = ('user', 'work_place', 'work_status', 'division', 'accept_question')
        widgets = {
            'work_place': forms.TextInput(attrs={'size': '20'}),
            'work_status': forms.TextInput(attrs={'size': '20'}),
            'division': forms.TextInput(attrs={'size': '20'}),
        }

class UserTagEditForm(ModelForm):
    """
    ユーザータグ編集フォーム
    """
    class Meta:
        model = UserTag
        fields = ('user', 'tag')
        widgets = {}

@login_required(login_url='/accounts/login')
def top_default(request):
    """
    トップページ（デフォルト）
    """

    histories = None
    return render_to_response('question/top_default.html',
                              {'histories': histories, 'uname': request.user.last_name+request.user.first_name},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
def question_edit(request, id=None):
    """
    質問ページ
    """

    # edit
    if id:
        q = get_object_or_404(Question, pk=id)
        # user check
        if q.questioner != request.user:
            print("不正なアクセスです！")
            return redirect('question:top')
    # new
    else:
        q = Question()

    #q = Question()

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

            # タイムリミットカウントダウン開始（非同期）
            result = countdown.delay(r_list)

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
    rand_user = User.objects.filter(~Q(username=u)).filter(~Q(username=q.questioner))

    try:
        r_list.answerer = random.choice(rand_user)
        r_list.question = q
        r_list.time_limit_date = datetime.datetime.now() + datetime.timedelta(hours=q.time_limit.hour, minutes=q.time_limit.minute, seconds=q.time_limit.second)
        return r_list
    except IndexError:
        return None

def reply_list_update_random_except(users, question):
    """
    指定されたユーザリスト以外の中からランダムに次の回答ユーザを決定する。
    """

    r_list = ReplyList()

    #rand_user = User.objects.filter(~Q(username=question.questioner))
    rand_user = User.objects.all()

    for u in users:
        rand_user = rand_user.filter(~Q(username=u))

    try:
        r_list.answerer = random.choice(rand_user)
        r_list.question = question
        r_list.time_limit_date = datetime.datetime.now() + datetime.timedelta(
                                    hours=question.time_limit.hour,
                                    minutes=question.time_limit.minute,
                                    seconds=question.time_limit.second)
        return r_list
    except IndexError:
        return None


@login_required(login_url='/accounts/login')
def reply_edit(request, id=None):
    """
    返信ページ
    """

    # 指定された質問を取ってくる
    q = get_object_or_404(Question, pk=id)

    #replylist = ReplyList.objects.filter(question=q)[0]
    # 各質問について、has_replied=Falseの回答済みリストは一つのみのはず
    replylist = get_object_or_404(ReplyList, question=q, has_replied=False)

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

            # この質問の自分あての回答リストを取ってきて、回答済みにしておく
            r_list = get_object_or_404(ReplyList, question = r.question, answerer=request.user, has_replied=False) #has_replied=Falseはいらないと思う
            r_list.has_replied = True
            r_list.save()

            return redirect('question:top')
        pass
    # new
    else:
        form = ReplyEditForm(instance=r)

    return render_to_response('question/reply_edit.html',
                                  {'form': form, 'question': q, 'id': id, 'replylist':replylist},
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
    来た質問をパスする。
    次に質問を回す人は、質問者と既にパスした人にはならないようにする。
    また、質問者以外のユーザを質問が回り終わったら、質問者にお知らせする。
    """

    if 'replylist_id' in request.POST:
        replylist_id = request.POST['replylist_id']
        replylist = ReplyList.objects.get(id=replylist_id)
        replylist.has_replied = True
        replylist.save()

        #new_replylist = reply_list_update_random(replylist.answerer, replylist.question)

        # 質問者と今までパスした人（自分=request.userも含む）は次の回答ユーザ候補から除く
        reply_lists_pass_users = ReplyList.objects.filter(question=replylist.question, has_replied=True)
        pass_user_list = [r.answerer for r in reply_lists_pass_users]
        pass_user_list.append(replylist.question.questioner)
        new_replylist = reply_list_update_random_except(pass_user_list, replylist.question)

        if new_replylist != None:
            new_replylist.save()
            return HttpResponse("パスしました") # TODO　パスしましたページ作る
        else:
            # TODO パスが回り終わったときに質問者に通知する仕組みを考える
            return HttpResponse("パスしましたが、次の回答ユーザが見つかりませんでした。この質問は回答者無しとして質問者に報告されます")
    else:
        return HttpResponse("不明なエラーです！（question_pass() in views.py）")

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
        r = Reply.objects.get(question=q) # 一つの質問につき返信が複数ある場合はfilterを使うこと
    except Reply.DoesNotExist:
        r = None

    # user check
    if q.questioner != request.user:
        # 他人の質問は表示できないようにする
        return HttpResponse("他の人の質問は表示できません！") # TODO　表示できないよページ作る

    return render_to_response('question/question_detail.html',
                              {'question': q, 'reply': r},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
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
    # 返信期限がまだ来てないもの、かつ返信期限が早いものから順に表示
    replylist = ReplyList.objects.filter(answerer=request.user, has_replied=False,
                                        time_limit_date__gte=datetime.datetime.now(pytz.utc)).order_by('time_limit_date')[:]
    questions = [r.question for r in replylist]

    return render_to_response('question/reply_list.html',
                                {'questions':questions},
                                context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
def mypage(request):
    """
    マイページ
    このページでユーザが登録済みのタグを表示かつ追加したいが、まだできてない。
    """

    # ユーザのプロファイルを取ってくる
    try:
        p = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        p = UserProfile()
        p.user = request.user
        p.save()

    # ユーザが登録しているタグを取ってくる
    #user_tags = UserTag.objects.filter(user=request.user)
    #user_tags = [user_tag.tag for user_tag in user_tags]
    try:
        t = UserTag.objects.filter(user=request.user)
    except UserTag.DoesNotExist:
        tag = Tag()
        tag.name = "temp tag"
        tag.save()
        t = UserTag()
        t.tag = tag
        t.user = request.user
        t.save()

    # edit
    if request.method == 'POST':
        #if(form.name == "")
        #   if()
        print(request.POST)
        if 'done' in request.POST:
            form = UserProfileEditForm(request.POST, instance=p)

            # 完了がおされたら
            if form.is_valid():
                r = form.save(commit=False)
                r.save()

                return redirect('question:top')
            pass
        """
        elif 'add_tag' in request.POST:
            tag_form = UserTagEditForm(request.POST, instance=t)

            # 完了がおされたら
            if tag_form.is_valid():
                r = tag_form.save(commit=False)
                r.save()

                return redirect('question:top')
        """
        pass
    # new
    else:
        form = UserProfileEditForm(instance=p)
        #tag_form = UserTagEditForm(instance=t)
        # TODO マイページにユーザが登録済みのタグを表示しつつ、追加・編集できるようにしたい

    return render_to_response('question/mypage.html',
                              {'form': form, 'uname': request.user.last_name+request.user.first_name},
                              context_instance=RequestContext(request))
