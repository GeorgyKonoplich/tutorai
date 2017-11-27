import os
import re

import inflect
import nltk
import numpy as np
import scipy

from sklearn.feature_extraction.text import TfidfVectorizer
from keras.models import load_model


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


class Bot:
    def __init__(self, root_path):
        nltk.download('stopwords')
        #self.topic_model = None
        #self.topic_model = load_model(root_path + '/static/topic_predict.model')
        #if self.topic_model is not None:
        #    print('topic model load')
        self.answers, self.questions, self.t2v, self.tf_vect = pre_process(root_path)

    def get_sentence(self, message):
        vec = self.tf_vect.transform([message]).toarray()[0]
        distance = 1.0
        index = 0
        for i, x in enumerate(self.answers):
            dist = scipy.spatial.distance.cosine(vec, self.t2v[i])
            if dist < distance:
                distance = dist
                index = i
        print(self.answers[index])
        if index < len(self.answers) - 1:
            response = self.answers[index+1][0]
        else:
            response = self.answers[0][0]
	userMsgId = '1a9cd3c3-07ea-4f6b-bcb8-5387b3ff0895'
	connectionid = 'e70d6890-0523-45ef-a2d1-02e7543ff328'
	lasttopicnumber = 0
	lastrownumber = 0
	state = 0
	return {'message': response, 'errors': {'0 errors':'you are cool guy'}, 'userMsgId': userMsgId, 'connectionId': connectionid, 'lasttopicnumber': lasttopicnumber, 'lastrownumber': lastrownumber, 'state': state}
