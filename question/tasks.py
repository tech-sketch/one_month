from celery import task
from question.models import ReplyList
from question.qa_manager import QAManager
import datetime
import pytz

@task
def auto_rand_pass():
    import django
    django.setup()
    tz_tokyo = pytz.timezone('Asia/Tokyo')
    time = datetime.datetime.now()
    print(tz_tokyo.localize(time))
    reply_list_list = ReplyList.objects.filter(time_limit_date__lt=tz_tokyo.localize(time), has_replied=False)
    #r_list_list = ReplyList.objects.filter(time_limit_date__it=datetime.datetime.now())

    print("---------------")
    if not reply_list_list:
        print("@@@@skip@@@@")
        print("パスすべき質問がありませんでした。スキップします")
        return 1

    for reply_list in reply_list_list:
        print("###pass###")
        qa_manager = QAManager()
        qa_manager.pass_question(reply_list.question, qa_manager.reply_list_update_random_except)




