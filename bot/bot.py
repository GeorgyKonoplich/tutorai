import requests
import logging
import json

import nltk
import scipy

from functions import pre_process, get_data_from_database, transform_digit, choose_answer
from pb_py import main as API
from grammar import get_errors_plural_forn_nouns


class Bot:
    def __init__(self, root_path):
        self.logger = logging.getLogger('bot')
        self.logger.debug('init')
        #self.topic_model = None
        #self.topic_model = load_model(root_path + '/static/topic_predict.model')
        #if self.topic_model is not None:
        #    print('topic model load')
        #self.answers, self.questions, self.t2v, self.tf_vect = pre_process(root_path)

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

    def get_sentence1(self, input_request):
        message = input_request['message']
        self.logger.debug('input message: {}'.format(message))

        host = 'aiaas.pandorabots.com'
        user_key = '836ff6d5a6fb542fd562b893edb4a98d'
        app_id = '1409617127698'
        botname = 'tutor1'
        result = API.talk(user_key, app_id, host, botname, message, clientID=input_request['userId'])
        response = result['response']
        session_id = result['sessionid']


        state = 0
        lasttopicnumber = 0
        lastrownumber = 0

        r = requests.get('https://api.textgears.com/check.php', params={'text': message, 'key':'PhdFWWMyoGkzCp8q'})
        self.logger.debug('check plural form')
        #errors = get_errors_plural_forn_nouns(message)

        url = "https://languagetool.org/api/v2/check"

        payload = "text=" + message + "&language=en-US&enabledOnly=false"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'accept': "application/json",
            'cache-control': "no-cache",
            'postman-token': "5c738aa3-20d4-263f-dbca-d3d747e36ec9"
        }

        response1 = requests.request("POST", url, data=payload, headers=headers)
        lang_tool_answer = json.loads(response1.text)
        return {'languagetool_errors':lang_tool_answer, 'message': response, 'lasttopicnumber': lasttopicnumber, 'lastrownumber': lastrownumber, 'state': state, 'sessionId': session_id, 'tutor_errors': {}}
        #return {'languagetool_errors': lang_tool_answer, 'message': message, 'lasttopicnumber': lasttopicnumber, 'lastrownumber': lastrownumber, 'state': state, 'sessionId': 0, 'tutor_errors': {}}
