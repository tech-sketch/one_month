from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import random, datetime, pytz
from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag
from question.forms import QuestionEditForm, ReplyEditForm, UserProfileEditForm
from accounts.models import User, UserProfile

# Create your views here.

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

    # edit
    if request.method == 'POST':
        form = QuestionEditForm(request.POST, instance=q)

        # 完了がおされたら
        if form.is_valid():

            # 質問を保存
            q = form.save(commit=False)
            q.questioner = request.user
            q.draft = form.cleaned_data['draft']
            q.save()

            # 06/16追加 : 所属外の人には送らない
            diff_dev_users_prof = UserProfile.objects.exclude(division=form.cleaned_data['destination_div'])
            diff_user_list = [prof.user for prof in diff_dev_users_prof]
            # 06/16追加 : 受信拒否の人には送らない
            deny_users_prof = UserProfile.objects.exclude(accept_question=1)
            deny_users_list = [prof.user for prof in deny_users_prof]

            # 回答ユーザ候補から除外するユーザ
            ex_user_list = list()
            ex_user_list.append(request.user)
            ex_user_list.extend(diff_user_list)
            ex_user_list.extend(deny_users_list)

            # ランダムに質問者を選んでからReplyListを生成して保存
            r_list = reply_list_update_random_except(ex_user_list, q)

            if r_list == None:
                q.delete()
                return HttpResponse("宛先ユーザが見つかりませんでした。。入力された質問は消去されます")
            else:
                r_list.save()

            # 選択されたタグから、新規にQuestionTagを生成して保存
            q_tags = form.cleaned_data['tag']
            for q_tag in q_tags:
                qt = QuestionTag()
                qt.tag = q_tag
                qt.question = q
                qt.save()

            # 追加されたタグ名から、新規にTagとQuestionTagを生成して保存
            tag_added_name = form.cleaned_data['tag_added']
            tags = Tag.objects.all()
            tag_name = [t.name for t in tags]
            if tag_added_name != "" and tag_added_name not in tag_name: # 新規に追加されたタグだったら保存
                t = Tag()
                t.name = tag_added_name
                t.save()
                qt = QuestionTag()
                qt.tag = t
                qt.question = q
                qt.save()

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

    candidate_users = User.objects.filter(~Q(username=u)).filter(~Q(username=q.questioner))

    try:
        r_list = ReplyList()
        r_list.answerer = random.choice(candidate_users)
        r_list.question = q
        r_list.time_limit_date = datetime.datetime.now() + datetime.timedelta(hours=q.time_limit.hour, minutes=q.time_limit.minute, seconds=q.time_limit.second)
        return r_list
    except IndexError:
        return None

def reply_list_update_random_except(users, question):
    """
    指定されたユーザリスト以外の中からランダムに次の回答ユーザを決定する。
    """

    #rand_user = User.objects.filter(~Q(username=question.questioner))
    candidate_users = User.objects.all()

    for u in users:
        candidate_users = candidate_users.filter(~Q(username=u))

    try:
        r_list = ReplyList()
        r_list.answerer = random.choice(candidate_users)
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
        q = replylist.question

        # 06/16追加 : 所属外の人には送らない
        diff_dev_users_prof = UserProfile.objects.filter(~Q(division=q.destination_div))
        diff_user_list = [prof.user for prof in diff_dev_users_prof]
        # 今までパスした人（自分=request.userも含む）には送らない
        reply_lists_pass_users = ReplyList.objects.filter(question=q, has_replied=True)
        pass_user_list = [r.answerer for r in reply_lists_pass_users]
        # 06/16 受信拒否の人には送らない
        deny_users_prof = UserProfile.objects.exclude(accept_question=1)
        deny_users_list = [prof.user for prof in deny_users_prof]

        # 回答ユーザ候補から除外するユーザ
        ex_user_list = list()
        ex_user_list.append(q.questioner)
        ex_user_list.extend(diff_user_list)
        ex_user_list.extend(pass_user_list)
        ex_user_list.extend(deny_users_list)

        new_replylist = reply_list_update_random_except(ex_user_list, replylist.question)

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

    # 質問のタグを取ってくる
    q_tags = QuestionTag.objects.filter(question=q)

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
                              {'question': q, 'q_tags': q_tags, 'reply': r,},
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
                                {'questions':questions,},
                                context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
def mypage(request):
    """
    マイページ
    """

    # ユーザのプロファイルを取ってくる
    try:
        p = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        p = UserProfile()
        p.user = request.user
        p.save()

    # ユーザが登録しているタグを取ってくる
    user_tags = UserTag.objects.filter(user=request.user)
    #user_tags = [user_tag.tag for user_tag in user_tags]

    # edit
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, instance=p)

        # 完了がおされたら
        if form.is_valid():
            r = form.save(commit=False)
            r.save()

            # 選択されたタグから、新規にQuestionTagを生成して保存
            q_tags = form.cleaned_data['tag']
            u_tag_names =[t.tag.name for t in user_tags]
            for q_tag in q_tags:
                if q_tag.name not in u_tag_names: # ユーザに新規に追加されたタグだったら保存
                    qt = UserTag()
                    qt.tag = q_tag
                    qt.user = request.user
                    qt.save()

            # 追加されたタグ名から、新規にTagとQuestionTagを生成して保存
            tag_added_name = form.cleaned_data['tag_added']
            tags = Tag.objects.all()
            tag_name =[t.name for t in tags]
            if tag_added_name != "" and tag_added_name not in tag_name: # 新規に追加されたタグだったら保存
                t = Tag()
                t.name = tag_added_name
                t.save()
                qt = UserTag()
                qt.tag = t
                qt.user = request.user
                qt.save()
            else:
                print(tag_added_name)

            return redirect('question:top')
        pass
    # new
    else:
        form = UserProfileEditForm(instance=p)
        #tag_form = UserTagEditForm(instance=t)
        # TODO マイページにユーザが登録済みのタグを表示しつつ、追加・編集できるようにしたい

    return render_to_response('question/mypage.html',
                              {'form': form, 'user_tags':user_tags, 'uname': request.user.last_name+request.user.first_name},
                              context_instance=RequestContext(request))
