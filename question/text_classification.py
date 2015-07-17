#coding:utf-8
import math
import sys
from collections import defaultdict

class NaiveBayes:
    def __init__(self):
        self.categories = set()
        self.vocabularies = set()
        self.word_count = {}
        self.cat_count = {}
        self.denominator = {}
        self.hit_count = 0

    # 訓練データ登録
    def train(self, text_data):
        for words in text_data:
            cat = words[0]
            self.categories.add(cat)
        for cat in self.categories:
            self.word_count[cat] = defaultdict(int)
            self.cat_count[cat] = 0
        for words in text_data:
            cat, doc = words[0], words[1:]
            self.cat_count[cat] += 1
            for word in doc:
                self.vocabularies.add(word)
                self.word_count[cat][word] += 1
        for cat in self.categories:
            self.denominator[cat] = sum(self.word_count[cat].values()) + len(self.vocabularies)

    def classify(self, doc):
        best_cat = None
        max_p = -sys.maxsize
        for cat in self.cat_count.keys():
            p = self.score(doc, cat)
            if p > max_p:
                max_p = p
                best_cat = cat
        return best_cat

    def word_prob(self, word, cat):
        self.hit_count += self.word_count[cat][word]
        return float(self.word_count[cat][word] + 1) / float(self.denominator[cat])

    def score(self, doc, cat):
        total = sum(self.cat_count.values())
        score = math.log(float(self.cat_count[cat]) / total)  # log P(cat)
        for word in doc:
            score += math.log(self.word_prob(word, cat))  # log P(word|cat)
        return score

    def start(self, doc):
        train_data = []
        for line in open('./question/train_model/category_model.csv', mode='r', encoding='utf-8'):
            train_data.append(line.split(","))
        self.train(train_data)
        genre = self.classify(doc)
        # 一件もヒットしなかったらetc
        if self.hit_count == 0:
            genre = "etc"
        return genre
