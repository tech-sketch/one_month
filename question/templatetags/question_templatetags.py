from django import template
from ..models import Reply, Question
register = template.Library()

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def pass_check(reply_list, question):
    if reply_list == None:
        return ''

    if not reply_list.time_limit_date:
        return 'タイマーは設定されていません。'

    if question.is_closed:
        return '質問は締め切られました。'

    if reply_list.has_replied:
        return 'パス済みです'

    return '<h3>タイムリミットまで残り</h3><div id="countdown" style="z-index: 1000;"></div>'

@register.filter
def pass_reply_list(reply_list):
    reply_list.has_replied = True
    reply_list.save()
    return ''

@register.filter
def comment_counter(q):

    if type(q) is Question:
        return Reply.objects.filter(question=q).count()
    else:
        return Reply.objects.filter(question=q.question).count()
