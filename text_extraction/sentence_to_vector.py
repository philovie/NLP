import numpy as np
import fasttext
import jieba
from six.moves import cPickle as pickle
from collections import defaultdict


class sentence_2_vector:

    def __init__(self) -> None:
        self.word_frequence = self.__init_frenquence()
        self.model = fasttext.load_model('D:/PyCharmProjects-git/practice/wiki-corpus-model.bin')

    def __init_frenquence(self):
        with open('D:/PyCharmProjects-git/practice/word_frequence.pickle', 'rb') as f:
            data = pickle.load(f)
            data = defaultdict(lambda: 1 / data['words_count'], data)
        return data

    def get_word_frenquence(self, word):
        return self.word_frequence[word]

    def cut(self,string):
        return ' '.join(jieba.cut(string))

    def get_sentence_vec(self, sentences):
        print(f'sentences is {sentences}')
        a = 0.001
        row = self.model.get_dimension()
        col = len(sentences)
        sentences_matrix = np.zeros((col, row))
        for i, sentence in enumerate(sentences):
            print(f'sentence is {sentence}')
            if len(sentence) == 0: continue
            words = self.cut(sentence).split(' ')
            length = len(words)
            if length == 0: continue
            sentence_vector = np.zeros(row)
            for word in words:
                pw = self.get_word_frenquence(word)
                if pw == 0: continue
                w = a / (a + pw)
                try:
                    vec = np.array(self.model.get_word_vector(word))
                    sentence_vector += w * vec
                except:
                    pass
            sentences_matrix[i, :] += sentence_vector
            sentences_matrix[i, :] /= length
        sentences_matrix = np.mat(sentences_matrix)
        u, s, vh = np.linalg.svd(sentences_matrix)
        sentences_matrix = sentences_matrix - u * u.T * sentences_matrix
        return sentences_matrix