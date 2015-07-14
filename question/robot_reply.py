import requests

def request_keyword_extraction(message):
    api_key = "dj0zaiZpPVkzR3VJbFlBUERxTyZzPWNvbnN1bWVyc2VjcmV0Jng9MjM-"
    url = "http://jlp.yahooapis.jp/KeyphraseService/V1/extract?appid=" + api_key
    param = {
        "sentence": message,
        "output": "json"
    }
    result = requests.post(url, data=param)
    print("request:" + result.text)
    return result.json()


def request_stack_over_flow(key_word_list):

    keyword_join = " ".join(key_word_list)
    print("keyword_join" + keyword_join)
    url = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=votes&body={0}&site=ja.stackoverflow".format(keyword_join)
    result_json = requests.get(url).json()
    # 検索結果が０件だった場合
    if len(result_json['items']) == 0:
        for keyword in key_word_list:
            new_url = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=votes&body={0}&site=ja.stackoverflow".format(
                keyword)
            result_json = requests.get(new_url).json()
            if len(result_json['items']) != 0:
                break

    return result_json


def reply(question):
    tags_name = question.get_tags_name()
    # 質問にタグがついているかどうか
    if len(tags_name) != 0:
        reply_list = [item['title'] + "\n" + item['link'] for item in request_stack_over_flow(tags_name[:3])['items']]
    else:
        key_word_json = request_keyword_extraction(question.text)
        word_list = [k for k, v in sorted(key_word_json.items(), key=lambda x: x[1], reverse=True)]
        reply_list = [item['title'] + "\n" + item['link'] for item in request_stack_over_flow(word_list[:3])['items']]
    return reply_list[:3]
