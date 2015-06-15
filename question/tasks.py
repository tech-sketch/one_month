from celery import task
from question.models import ReplyList
from question.views import reply_list_update_random
import datetime
import pytz

@task
def auto_rand_pass():
    tz_tokyo = pytz.timezone('Asia/Tokyo')
    time = datetime.datetime.now()
    #print(tz_tokyo.localize(time))
    r_list_list = ReplyList.objects.filter(time_limit_date__lt=tz_tokyo.localize(time), has_replied=False)
    #r_list_list = ReplyList.objects.filter(time_limit_date__it=datetime.datetime.now())


    print("---------------")
    for r_list in r_list_list:
        print("###pass###")
        print(r_list.question.title)
        print(r_list.time_limit_date)

        r_list.has_replied = True
        r_list.save()

        new_r_list = reply_list_update_random( r_list.answerer,  r_list.question)
        new_r_list.save()
