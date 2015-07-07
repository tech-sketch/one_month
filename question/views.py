from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from accounts.models import UserProfile, WorkStatus, WorkPlace, Division
from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag, QuestionDestination
from question.forms import QuestionEditForm, ReplyEditForm, UserProfileEditForm, KeywordSearchForm
from question.qa_manager import QAManager, QuestionState, ReplyState
import datetime

# Create your views here.
@login_required(login_url='/accounts/login')
def top_default(request, msg=None):
    """
    トップページ
    """

    # added
    form = None
    if request.method == 'GET':
        form = KeywordSearchForm()
        # 自分の質問を取ってくる
        questions = Question.objects.filter(questioner=request.user)
        # 自分宛の質問リストを取ってくる
        reply_lists = ReplyList.objects.filter(answerer=request.user)

    elif request.method == 'POST':
        form = KeywordSearchForm(request.POST)

        """
       以下の質問をキーワード検索で取ってくる
       * 自分がした質問のタイトル・内容・タグいずれかがキーワードと部分一致
       * 相手から自分へ来た質問のタイトル・内容・タグいずれかがキーワードと部分一致
       * 自分の回答内容がキーワードと部分一致
       * 自分の投稿に対する相手の回答内容がキーワードと部分一致
       """

        if form.is_valid():
            # すべての質問の中からキーワードに合致する質問のみ取り出す
            questions = list(Question.objects.filter(Q(title__contains=form.clean()['keyword']) |
                                                  Q(text__contains=form.clean()['keyword'])))

            # 回答内容にキーワードが含まれるもののうち自分が答えた質問のみ取り出す
            replies = list(Reply.objects.filter(Q(text__contains=form.clean()['keyword'])))

            # 自分宛の質問リストを取ってくる（パス含む）
            reply_lists = ReplyList.objects.filter(answerer=request.user)

            # キーワードに合致するすべての質問のうち、自分が投稿した質問と、自分に来た質問を取り出す
            q_list_tmp = []
            r_list_tmp = []
            for ql in questions:
                if ql.questioner == request.user:
                    q_list_tmp.append(ql)
                rl = [rl for rl in reply_lists if ql.id == rl.question.id]
                r_list_tmp.extend(rl)

            # 自分の返信内容とキーワードが合致するものを取り出す
            for r in replies:
                if r.answerer == request.user:
                    rl = [rl for rl in reply_lists if r.question.id == rl.question.id]
                    r_list_tmp.extend(rl)
                elif r.question.questioner == request.user:
                    reply_lists = ReplyList.objects.filter(question=r.question)
                    rl = [rl for rl in reply_lists if r.question.id == rl.question.id]
                    r_list_tmp.extend(rl)

            reply_lists = r_list_tmp

            # キーワードに合致するすべてのタグを取り出す
            tags = list(Tag.objects.filter(Q(name__contains=form.clean()['keyword']))) #キーワードが含まれるタグ（複数）

            # 自分が投稿した質問のタグと一致するもののみ取り出す
            for tag in tags:
                  q_tags = QuestionTag.objects.filter(tag=tag)#タグ名が合致する質問タグ
                  q = [q_tag.question for q_tag in q_tags if q_tag.question.questioner == request.user]
                  q_list_tmp.extend(q)
                  q_list_tmp = list(set(q_list_tmp))
            questions = q_list_tmp

            # 自分が答えた質問のタグと一致するもののみ取り出す
            replies = list(Reply.objects.filter(answerer=request.user))
            for r in replies:
                for tag in tags:
                    q_tags = QuestionTag.objects.filter(tag=tag)#タグ名が合致する質問タグ
                    q = [q_tag.question for q_tag in q_tags if r.question.id == q_tag.question.id and r.answerer == request.user]
                    q_list_tmp.extend(q)
                    q_list_tmp = list(set(q_list_tmp))

            a = []
            b = []
            r_list_tmp = ReplyList.objects.filter(answerer=request.user)
            for tag in tags:
                q_tags = QuestionTag.objects.filter(tag=tag)#タグ名が合致する質問タグ
                for rl in r_list_tmp:#自分に来た質問
                    for q_tag in q_tags:
                        if rl.question.id == q_tag.question.id:
                            a.append(rl)
                            b = list(set(a))
                            reply_lists.extend(b)

            reply_lists = list(set(reply_lists))


    # 自分の質問と自分宛ての質問の状態を調べる
    qa_manager = QAManager(request.user)
    questions = qa_manager.question_state(questions)
    reply_lists = qa_manager.reply_state(reply_lists)

    # 自分と自分宛の質問を結合して時系列に並べる
    qa_list = list()
    qa_list.extend(questions)
    qa_list.extend(reply_lists)
    qa_list = sorted(qa_list, reverse=True, key=lambda x: x[0].date if isinstance(x[0],Question) else x[0].question.date)#OK?

    # プロフィール
    for qa in qa_list:
        if isinstance(qa[0], Question):
            profile = UserProfile.objects.get(user=qa[0].questioner)
        elif isinstance(qa[0], ReplyList):
            profile = UserProfile.objects.get(user=qa[0].question.questioner)
        qa.append(profile)

    histories = None
    return render_to_response('question/top_all.html',
                              {'histories': histories, 'qa_list':qa_list,
                               'last_login': request.user.last_login, 'msg':msg},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
def question_edit(request, id=None, msg=None):
    """
    質問ページ
    """

    # edit
    if id:
        q = get_object_or_404(Question, pk=id)
        # user check
        if q.questioner != request.user:
            print("不正なアクセスです！")
            return redirect('dotchain:top')
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
            print('divlsitdivlsitdivlsitdivlsitdivlsitdivlsitdivlsit')
            print(div_list)
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
                msg = '宛先ユーザが見つかりませんでした。入力された質問は消去されます。\n'
                msg += '次の原因が考えられます。\n'
                msg += '・送信先にユーザがいない\n'
                msg += '・送信先に1日以内にログインしたユーザがいない\n'
                msg += '・送信先に受信拒否のユーザしかいない'
                return render_to_response('question/question_edit.html',
                              {'form': form, 'id': id, 'msg': msg},
                              context_instance=RequestContext(request))
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

            return redirect('dotchain:top')
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
    #if ReplyList.objects.filter(question=q, answerer=request.user, has_replied=True):
    #    msg = 'その質問はすでにパスされています'
    #    return render_to_response('question/top_default.html',{'msg':msg},context_instance=RequestContext(request))

    if q.is_closed:
        msg = 'その質問の回答は締め切られました。'
        return render_to_response('question/top_default.html',{'msg':msg},context_instance=RequestContext(request))

    #replylist = ReplyList.objects.filter(question=q)[0]
    # 各質問について、has_replied=Falseの回答済みリストは一つのみのはず

    replylist = get_object_or_404(ReplyList, question=q, has_replied=False)
    print("rep")

    r = Reply()

    # edit
    if request.method == 'POST':
        form = ReplyEditForm(request.POST, instance=r)

        # 完了がおされたら
        if form.is_valid():
            # この質問の自分あての回答リストを取ってきて、回答済みにしておく
            if(q.questioner!=request.user):
                r_list = get_object_or_404(ReplyList, question=q, answerer=request.user) #has_replied=Falseはいらないと思う
                if r_list.has_replied:
                    msg = 'その質問は自動的にパスされました'
                    return render_to_response('question/top_default.html',{'msg':msg},context_instance=RequestContext(request))
                #r_list.has_replied = True
                r_list.time_limit_date=None
                r_list.save()

                tag_list = QuestionTag.objects.filter(question=q)
                for tag in tag_list:
                    if not UserTag.objects.filter(user=request.user, tag=tag.tag):
                        user_tag = UserTag()
                        user_tag.tag = tag.tag
                        user_tag.user = request.user
                        user_tag.save()
                        print(user_tag)

            r = form.save(commit=False)
            r.question = q
            r.answerer = request.user
            r.draft = form.cleaned_data['draft']
            r.save()

            #質問を締め切る
            #q.is_closed = True
            #q.save()

            msg = '返信しました。'
            return render_to_response('question/top_default.html',{'msg':msg},context_instance=RequestContext(request))
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
     # 自分の質問を取ってきて時系列に並べる
    q = Question.objects.filter(questioner=request.user).order_by('date')

    # 各質問の状態を調べる
    q_manager = QAManager(request.user)
    qa_list = q_manager.question_state(q)

    # プロフィール
    for qa in qa_list:
        if isinstance(qa[0], Question):
            profile = UserProfile.objects.get(user=qa[0].questioner)
        elif isinstance(qa[0], ReplyList):
            profile = UserProfile.objects.get(user=qa[0].question.questioner)
        qa.append(profile)

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
    reply_list = ReplyList.objects.get(id=id)
    if reply_list.has_replied:
        msg = 'すでにパスした質問です。'
        return render_to_response('question/top_default.html',{'msg':msg},context_instance=RequestContext(request))

    qa_manager = QAManager()
    if qa_manager.pass_question(reply_list.question, qa_manager.reply_list_update_random_except):
        msg = '質問をパスしました。'
        return render_to_response('question/top_default.html',{'msg':msg},context_instance=RequestContext(request))
    else:
        reply_list.question.is_closed = True
        reply_list.question.save()
        msg = '質問をパスしました。\n'
        msg += '次の送信先がないため質問は締め切られます。'
        return render_to_response('question/top_default.html',{'msg':msg},context_instance=RequestContext(request))


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
        r = Reply.objects.filter(question=q) # 一つの質問につき返信が複数ある場合はfilterを使うこと
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
        msg = '他の人の質問は閲覧できません。'
        msg = '他の人の質問は閲覧できません。'
        return render_to_response('question/top_default.html',{'msg':msg},context_instance=RequestContext(request)) # TODO　表示できないよページ作る

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

    # プロフィール
    for qa in qa_list:
        if isinstance(qa[0], Question):
            profile = UserProfile.objects.get(user=qa[0].questioner)
        elif isinstance(qa[0], ReplyList):
            profile = UserProfile.objects.get(user=qa[0].question.questioner)
        qa.append(profile)

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

    work_place, created = WorkPlace.objects.get_or_create(name='東京', defaults=dict(name='東京',),)
    work_status, created = WorkStatus.objects.get_or_create(name='在席', defaults=dict(name='在席',),)
    division, created = Division.objects.get_or_create(code=2, name='人事', defaults=dict(code=2, name='人事'))
    p, created = UserProfile.objects.get_or_create(user=request.user,
                                                   defaults=dict(avatar='images/icons/pepper.png',
                                                                 work_place=work_place,
                                                                 work_status=work_status,
                                                                 division=division,
                                                                 accept_question=1,),)


    # ユーザが登録しているタグを取ってくる
    user_tags = UserTag.objects.filter(user=request.user)
    #user_tags = [user_tag.tag for user_tag in user_tags]

    # edit
    if request.method == 'POST':

        form = UserProfileEditForm(request.POST, request.FILES, instance=p)

        # 完了がおされたら
        if form.is_valid():
            print(form)

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

            return redirect('dotchain:mypage')
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
def search(request):

    if request.method == 'GET':
        form = KeywordSearchForm()

    #elif request.method == 'POST':
    #  form = KeywordSearchForm(request.POST)

    return render_to_response('question/question_search.html',
                              {'form': form, 'uname': request.user.last_name+request.user.first_name},
                              context_instance=RequestContext(request))

@login_required(login_url='/accounts/login')
def network(request):
    all_user = [[u.username, 'u{}'.format(u.id), 5*len(Reply.objects.filter(answerer=u))] for u in User.objects.all()]
    all_tag = [[t.name, 't{}'.format(t.id)] for t in Tag.objects.all()]
    all_reply = [['u{}'.format(r.answerer.id),  'u{}'.format(r.question.questioner.id)] for r in Reply.objects.all()]
    all_reply = [[s[0], s[1], all_reply.count([s[0], s[1]]) + all_reply.count([s[1], s[0]])]for s in set([tuple(sorted(r)) for r in all_reply])]
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

    all_pass_temp = ['u{}'.format(r.answerer.id) for r in ReplyList.objects.filter(question=q).order_by('id')]
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
