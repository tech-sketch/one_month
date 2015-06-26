#-*- coding: utf-8 -*-

from enum import Enum

from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag

class QuestionState(Enum):
    pending = 0
    solved = 1
    unsolved = 2

class ReplyState(Enum):
    pending = 0
    replied = 1
    passed = 2

class QAManager():
    def __init__(self, user):
        self.user = user

    #その質問のQuestionStateを調べるメソッド
    def question_state(self, question_list):

        if isinstance(question_list, Question):
            print('[qa_manager:question_state] Warning: the arg is not a type Question!')
            print('[qa_manager:question_state] Returns None')
            return None

        qa_list = list()
        #自分の質問が解決済みかどうか調べる
        for q in question_list:
            r = Reply.objects.filter(question=q) # いまの仕様では返信は一つのはず
            if len(r): #解決済み
                qa_list.append([q, QuestionState.solved.name])
            else:
                if True: #TODO 未解決or回答待ちの判定は未実装です！！！
                    #qa_list.append([q, QuestionState.unsolved.name]) #未解決
                    qa_list.append([q, QuestionState.pending.name]) #未解決
                else:
                    qa_list.append([q, QuestionState.pending.name]) #回答待ち

        return  qa_list


    #その質問のReplyStateを調べるメソッド
    def reply_state(self, reply_list):

        if isinstance(reply_list, ReplyList):
            print('[qa_manager:reply_state] Warning: the arg is not a type Question!')
            print('[qa_manager:reply_state] Returns None')
            return None

        qa_list = list()

        for rl in reply_list:
            if not rl.has_replied:
                qa_list.append([rl, ReplyState.pending.name])
            else:
                r = Reply.objects.filter(question=rl.question, answerer=self.user) #最大一つしか出てこないはず
                if len(r): #自分が回答した
                    qa_list.append([rl, ReplyState.replied.name])
                else: # パスした
                    qa_list.append([rl, ReplyState.passed.name])

        return qa_list