import requests
import json

def request_keyword_extraction(message):
    api_key = "517836486f5739754a4d41684b54346b6e365a55486475564648756b58773563504c30414d7759476b5638"
    url = "https://api.apigw.smt.docomo.ne.jp/gooLanguageAnalysis/v1/entity?APIKEY=" + api_key
    body = {"request_id": "record001",
            "sentence": message,
            "class_filter": "ART|ORG|PSN|LOC|DAT|TIM"}
    return requests.post(url, data=body).json()

def request_stack_over_flow(keyword_list):
    keyword = ";".join(keyword_list)
    print(keyword)
    url = "https://api.stackexchange.com/2.2/questions?order=desc&sort=votes&tagged={0}&site=ja.stackoverflow".format(keyword)
    return requests.get(url).json()

def reply(message):
    word_list = [ne[0] for ne in request_keyword_extraction(message)['ne_list']]
    reply_list = [item['title'] + "\n" + item['link'] for item in request_stack_over_flow(word_list)['items']]
    return reply_list[0:3]
