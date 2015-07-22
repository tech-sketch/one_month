from django import template
from ..models import Reply, Question, ReplyList
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

@register.filter
def pass_counter(q):

    if type(q) is Question:
        return ReplyList.objects.filter(question=q, has_replied=True).count()
    else:
        return ReplyList.objects.filter(question=q.question, has_replied=True).count()

@register.filter
def count_line(text, num):
    """
    トップ画面で使う。カードの本文の行数を数える。改行＋折り返しで行数を判定する。
    :param text: 本文
    :param num: カード一行あたりの文字数
    :return: 本文の行数
    """

    br_split = text.partition('¥n')
    l = len(br_split)
    for line in br_split:
        if len(line) > num:
            l += len(line)/num-1
    return l
