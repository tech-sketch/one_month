from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from accounts.models import UserProfile
from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag, QuestionDestination
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
    qa_list = sorted(qa_list, reverse=True, key=lambda x: x[0].date if isinstance(x[0],Question) else x[0].question.date)#OK?
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
            # 質問を保存
            q = form.save(commit=False)
            q.questioner = request.user
            q.draft = form.cleaned_data['draft']
            q.save()

            div_list = form.cleaned_data['destination']
            for div in div_list:
                d = QuestionDestination()
                d.question = q
                d.tag = div
                d.save()

            # ランダムに質問者を選んでからReplyListを生成して保存
            qa_manager = QAManager()
            r_list = qa_manager.make_reply_list(q, qa_manager.reply_list_update_random_except)

            if r_list == None:
                q.delete()
                msg = '宛先ユーザが見つかりませんでした。。入力された質問は消去されます。'
                msg += '次の原因が考えられます。'
                msg += '・送信先にユーザがいない'
                msg += '・送信先に1日以内にログインしたユーザがいない'
                msg += '・送信先に受信拒否のユーザしかいない'
                return HttpResponse(msg)
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
    if ReplyList.objects.filter(question=q, answerer=request.user, has_replied=True):
        return HttpResponse("パスされました")

    if q.is_closed:
        return HttpResponse("回答は締め切られました")

    #replylist = ReplyList.objects.filter(question=q)[0]
    # 各質問について、has_replied=Falseの回答済みリストは一つのみのはず
    replylist = get_object_or_404(ReplyList, question=q, has_replied=False)

    r = Reply()

    # edit
    if request.method == 'POST':
        form = ReplyEditForm(request.POST, instance=r)

        # 完了がおされたら
        if form.is_valid():
            # この質問の自分あての回答リストを取ってきて、回答済みにしておく
            r_list = get_object_or_404(ReplyList, question=q, answerer=request.user) #has_replied=Falseはいらないと思う
            if r_list.has_replied:
                return HttpResponse("自動的にパスされました")
            r_list.has_replied = True
            r_list.save()

            r_list.question.is_closed = True
            r_list.question.save()

            r = form.save(commit=False)
            r.question = q
            r.answerer = request.user
            r.draft = form.cleaned_data['draft']
            r.save()

            #質問を締め切る
            q.is_closed = True
            q.save()

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
    q = sorted(q, reverse=True, key=lambda x: x.date)#OK?

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
        replylist = ReplyList.objects.get(id=id)
        if replylist.has_replied:
             return HttpResponse("パス済みです")

        #new_replylist = reply_list_update_random(replylist.answerer, replylist.question)
        qa_manager = QAManager()
        print(replylist.question.title)
        if qa_manager.pass_question(replylist.question, qa_manager.reply_list_update_random_except):
            return HttpResponse("パスしました")
        else:
            replylist.question.is_closed = True
            replylist.question.save()
            return HttpResponse("パスしましたがすべてのユーザがパスしたため質問は締め切ります")
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
    print(q.questioner)
    print(request.user)
    print(reply_list)
    if q.questioner != request.user and reply_list==None:
        # 他人の質問は表示できないようにする
        return HttpResponse("他の人の質問は表示できません！") # TODO　表示できないよページ作る

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

    # 自分宛の質問のうち、自分の回答待ちになっている質問を取ってくる
    reply_list = ReplyList.objects.filter(answerer=request.user, has_replied=False)

    # 自分宛の質問を時系列に並べる
    reply_list = sorted(reply_list, reverse=True, key=lambda x: x.question.date)#OK?

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
                print("tag_added")
                print(tag_added_name)

            return redirect('question:mypage')
        pass
    # new
    else:
        form = UserProfileEditForm(instance=p)
        #tag_form = UserTagEditForm(instance=t)
        # TODO マイページにユーザが登録済みのタグを表示しつつ、追加・編集できるようにしたい

    user_question = Question.objects.filter(questioner=request.user)
    user_reply = Reply.objects.filter(answerer=request.user)
    return render_to_response('question/mypage.html',
                              {'form': form, 'user_tags':user_tags, 'uname': request.user, 'uprof':p, 'uquestion':user_question, 'ureply':user_reply},
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

    user_reply_list =ReplyList.objects.filter(question=q).order_by('time_limit_date')[0]
    if ReplyList.objects.filter(question=q, answerer=request.user):
        user_reply_list = ReplyList.objects.get(question=q, answerer=request.user)
    # user check
    if q.questioner != request.user:
        pass
        # 他人の質問は表示できないようにする
        #return HttpResponse("他の人の質問は表示できません！") # TODO　表示できないよページ作る

    all_user = [[u.username, 'u{}'.format(u.id)] for u in User.objects.all()]
    all_tag = [[t.name, 't{}'.format(t.id)] for t in Tag.objects.all()]
    all_reply = [['u{}'.format(r.answerer.id),  'u{}'.format(r.question.questioner.id)] for r in Reply.objects.all()]
    all_reply = set([tuple(sorted(r)) for r in all_reply])
    all_userTag = [['u{}'.format(u.user.id),  't{}'.format(u.tag.id)] for u in UserTag.objects.all()]

    all_pass_temp = ['u{}'.format(r.answerer.id) for r in ReplyList.objects.filter(question=q).order_by('time_limit_date')]
    all_pass_temp.insert(0, 'u{}'.format(q.questioner.id), )
    all_pass = [[all_pass_temp[n-1], all_pass_temp[n]] for n in range(1, len(all_pass_temp))]
    print( request.user)

    return render_to_response('question/pass_network.html',
                              {'user_reply_list': user_reply_list, 'you': [request.user.username, 'u{}'.format(request.user.id)], 'all_user': all_user, 'all_reply': all_reply, 'all_tag': all_tag, 'all_userTag': all_userTag, 'all_pass': all_pass},
                              context_instance=RequestContext(request))

def debug(request):
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
    qa_list = sorted(qa_list, reverse=True, key=lambda x: x[0].date if isinstance(x[0],Question) else x[0].question.date)#OK?
    #print(qa_list)

    # 自分の回答を取ってくる
    r = Reply.objects.filter(answerer=request.user)

    histories = None
    return render_to_response('question/top_debug.html',
                              {'histories': histories, 'qa_list':qa_list, 'uname': request.user.last_name+request.user.first_name, 'last_login': request.user.last_login},
                              context_instance=RequestContext(request))
