import requests
import logging

import nltk
import scipy

from functions import pre_process, get_data_from_database, transform_digit, choose_answer


class Bot:
    def __init__(self, root_path):
        nltk.download('stopwords')
        self.logger = logging.getLogger('bot')
        self.logger.debug('init')
        #self.topic_model = None
        #self.topic_model = load_model(root_path + '/static/topic_predict.model')
        #if self.topic_model is not None:
        #    print('topic model load')
        self.answers, self.questions, self.t2v, self.tf_vect = pre_process(root_path)

    def get_sentence(self, input_request):
        user_data = get_data_from_database(input_request=input_request)
        self.logger.debug('user data: {}'.format(user_data))

        #if user_data[u'LastBotMessage'] is None:
        message = input_request['message']
        #else:
        #    message = user_data[u'LastBotMessage'] + ' ' + user_data[u'LastUserMessage']

        self.logger.debug('input message: {}'.format(message))

        vec = self.tf_vect.transform([message]).toarray()[0]
        distance = 1.0
        index = 0
        for i, x in enumerate(self.answers):
            dist = scipy.spatial.distance.cosine(vec, self.t2v[i])
            if dist < distance:
                distance = dist
                index = i
        self.logger.debug('similar sentence: {}'.format(self.answers[index][0]))
        #if index < len(self.answers) - 1:
        #    index = index + 1
        #else:
        #    index = 0
        lasttopicnumber = self.answers[index][1]
        lastrownumber = self.answers[index][2]
        response, lasttopicnumber, lastrownumber = choose_answer(self.answers, lasttopicnumber, lastrownumber+1)
        self.logger.debug('answer sentence: {}'.format(response))
        if response is None:
            response = 'Finish dialog. ' + self.answers[0][0]
            lasttopicnumber = self.answers[0][1]
            lastrownumber = self.answers[0][2]
        state = 0
        r = requests.get('https://api.textgears.com/check.php', params={'text': message, 'key':'PhdFWWMyoGkzCp8q'})
        return {'message': response, 'errors': r.json(), 'lasttopicnumber': lasttopicnumber, 'lastrownumber': lastrownumber, 'state': state}
