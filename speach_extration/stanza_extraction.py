# coding=utf8
import stanza

def to_dot(dependencies):
    nodes = {}
    for i, dependency in enumerate(dependencies):
        nodes[i] = dependency

    s = 'digraph G{\n'
    s += 'edge [dir=forward]\n'
    s += 'node [shape=plaintext fontname="SimSun"]\n'

    # Draw the remaining nodes
    for node in sorted(nodes.values(), key=lambda v: v['id']):
        s += '\n%s [label="%s (%s)"]' % (
            node['id'],
            node['id'],
            node['text'],
        )
        s += '\n%s -> %s [label="%s"]' % (node['head'], node['id'], node['deprel'])
    s += "\n}"
    return s

class extraction():

    def __init__(self) -> None:
        super().__init__()
        self.__zh_nlp = stanza.Pipeline('zh', processors='tokenize,pos,lemma,ner,depparse', verbose=False, use_gpu=True)
        self.__get_speak_words()

    def __get_speak_words(self):
        filepath = 'D:/PyCharmProjects-git/NLP/speach_extration/speak_words.txt'
        self.__speak_words, lines = [], []
        with open(filepath, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            self.__speak_words += [line.strip()]

    def __get_dependencies(self,corpus):
        zh_doc = self.__zh_nlp(corpus)
        return zh_doc.sentences

    def __analysize(self,sentences):
        speak_results,subjects,verbs,Objects = [],[],[],[]
        for i, sentence in enumerate(sentences):
            segments = sentence.to_dict()
            object_head = None
            root_id = None
            ahead = None
            subject = ''
            verb = ''
            Object = ''
            for segment in segments:
                if segment['deprel'] == 'root' and segment['upos'] == 'VERB' and segment['text'] in self.__speak_words:
                    root_id = segment['id']
                    verb = segment['text']
                if root_id and int(segment['id']) > int(root_id) and segment['upos'] != 'PUNCT':
                    object_head = int(segment['id'])
                    break

            for segment in segments:
                if str(segment['head']) == str(root_id) and segment['deprel'] == 'nsubj':
                    if segment['upos'] == 'PROPN':
                        subject = segment['text']
                    else:
                        subject = segment['text']
                        subject_id = segment['id']
                        for segment in segments:
                            if str(segment['head']) == str(subject_id) and segment['upos'] == 'PROPN':  # and segment['deprel'] == 'nmod'
                                ahead = segment['text']
                                subject_id = segment['id']
                        if ahead:
                            subject = ahead + subject
                        else:
                            subject = None
                    break
            for segment in segments:
                if object_head and int(segment['id']) >= int(object_head):
                    Object += segment['text']
            if subject:
                subjects += [subject]
                verbs += [verb]
                Objects += [Object]
                speak_results += [subject + '->' + verb + '->' +Object]
        return (subjects,verbs,Objects)

    def extraction(self,corpus):
        if corpus.strip():
            return self.__analysize(self.__get_dependencies(corpus))
        else: return ([],[],[])
extraction = extraction()
while(True):
    corpus = input('please enter corpus:')
    subjects,verbs,Objects = extraction.extraction(corpus)
    for i,subject in enumerate(subjects):
        print(f'{subject}->{verbs[i]}->{Objects[i]}')