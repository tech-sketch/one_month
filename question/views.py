from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from accounts.models import UserProfile
from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag
from question.forms import QuestionEditForm, ReplyEditForm, UserProfileEditForm
from question.qa_manager import QAManager, QuestionState, ReplyState
import random, datetime, pytz

# Create your views here.
@login_required(login_url='/accounts/login')
def top_default(request):
    """
    トップページ
    """

    # 自分の質問を取ってくる
    q_list = Question.objects.filter(questioner=request.user)

    # 自分宛の質問を取ってくる
    reply_list = ReplyList.objects.filter(answerer=request.user)

    # 自分の質問と自分宛ての質問の状態を調べる
    qa_manager = QAManager(request.user)
    q_list = qa_manager.question_state(q_list)
    r_list = qa_manager.reply_state(reply_list)

    # 自分と自分宛の質問を結合して時系列に並べる
    qa_list = list()
    qa_list.extend(q_list)
    qa_list.extend(r_list)
    sorted(qa_list, key=lambda x: x[0].date if isinstance(x[0],Question) else x[0].question.date)#OK?
    #print(qa_list)

    # 自分の回答を取ってくる
    r = Reply.objects.filter(answerer=request.user)

    histories = None
    return render_to_response('question/top_all.html',
                              {'histories': histories, 'qa_list':qa_list, 'uname': request.user.last_name+request.user.first_name, 'last_login': request.user.last_login},
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
            print("-------------------------------")
            print(form.cleaned_data['destination'])
            # 質問を保存
            q = form.save(commit=False)
            q.questioner = request.user
            q.draft = form.cleaned_data['draft']
            q.save()

            # 06/16追加 : 所属外の人には送らない
            diff_dev_users_prof = UserProfile.objects.exclude(division__in=[d for d in form.cleaned_data['destination']])
            diff_user_list = [prof.user for prof in diff_dev_users_prof]
            # 06/16追加 : 受信拒否の人には送らない
            deny_users_prof = UserProfile.objects.exclude(accept_question=1)
            deny_users_list = [prof.user for prof in deny_users_prof]

            # 06/23追加：最終ログイン日から一定の日数が経過している人には送らない
            # TODO　最終ログイン日から何日に設定するか？あるいは動的に決めるか？（今は1日以内）
            #date_out_limit = datetime.datetime.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
            #no_login_users = User.objects.exclude(last_login__gte=date_out_limit)
            no_login_users = []
            # 回答ユーザ候補から除外するユーザ
            ex_user_list = list()
            ex_user_list.append(request.user)
            ex_user_list.extend(diff_user_list)
            ex_user_list.extend(deny_users_list)
            ex_user_list.extend(no_login_users)

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
        form = QuestionEditForm(instance=q, initial={'time_limit': datetime.timedelta(minutes=1)})

    return render_to_response('question/question_edit.html',
                              {'form': form, 'id': id},
                              context_instance=RequestContext(request))

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

    r = Reply()

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
    自分の質問を表示する
    """

    # 自分の質問を取ってくる
    q_mine = Question.objects.filter(questioner=request.user)

    # 自分の質問を時系列に並べる
    q = list()
    q.extend(q_mine)
    sorted(q, key=lambda x: x.date)#OK?

    # 各質問の状態を調べる
    q_manager = QAManager(request.user)
    qa_list = q_manager.question_state(q)

    histories = None
    return render_to_response('question/top_q.html',
                              {'histories': histories, 'qa_list': qa_list,
                               'uname': request.user.last_name+request.user.first_name,
                               'last_login': request.user.last_login},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
def question_pass(request, id=None):
    """
    来た質問をパスする。
    次に質問を回す人は、質問者と既にパスした人にはならないようにする。
    また、質問者以外のユーザを質問が回り終わったら、質問者にお知らせする。
    """

    #if 'replylist_id' in request.POST:
    if True:
        #replylist_id = request.POST['replylist_id']
        replylist =  ReplyList.objects.get(id=id)
        #replylist = ReplyList.objects.get(id=replylist_id)
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
        # 06/23追加：最終ログイン日から一定の日数が経過している人には送らない
        # TODO　最終ログイン日から何日に設定するか？あるいは動的に決めるか？（今は1日以内）
        date_out_limit = datetime.datetime.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        no_login_users = User.objects.exclude(last_login__gte=date_out_limit)

        # 回答ユーザ候補から除外するユーザ
        ex_user_list = list()
        ex_user_list.append(q.questioner)
        ex_user_list.extend(diff_user_list)
        ex_user_list.extend(pass_user_list)
        ex_user_list.extend(deny_users_list)
        ex_user_list.extend(no_login_users)

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
    質問の詳細を表示する
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

    # 回答リストを取ってくる
    try:
        reply_list = ReplyList.objects.get(question=q, answerer=request.user)
    except ReplyList.DoesNotExist:
        reply_list = None

    # user check
    #if q.questioner != request.user:
    #    # 他人の質問は表示できないようにする
    #    return HttpResponse("他の人の質問は表示できません！") # TODO　表示できないよページ作る

    return render_to_response('question/question_detail.html',
                              {'question': q, 'q_tags': q_tags, 'reply': r, 'reply_list': reply_list,
                               'uname': request.user.last_name+request.user.first_name},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
def reply_list(request):
    """
    自分に来た質問一覧を表示する
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
    #replylist = ReplyList.objects.filter(answerer=request.user, has_replied=False,time_limit_date__gte=datetime.datetime.now(pytz.utc)).order_by('time_limit_date')[:]
    #questions = [r.question for r in replylist]

    #return render_to_response('question/reply_list.html',
    #                            {'questions':questions,},
    #                           context_instance=RequestContext(request))

    # 自分宛の質問を取ってくる
    reply_list = ReplyList.objects.filter(answerer=request.user)

    # 自分宛の質問を時系列に並べる
    sorted(reply_list, key=lambda x: x.question.date)#OK?

    # 各質問の状態を調べる
    q_manager = QAManager(request.user)
    qa_list = q_manager.reply_state(reply_list=reply_list)

    histories = None
    return render_to_response('question/top_r.html',
                              {'histories': histories, 'qa_list': qa_list, 'uname': request.user.last_name+request.user.first_name, 'last_login': request.user.last_login},
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
            tags = form.cleaned_data['tag']
            u_tag_names =[t.tag.name for t in user_tags]
            for q_tag in tags:
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

@login_required(login_url='/accounts/login')
def network(request):
    all_user = [[u.username, 'u{}'.format(u.id)] for u in User.objects.all()]
    all_tag = [[t.name, 't{}'.format(t.id)] for t in Tag.objects.all()]
    all_reply = [['u{}'.format(r.answerer.id),  'u{}'.format(r.question.questioner.id)] for r in Reply.objects.all()]
    all_reply = set([tuple(sorted(r)) for r in all_reply])
    all_userTag = [['u{}'.format(u.user.id),  't{}'.format(u.tag.id)] for u in UserTag.objects.all()]

    return render_to_response('question/network.html',
                              {'all_user': all_user, 'all_reply': all_reply, 'all_tag': all_tag, 'all_userTag': all_userTag },
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
def pass_network(request, id=None):
    q = get_object_or_404(Question, pk=id)
    # user check
    if q.questioner != request.user:
        # 他人の質問は表示できないようにする
        return HttpResponse("他の人の質問は表示できません！") # TODO　表示できないよページ作る

    all_user = [[u.username, 'u{}'.format(u.id)] for u in User.objects.all()]
    all_tag = [[t.name, 't{}'.format(t.id)] for t in Tag.objects.all()]
    all_reply = [['u{}'.format(r.answerer.id),  'u{}'.format(r.question.questioner.id)] for r in Reply.objects.all()]
    all_reply = set([tuple(sorted(r)) for r in all_reply])
    all_userTag = [['u{}'.format(u.user.id),  't{}'.format(u.tag.id)] for u in UserTag.objects.all()]

    all_pass_temp = ['u{}'.format(r.answerer.id) for r in ReplyList.objects.filter(question=q).order_by('time_limit_date')]
    all_pass_temp.insert(0, 'u{}'.format(q.questioner.id), )
    all_pass = [[all_pass_temp[n-1], all_pass_temp[n]] for n in range(1, len(all_pass_temp))]

    return render_to_response('question/pass_network.html',
                              {'all_user': all_user, 'all_reply': all_reply, 'all_tag': all_tag, 'all_userTag': all_userTag, 'all_pass': all_pass},
                              context_instance=RequestContext(request))
