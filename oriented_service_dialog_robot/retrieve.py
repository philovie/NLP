import pandas as pd
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine
from functools import reduce
from operator import and_
from collections import defaultdict


class retrieve():

    def __init__(self) -> None:
        super().__init__()
        self.__get_stop_words()
        self.__load_data()
        self.__tfidfrizer()

    @classmethod
    def __cut(self,string): return ' '.join(jieba.cut(string))

    @classmethod
    def __get_stop_words(self):
        filepath = 'D:/PyCharmProjects-git/NLP/oriented_service_dialog_robot/stopwords.txt'
        self.__stop_words, lines = [], []
        with open(filepath, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            self.__stop_words += [line.strip()]
        print(self.__stop_words)

    @classmethod
    def __load_data(self):
        file_path = 'D:/share folder/项目四.csv'
        self.__dialog = pd.read_csv(file_path)
        self.__question = self.__cut_question(self.__dialog['question'])
        self.__answer = self.__dialog['answer']

    @classmethod
    def __cut_question(self,questions):
        for i, sentence in enumerate(questions):
            sentence = str(sentence)
            if not sentence.strip(): continue
            questions[i] = self.__cut(sentence)
            if i % 1000 == 0:
                print(i)
        return questions

    @classmethod
    def __tfidfrizer(self):
        self.__vectorized = TfidfVectorizer()

        self.__X = self.__vectorized.fit_transform(self.__question)

        self.__transposed_x = self.__X.transpose().toarray()

        self.__X_array = self.__X.toarray()

        self.__news_content = [self.__cut(n) for n in self.__question]

        self.__word_2_id = defaultdict(lambda :-1, self.__vectorized.vocabulary_)


    @classmethod
    def __distance(self,v1, v2):
        return cosine(v1, v2)

    @classmethod
    def __search_engine(self,query):
        """
        @query is the searched words, splited by space
        @return is the related documents which ranked by tfidf similarity
        """
        words = query.split()

        query_vec = self.__vectorized.transform([' '.join(words)]).toarray()[0]

        candidates_ids = [self.__word_2_id[w] for w in words]

        documents_ids = [
            set(np.where(self.__transposed_x[_id])[0]) for _id in candidates_ids
        ]
        sorted_docuemtns_id = []
        if len(documents_ids) > 0 :
            merged_documents = reduce(and_, documents_ids)
            sorted_docuemtns_id = sorted(merged_documents, key=lambda i: self.__distance(query_vec, self.__X[i].toarray()))

        return sorted_docuemtns_id

    @classmethod
    def __preprocess(self,query):
        query_words = self.__cut(query).split(' ')
        query_words_remove_stop_words = []
        for i, query_word in enumerate(query_words):
            if query_word not in self.__stop_words:
                query_words_remove_stop_words += [query_word]
        query_words = ' '.join(query_words_remove_stop_words)
        print(query_words)
        return query_words


    def search(self,query):
        answers_ids = self.__search_engine(self.__preprocess(query))
        if len(answers_ids) != 0:
            answer_id = answers_ids.pop(0)
        else:
            answer_id = None
        if answer_id:
            return self.__answer[answer_id]
        else:
            return "我不是太懂你的问题，能换种方式问我嘛..."


retrieve = retrieve()
print('让我们开始聊天吧')
query = input()
while(True):
    print(retrieve.search(query))
    query = input()