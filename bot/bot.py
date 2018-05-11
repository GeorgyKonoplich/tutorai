import requests
import logging
import json
import random
import nltk

from bot.functions import pre_process, choose_answer, find_similar_sentence
from common.cache.service import set_data, get_data


class Bot:
    def __init__(self, root_path):
        self.logger = logging.getLogger('bot')
        self.logger.debug('init')
        self.documents, self.all_sentences, self.tf_vect = pre_process(root_path)
        self.root_path = root_path

    def get_sentence(self, input_request):
        message = input_request['message']
        user_id = input_request['userId']
        theme = input_request['theme']
        self.logger.debug('input message: {}'.format(message))

        user_data = get_data(user_id, self.root_path)
        last_document = None
        last_node = None
        if user_data is not None:
            last_document = user_data['document']
            last_node = user_data['node']
        self.logger.debug('last document: {}, last node: {}'.format(last_document, last_node))

        document, response_node = self.find_reply(
            message=message,
            last_document=last_document,
            last_node=last_node
        )
        self.logger.debug('response document: {}, response node: {}'.format(document, response_node))
        response = self.documents[document][response_node]['sentence']
        self.logger.debug('answer sentence: {}'.format(response))
        lang_tool_answer, textgears_response = self.get_errors(message)
        set_data({user_id: {'document': document, 'node': response_node}}, self.root_path)

        return {'message': response, 'textgears_response_errors': textgears_response.json(), 'language_tool_errors': lang_tool_answer}

    def find_reply(self, message, last_document, last_node):
        distance, document, similar_node = find_similar_sentence(
            input_sentence=message,
            tf_vect=self.tf_vect,
            documents=self.documents,
            theme=last_document,
            sentence_id=last_node
        )
        response_node = None
        if document is None:
            if (last_document is not None) and (last_node is not None) and (
                    len(self.documents[last_document][last_node]['nodes']) > 0):
                response_node = choose_answer(
                    documents=self.documents,
                    document=last_document,
                    node=self.documents[last_document][last_node]['nodes'][0]
                )
                document = last_document
        else:
            self.logger.debug('similar sentence: {}, distance: {}, document: {}'.
                              format(self.documents[document][similar_node]['sentence'], distance, document))
            response_node = choose_answer(
                documents=self.documents,
                document=document,
                node=similar_node
            )

        if response_node is None:
            self.logger.debug('choose random theme')
            files = ['Sports', 'Movie', 'Family', 'Theatre']
            x = random.randint(0, 3)
            document = files[x]
            response_node = 1
        return document, response_node

    @staticmethod
    def get_errors(message):
        url = "https://languagetool.org/api/v2/check"
        payload = "text=" + message + "&language=en-US&enabledOnly=false"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'accept': "application/json",
            'cache-control': "no-cache",
            'postman-token': "5c738aa3-20d4-263f-dbca-d3d747e36ec9"
        }
        lang_tool_response = requests.request("POST", url, data=payload, headers=headers)
        lang_tool_answer = json.loads(lang_tool_response.text)

        textgears_response = requests.get('https://api.textgears.com/check.php',
                                          params={'text': message, 'key': 'PhdFWWMyoGkzCp8q'})

        return lang_tool_answer, textgears_response
