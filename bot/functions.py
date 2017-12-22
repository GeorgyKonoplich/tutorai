import os
import re
import requests
import inflect

import numpy as np

from keras.models import load_model
from random import shuffle
from sklearn.feature_extraction.text import TfidfVectorizer

def pre_process(root_path):
    classes = np.load(root_path + '/static/classes.npy').item()
    print(classes)
    dialog_folder = root_path + '/static/dialogs_new_format/'
    all_sentences = []
    targets = []
    for txt in os.listdir(dialog_folder):
        lines = open(dialog_folder + txt, 'r').readlines()
        lines = list(filter(lambda x: x != '\n', lines))
        prepared_sentences = []
        for s in lines:
            sentence = ''.join(x for x in s if
                                   x.isalpha() or x.isdigit() or x == ' ' or x == '.' or x == '?' or x == '!' or x == ',' or x == '\'')
            sentence = re.sub(' +', ' ', sentence)
            prepared_sentences.append(sentence)
        all_sentences.append(prepared_sentences)
        target = ''.join([x if not x.isdigit() else '' for x in txt.split('.')[0]])
        targets.append(target)

    answers = []
    questions = []
    texts = []
    for i, theme in enumerate(all_sentences):
        words = all_sentences[i][0].split()
        s = ' '.join([word for word in words[2:]])
        questions.append((s, classes[targets[i]]))
        for j, line in enumerate(all_sentences[i]):
            if line[0] != ' ':
                words = line.split()
                index = int(words[0].split('.')[0])
                line = ' '.join([word for word in words[2:]])
            else:
                words = line.split()
                line = ' '.join([word for word in words[1:]])

            line = transform_digit(line) #todo: think about this
            #mean = word_averaging(w2v, line.split())
            texts.append(line)
            answers.append((line, classes[targets[i]], index, i))

    tf_vect = TfidfVectorizer(preprocessor=None)
    tf_vect.fit(texts)
    text2vec = list(tf_vect.transform(texts).toarray())
    return answers, questions, text2vec, tf_vect


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


def get_data_from_database(input_request):
    response = requests.get('http://tutorai-env.33zqcsby6q.us-east-1.elasticbeanstalk.com/api/messagesapi/GetLastUserChain',
                     params={'userId': input_request['userId'],
                             'connectionId': input_request['connectionId']})
    return response.json()


def choose_answer(answers, theme, index):
    answer = []
    for i, x in enumerate(answers):
        if x[1] != theme:
            continue
        if x[2] == index:
            answer.append(x)
    if len(answer) > 0:
        shuffle(answer)
        return answer[0][0], answer[0][1], answer[0][2]
    else:
        return None, None, None
