import os
import re
import inflect
import scipy

from random import shuffle
from sklearn.feature_extraction.text import TfidfVectorizer


def pre_process(root_path):
    dialog_folder = root_path + '/static/dialogs_vd/'
    documents = {}
    all_sentences = []
    for txt in os.listdir(dialog_folder):
        lines = open(dialog_folder + txt, 'r').readlines()
        filename = ''.join([x if not x.isdigit() else '' for x in txt.split('.')[0]])
        dialog_graph = {}
        is_nodes = False
        for line in lines:
            if line == '\n':
                is_nodes = True
                continue
            if is_nodes:
                line = re.sub(' +', ' ', line)
                x = int(line.split(' ')[0])
                y = int(line.split(' ')[1])
                dialog_graph[x]['nodes'].append(y)
            else:
                sentence = ''.join(x for x in line if x.isalpha()
                                   or x.isdigit() or x == ' '
                                   or x == '.' or x == '?' or x == '!'
                                   or x == ',' or x == '\'')
                sentence = re.sub(' +', ' ', sentence)
                idx = int(sentence.split('.')[0])
                reply = '.'.join(sentence.split('.')[1:])
                if reply[0] == ' ':
                    reply = reply[1:]
                dialog_graph[idx] = {'sentence': reply, 'nodes': []}
                all_sentences.append(reply)

        documents[filename] = dialog_graph
        tf_vect = TfidfVectorizer(preprocessor=None)
        tf_vect.fit(all_sentences)
    return documents, all_sentences, tf_vect


def find_similar_sentence(input_sentence, tf_vect, documents, theme=None, sentence_id=None):
    min_distance = 1.0
    min_document = None
    min_node = None
    for document in documents:
        if (theme is None) or (document == theme):
            for node in documents[document]:
                if (sentence_id is None) or (node in documents[theme][sentence_id]['nodes']):
                    sentence = documents[document][node]['sentence']
                    input_vec = tf_vect.transform([input_sentence]).toarray()[0]
                    vec = tf_vect.transform([sentence]).toarray()[0]
                    distance = scipy.spatial.distance.cosine(input_vec, vec)
                    if distance < min_distance:
                        min_distance = distance
                        min_document = document
                        min_node = node
    return min_distance, min_document, min_node


def choose_answer(documents, document, node):
    answer = []
    for x in documents[document][node]['nodes']:
        answer.append(x)
    if len(answer) > 0:
        shuffle(answer)
        return answer[0]
    else:
        return None


def transform_digit(sentence):
    words = sentence.split(' ')
    ie = inflect.engine()
    changed_words = []
    for x in words:
        stop = ''
        if x[-1] == '.' or x[-1] == '?' or x[-1] == '!' or x[-1] == ',':
            stop = x[-1]
            x = x[0:-1]
        if x.isdigit():
            x = ie.number_to_words(x)
            x = re.sub('-', ' ', x)
        x = x + stop
        changed_words.append(x)
    return ' '.join(changed_words)
