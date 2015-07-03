from django import template
from ..models import Reply, Question
register = template.Library()

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def pass_check(reply_list, question):
    if not reply_list.time_limit_date:
        return 3

    if question.is_closed:
        return 2

    if reply_list.has_replied:
        return 1

    return 0

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
