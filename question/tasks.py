from celery import task
from accounts.models import User
from question.qa_manager import QAManager
from question.models import Reply, ReplyList, QuestionDestination
from question.robot_reply import ReplyRobot
from django.db.models import Q
import datetime
import pytz

@task
def auto_rand_pass():
    import django
    django.setup()
    tz_tokyo = pytz.timezone('Asia/Tokyo')
    time = datetime.datetime.now()
    print(tz_tokyo.localize(time))
    reply_list_list = ReplyList.objects.filter(time_limit_date__lt=tz_tokyo.localize(time), has_replied=False).filter(~Q(time_limit_date=None))
    #r_list_list = ReplyList.objects.filter(time_limit_date__it=datetime.datetime.now())

    from one_month import settings

    print("---------------")
    if not reply_list_list:
        print("@@@@skip@@@@")
        print("パスすべき質問がありませんでした。スキップします")
        return 1

    for reply_list in reply_list_list:
        print("###pass###")
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
                    text += "難問です。答えられたらすごいです。\n"
                else:
                    text = "[StackOverFlowより] 以下のページはどうでしょうか？\n\n" + "\n".join(reply_data['reply_list']) + "\n"
                if len(reply_data['word_list']) != 0:
                    urls = []
                    for w in reply_data['word_list']:
                        # すべてのユーザの過去の全質問（各質問の回答は含まない）の中から、抽出結果でキーワード検索をかける（最大３件）
                        questions, reply_lists = QAManager.search_keyword_all_user(keyword=str(w), question=True, tag=True,
                                                                                   reply=False)
                        for q in questions:
                            if q.id != reply_list.question.id and len(urls) <= 2:
                                urls.append(q.title + "\n" + 'http://' + settings.HOST_NAME + '/dotchain/q_detail/' + str(q.id) + '\n')
                    text += "\n[過去の質問より] 以下のページはどうでしょうか？\n\n" + "\n".join(list(set(urls))) if len(
                        urls) else "\n過去の関連質問はありませんでした。"
                    text += "\n\n抽出結果：" + "、".join(reply_data['word_list'])
                text += "\n推定ジャンル：" + reply_data['genre']

                robot, created = User.objects.get_or_create(username='__robot__@dotChain',
                                                            defaults=dict(first_name='太郎', last_name='ロボット', ), )
                Reply.objects.create(question=reply_list.question, answerer=robot, text=text)
        else:
            reply_list.question.update(is_closed=True)


