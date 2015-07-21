import requests
import re
from question.text_classification import NaiveBayes

class ReplyRobot:
    def __init__(self):
        self.word_list = []
        self.question_genre = 'etc'
        self.question_tags_name = None
        self.api_key = "dj0zaiZpPVkzR3VJbFlBUERxTyZzPWNvbnN1bWVyc2VjcmV0Jng9MjM-"

    @staticmethod
    def remove_source_code(message):
        return re.sub(r'[^亜-熙ぁ-んァ-ヶ]{30,}', "", message)

    def request_keyword_extraction(self, message):
        url = "http://jlp.yahooapis.jp/KeyphraseService/V1/extract?appid=" + self.api_key
        print(self.remove_source_code(message))
        param = {
            "sentence": self.remove_source_code(message),
            "output": "json"
        }
        result = requests.post(url, data=param)
        print("request:" + result.text)
        return result.json()

    def request_stack_over_flow(self):
        re_word_list = [re.sub(r'\.|#|&|\?|:|=', "", word) for word in self.word_list[:3]]
        keyword_join = " ".join(re_word_list)
        print(keyword_join)
        url = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=votes&body={0}&site=ja.stackoverflow".format(
        keyword_join)
        result_json = requests.get(url).json()
        # 検索結果が０件だった場合
        if len(result_json['items']) == 0:
            for keyword in re_word_list:
                new_url = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=votes&body={0}&site=ja.stackoverflow".format(
                keyword)
                result_json = requests.get(new_url).json()
                if len(result_json['items']) != 0:
                    break
        return result_json

    def get_answer(self):
        # 質問にタグがついているかどうか
        if len(self.question_tags_name) != 0:
                self.word_list = self.question_tags_name
        if self.question_genre == 'IT':
            reply_list = [item['title'] + "\n" + item['link'] for item in self.request_stack_over_flow()['items']]
        elif self.question_genre == 'food':
            reply_list = []
        elif self.question_genre == 'etc':
            reply_list = []
        return {"reply_list": reply_list[:3], "word_list": self.word_list[:3], "genre": self.question_genre}

    def reply(self, question):
        self.question_tags_name = question.get_tags_name()
        key_word_json = self.request_keyword_extraction(question.text)
        if len(key_word_json) != 0:
            self.word_list = [k for k, v in sorted(key_word_json.items(), key=lambda x: x[1], reverse=True)]
            self.question_genre = NaiveBayes().start(self.word_list)
        return self.get_answer()

