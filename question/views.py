import datetime

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User

from accounts.models import UserProfile, WorkStatus, WorkPlace, Division
from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag, QuestionDestination
from question.forms import QuestionEditForm, ReplyEditForm, UserProfileEditForm, KeywordSearchForm
from question.qa_manager import QAManager
from question.robot_reply import ReplyRobot
from question import message_definition as m



# Create your views here.
@login_required(login_url='/accounts/login')
def top_default(request, msg=None):
    """
    トップページ
    """

    form = KeywordSearchForm()
    # 自分の質問を取ってくる
    questions = Question.objects.filter(questioner=request.user)
    # 自分宛の質問リストを取ってくる
    reply_lists = ReplyList.objects.filter(answerer=request.user)

    if request.method == 'POST':
        form = KeywordSearchForm(request.POST)

        """
       以下の質問をキーワード検索で取ってくる
       * 自分がした質問のタイトル・内容・タグいずれかがキーワードと部分一致
       * 相手から自分へ来た質問のタイトル・内容・タグいずれかがキーワードと部分一致
       * 自分の回答内容がキーワードと部分一致
       * 自分の投稿に対する相手の回答内容がキーワードと部分一致
       """
        # 自分宛の質問リストを取ってくる（パス含む）
        reply_lists = ReplyList.objects.filter(answerer=request.user)
        if form.is_valid():
            # すべての質問の中からキーワードに合致する質問のみ取り出す
            questions = list(Question.objects.filter(Q(title__contains=form.clean()['keyword']) |
                                                     Q(text__contains=form.clean()['keyword'])))

            # 回答内容にキーワードが含まれるもののうち自分が答えた質問のみ取り出す
            replies = list(Reply.objects.filter(Q(text__contains=form.clean()['keyword'])))

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

            # -----------------------------------------------------------------------------------

            # キーワードに合致するすべてのタグを取り出す
            tags = list(Tag.objects.filter(Q(name__contains=form.clean()['keyword'])))  # キーワードが含まれるタグ（複数）

            # 自分が投稿した質問のタグと一致するもののみ取り出す
            for tag in tags:
                q_tags = QuestionTag.objects.filter(tag=tag)  # タグ名が合致する質問タグ
                q = [q_tag.question for q_tag in q_tags if q_tag.question.questioner == request.user]
                q_list_tmp.extend(q)
                q_list_tmp = list(set(q_list_tmp))
            questions = q_list_tmp

            # 自分が答えた質問のタグと一致するもののみ取り出す
            replies = list(Reply.objects.filter(answerer=request.user))
            for r in replies:
                for tag in tags:
                    q_tags = QuestionTag.objects.filter(tag=tag)  # タグ名が合致する質問タグ
                    q = [q_tag.question for q_tag in q_tags if
                         r.question.id == q_tag.question.id and r.answerer == request.user]
                    q_list_tmp.extend(q)
                    q_list_tmp = list(set(q_list_tmp))

            a = []
            b = []
            r_list_tmp = ReplyList.objects.filter(answerer=request.user)
            for tag in tags:
                q_tags = QuestionTag.objects.filter(tag=tag)  # タグ名が合致する質問タグ
                for rl in r_list_tmp:  # 自分に来た質問
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
    qa_list = sorted(qa_list, reverse=True,
                     key=lambda x: x[0].date if isinstance(x[0], Question) else x[0].question.date)

    # プロフィール
    for qa in qa_list:
        if isinstance(qa[0], Question):
            profile = UserProfile.objects.get(user=qa[0].questioner)
        elif isinstance(qa[0], ReplyList):
            profile = UserProfile.objects.get(user=qa[0].question.questioner)
        qa.append(profile)

    return render_to_response('question/top_all.html',
                              {'qa_list': qa_list,
                               'last_login': request.user.last_login, 'msg': msg},
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login')
def question_edit(request, id=None, msg=None):
    """
    質問ページ
    """

    # edit
    """
　　#質問の編集機能は今は使っていない
    if id:
        q = get_object_or_404(Question, pk=id)
        # user check
        if q.questioner != request.user:
            return top_default(request, msg=m.INFO_INVALID_ACCESS)
    # new
    else:
   """
    q = Question()

    # edit
    if request.method == 'POST':
        form = QuestionEditForm(request.POST, instance=q)

        # 完了がおされたら
        if form.is_valid():
            # 質問を保存
            q = form.save(commit=False)
            q.update(questioner=request.user, draft=form.cleaned_data['draft'])

            div_list = form.cleaned_data['destination']
            for div in div_list:
                QuestionDestination.objects.create(question=q, tag=div)

            # ランダムに質問者を選んでからReplyListを生成して保存
            qa_manager = QAManager()
            r_list = qa_manager.make_reply_list(q, qa_manager.reply_list_update_random_except)

            if r_list is None:
                q.delete()
                msg = m.INFO_NO_DESTINATION
                return render_to_response('question/question_edit.html',
                                          {'form': form, 'id': id, 'msg': msg},
                                          context_instance=RequestContext(request))
            else:
                r_list.save()

            # 選択されたタグから、新規にQuestionTagを生成して保存
            q_tags = form.cleaned_data['tag']
            for q_tag in q_tags:
                QuestionTag.objects.create(tag=q_tag, question=q)

            # 追加されたタグ名から、新規にTagとQuestionTagを生成して保存
            tag_added_name = form.cleaned_data['tag_added']
            tags = Tag.objects.all()
            tag_name = [t.name for t in tags]
            if tag_added_name != "" and tag_added_name not in tag_name:  # 新規に追加されたタグだったら保存
                t = Tag.objects.create(name=tag_added_name)
                QuestionTag.objects.create(tag=t, question=q)
            return top_default(request, msg=m.INFO_QUESTION_SEND_OK)
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

    if q.is_closed:
        return top_default(request, msg=m.INFO_REPLY_ALREADY_FINISH)

    replylist = get_object_or_404(ReplyList, question=q, has_replied=False)

    r = Reply()

    # edit
    if request.method == 'POST':
        form = ReplyEditForm(request.POST, instance=r)

        # 完了がおされたら
        if form.is_valid():
            if q.questioner != request.user:
                # 回答した質問の制限時間をNoneにしておく
                r_list = get_object_or_404(ReplyList, question=q, answerer=request.user)
                if r_list.has_replied:
                    return top_default(request, msg=m.INFO_QUESTION_ALREADY_AUTO_PASS)
                r_list.update(time_limit_date=None)

                # 回答した人に、質問のタグを付加する
                tag_list = QuestionTag.objects.filter(question=q)
                for tag in tag_list:
                    if not UserTag.objects.filter(user=request.user, tag=tag.tag):
                        UserTag.objects.create(tag=tag.tag, user=request.user)

            r = form.save(commit=False)
            r.update(question=q, answerer=request.user, draft=form.cleaned_data['draft'])

            return top_default(request, msg=m.INFO_REPLY_SEND_OK)
        pass
    # new
    else:
        form = ReplyEditForm(instance=r)

    return render_to_response('question/reply_edit.html',
                              {'form': form, 'question': q, 'id': id, 'replylist': replylist},
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

    # 自分の質問を時系列に並べる
    qa_list = sorted(qa_list, reverse=True,
                     key=lambda x: x[0].date if isinstance(x[0], Question) else x[0].question.date)

    # プロフィール
    for qa in qa_list:
        if isinstance(qa[0], Question):
            profile = UserProfile.objects.get(user=qa[0].questioner)
        elif isinstance(qa[0], ReplyList):
            profile = UserProfile.objects.get(user=qa[0].question.questioner)
        qa.append(profile)

    return render_to_response('question/top_q.html',
                              {'qa_list': qa_list,
                               'last_login': request.user.last_login},
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login')
def question_pass(request, id=None):
    """
    来た質問をパスする。
    次に質問を回す人は、質問者と既にパスした人にはならないようにする。
    また、質問者以外のユーザを質問が回り終わったら、質問者にお知らせする。

    v1.1新機能：ロボット(AI)による自動返信。ある回数だけパスされたら質問から抽出されたキーワードを使って検索URLを返信する。
    """
    reply_list = ReplyList.objects.get(id=id)
    if reply_list.has_replied:
        return top_default(request, msg=m.INFO_QUESTION_ALREADY_AUTO_PASS)

    qa_manager = QAManager()
    pass_success = qa_manager.pass_question(reply_list.question, qa_manager.reply_list_update_random_except)

    if pass_success:
        # 宛先にロボットが含まれるかどうか調べる
        try:
            to_robot = QuestionDestination.objects.filter(question=reply_list.question)
            to_robot = [i for i in to_robot if i.tag.code == 99]
        except QuestionDestination.DoesNotExist:
            to_robot = []

        # 何回目のパスでロボットが返信してくるか。現在は１に固定
        if len(to_robot) and reply_list.question.pass_counter() == 1 and not reply_list.question.has_reply():
            text = ''
            reply_data = ReplyRobot().reply(reply_list.question)
            if len(reply_data['reply_list']) == 0:
                text = "難問です。答えられたらすごいです。"
            else:
                text = "以下のページはどうでしょうか？\n\n" + "\n".join(reply_data['reply_list'])
            if len(reply_data['word_list']) != 0:
                text += "\n\n抽出結果：" + "、".join(reply_data['word_list'])
            text += "\n推定ジャンル：" + reply_data['genre']

            robot, created = User.objects.get_or_create(username='__robot__@dotChain', defaults=dict(first_name='太郎', last_name = 'ロボット',),)
            Reply.objects.create(question=reply_list.question, answerer=robot, text=text)
        return top_default(request, msg=m.INFO_QUESTION_PASS)
    else:
        reply_list.question.update(is_closed=True)
        return top_default(request, msg='{0}\n{1}'.format(m.INFO_QUESTION_PASS, m.INFO_PASS_FINISH))


@login_required(login_url='/accounts/login')
def question_detail(request, id=None):
    """
    質問の詳細を表示する
    """

    # 指定された質問を取ってくる
    q = get_object_or_404(Question, pk=id)

    # 質問のあて先を取ってくる
    d = QuestionDestination.objects.filter(question=q)

    # 質問のタグを取ってくる
    q_tags = QuestionTag.objects.filter(question=q)

    # 質問に対する回答を取ってくる
    # まだ回答が来てない場合のためにget_object_or_404は使わずにこちらを使う
    try:
        r = Reply.objects.filter(question=q)  # 一つの質問につき返信が複数ある場合はfilterを使うこと
    except Reply.DoesNotExist:
        r = None

    # 回答リストを取ってくる
    try:
        reply_list = ReplyList.objects.get(question=q, answerer=request.user)
    except ReplyList.DoesNotExist:
        reply_list = None

    # user check
    if q.questioner != request.user and reply_list == None:
        return top_default(request, msg=m.INFO_QUESTION_INVALID_ACCESS)

    return render_to_response('question/question_detail.html',
                              {'question': q, 'destinations':d, 'q_tags': q_tags, 'reply': r, 'reply_list': reply_list},
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login')
def reply_list(request):
    """
    自分に来た質問一覧を表示する
    """

    # 自分宛の質問のうち、自分の回答待ちになっている質問を取ってきて時系列に並べる
    reply_list = ReplyList.objects.filter(answerer=request.user, has_replied=False)
    reply_list = sorted(reply_list, reverse=True, key=lambda x: x.question.date)

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

    return render_to_response('question/top_r.html',
                              {'qa_list': qa_list, 'last_login': request.user.last_login},
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login')
def mypage(request):
    """
    マイページ
    """

    # ユーザのプロファイルを取ってくる
    p = get_object_or_404(UserProfile, user=request.user)

    # ユーザが登録しているタグを取ってくる
    user_tags = UserTag.objects.filter(user=request.user)

    # edit
    if request.method == 'POST':

        form = UserProfileEditForm(request.POST, request.FILES, instance=p)

        # 完了がおされたら
        if form.is_valid():
            r = form.save(commit=False)
            r.save()

            # 選択されたタグから、新規にQuestionTagを生成して保存
            tags = form.cleaned_data['tag']
            u_tag_names = [t.tag.name for t in user_tags]
            for q_tag in tags:
                if q_tag.name not in u_tag_names:  # ユーザに新規に追加されたタグだったら保存
                    UserTag.objects.create(tag=q_tag, user=request.user)

            # 追加されたタグ名から、新規にTagとQuestionTagを生成して保存
            tag_added_name = form.cleaned_data['tag_added']
            tags = Tag.objects.all()
            tag_name = [t.name for t in tags]
            if tag_added_name != "" and tag_added_name not in tag_name:  # 新規に追加されたタグだったら保存
                t = Tag.objects.create(name=tag_added_name)
                UserTag.objects.create(tag=t, user=request.user)
            return redirect('dotchain:mypage')
        pass
    # new
    else:
        form = UserProfileEditForm(instance=p)

    user_question = Question.objects.filter(questioner=request.user)
    user_reply = Reply.objects.filter(answerer=request.user)
    return render_to_response('question/mypage.html',
                              {'form': form, 'user_tags': user_tags, 'uprof': p, 'uquestion': user_question,
                               'ureply': user_reply},
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login')
def search(request):
    if request.method == 'GET':
        form = KeywordSearchForm()

    return render_to_response('question/question_search.html',
                              {'form': form},
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login')
def network(request):
    all_user = [[u.username, 'u{}'.format(u.id), 5 * len(Reply.objects.filter(answerer=u))] for u in User.objects.all()]
    all_tag = [[t.name, 't{}'.format(t.id)] for t in Tag.objects.all()]
    all_reply = [['u{}'.format(r.answerer.id), 'u{}'.format(r.question.questioner.id)] for r in Reply.objects.all()]
    all_reply = [[s[0], s[1], all_reply.count([s[0], s[1]]) + all_reply.count([s[1], s[0]])] for s in
                 set([tuple(sorted(r)) for r in all_reply])]
    all_userTag = [['u{}'.format(u.user.id), 't{}'.format(u.tag.id)] for u in UserTag.objects.all()]

    return render_to_response('question/network.html',
                              {'all_user': all_user, 'all_reply': all_reply, 'all_tag': all_tag,
                               'all_userTag': all_userTag},
                              context_instance=RequestContext(request))


@login_required(login_url='/accounts/login')
def pass_network(request, id=None):
    q = get_object_or_404(Question, pk=id)

    user_reply_list = ReplyList.objects.filter(question=q).order_by('time_limit_date')[0]
    if ReplyList.objects.filter(question=q, answerer=request.user):
        user_reply_list = ReplyList.objects.get(question=q, answerer=request.user)
    # user check
    if q.questioner != request.user:
        pass
        # 他人の質問は表示できないようにする
        # return HttpResponse("他の人の質問は表示できません！") # TODO　表示できないよページ作る

    all_user = [[u.username, 'u{}'.format(u.id)] for u in User.objects.all()]
    all_tag = [[t.name, 't{}'.format(t.id)] for t in Tag.objects.all()]
    all_reply = [['u{}'.format(r.answerer.id), 'u{}'.format(r.question.questioner.id)] for r in Reply.objects.all()]
    all_reply = set([tuple(sorted(r)) for r in all_reply])
    all_userTag = [['u{}'.format(u.user.id), 't{}'.format(u.tag.id)] for u in UserTag.objects.all()]

    all_pass_temp = ['u{}'.format(r.answerer.id) for r in ReplyList.objects.filter(question=q).order_by('id')]
    all_pass_temp.insert(0, 'u{}'.format(q.questioner.id), )
    all_pass = [[all_pass_temp[n - 1], all_pass_temp[n]] for n in range(1, len(all_pass_temp))]
    print(request.user)

    return render_to_response('question/pass_network.html',
                              {'user_reply_list': user_reply_list,
                               'you': [request.user.username, 'u{}'.format(request.user.id)], 'all_user': all_user,
                               'all_reply': all_reply, 'all_tag': all_tag, 'all_userTag': all_userTag,
                               'all_pass': all_pass},
                              context_instance=RequestContext(request))
