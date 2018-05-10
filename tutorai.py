from flask import Flask, jsonify, request, render_template
from bot.bot import Bot
import logging
from common.log import configure_loggers_with_file
import aiml
import os
from google.cloud import translate

app = Flask(__name__)
configure_loggers_with_file(app.root_path)
logger = logging.getLogger('tutor')
bot = Bot(app.root_path)


@app.route('/')
def hello():
    #logger.debug('init')
    return render_template('chat.html')

@app.route("/ask", methods=['POST'])
def ask():
    message = str(request.form['messageText'])

    kernel = aiml.Kernel()

    if os.path.isfile("bot_brain.brn"):
        kernel.bootstrap(brainFile = "bot_brain.brn")
    else:
        kernel.bootstrap(learnFiles = os.path.abspath("aiml/std-startup.xml"), commands = "load aiml b")
        kernel.saveBrain("bot_brain.brn")

    # kernel now ready for use
    while True:
        if message == "quit":
            exit()
        elif message == "save":
            kernel.saveBrain("bot_brain.brn")
        else:
            bot_response = kernel.respond(message)
            # print bot_response
            return jsonify({'status':'OK','answer':bot_response})


@app.route('/get_sentence/', methods=["POST"])
def main():
    input_data = request.get_json(request.data)
    logger.debug('Request received: {}'.format(input_data))
    answer = bot.get_sentence(input_data)
    answer['userMsgId'] = input_data['userMsgId']
    answer['connectionId'] = input_data['connectionId']
    logger.debug('Response is formed: {}'.format(answer))
    return jsonify(answer)

def main1():
    input_data = request.get_json(request.data)
    logger.debug('Request received: {}'.format(input_data))
    answer = bot.get_sentence1(input_data)
    kernel = aiml.Kernel()
    if os.path.isfile("bot_brain.brn"):
        kernel.bootstrap(brainFile = "bot_brain.brn")
    else:
        kernel.bootstrap(learnFiles = os.path.abspath("aiml/std-startup.xml"), commands = "load aiml b")
        kernel.saveBrain("bot_brain.brn")
    print(answer['message'])
    message = answer['message']
    while True:
        if message == "quit":
            exit()
        elif message == "save":
            kernel.saveBrain("bot_brain.brn")
        else:
            bot_response = kernel.respond(message)
    	    answer['message'] = bot_response
            answer['userMsgId'] = input_data['userMsgId']
            answer['connectionId'] = input_data['connectionId']
            logger.debug('Response is formed: {}'.format(answer))
            return jsonify(answer)


@app.route('/translate_word/', methods=["POST"])
def translate_word():
    input_data = request.get_json(request.data)
    translate_client = translate.Client.from_service_account_json(app.root_path + '/static/try-apis-23e63e8677c1.json')
    target = 'ru'
    word = input_data['word']
    translation = translate_client.translate(
        word,
        target_language=target)

    return jsonify({'translate': translation['translatedText'].encode('utf-8')})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
