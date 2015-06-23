from celery import task
from question.models import ReplyList
from question.views import reply_list_update_random_except
import datetime
import pytz

@task
def auto_rand_pass():
    import django
    django.setup()
    tz_tokyo = pytz.timezone('Asia/Tokyo')
    time = datetime.datetime.now()
    print(tz_tokyo.localize(time))
    r_list_list = ReplyList.objects.filter(time_limit_date__lt=tz_tokyo.localize(time), has_replied=False)
    #r_list_list = ReplyList.objects.filter(time_limit_date__it=datetime.datetime.now())

    print("---------------")
    if not r_list_list:
        print("@@@@skip@@@@")
        print("パスすべき質問がありませんでした。スキップします")
        return 1

    for r_list in r_list_list:
        print("###pass###")

        r_list.has_replied = True
        r_list.save()

        reply_lists_pass_users = ReplyList.objects.filter(question=r_list.question, has_replied=True)
        pass_user_list = [r.answerer for r in reply_lists_pass_users]
        pass_user_list.append(r_list.question.questioner)
        new_r_list = reply_list_update_random_except(pass_user_list,  r_list.question)
        if new_r_list != None:
            new_r_list.save()
            print('{0}からの質問「{1}」を{2}から{3}にパスしました。 タイムリミットは{4}'.format(r_list.question.questioner, r_list.question.title, r_list.answerer, new_r_list.answerer, new_r_list.time_limit_date))
        else:
            print('パスできませんでした')




