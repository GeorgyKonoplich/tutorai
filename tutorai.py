from flask import Flask, jsonify, request
from bot.bot import Bot
import logging
from common.log import configure_loggers_with_file
#import graphitesend

app = Flask(__name__)
bot = Bot(app.root_path)
configure_loggers_with_file(app.root_path)
logger = logging.getLogger('tutor')
#g = graphitesend.init(graphite_port=3031,graphite_server='127.0.0.1')


@app.route('/init')
def hello_world():
    logger.debug('init')
    return 'Hello World!'


@app.route('/get_sentence/', methods=["POST"])
def main():
    input_data = request.get_json(request.data)
    logger.debug('Request received: {}'.format(input_data))
    answer = bot.get_sentence(input_data['message'])
    answer['userMsgId'] = input_data['userMsgId']
    answer['connectionId'] = input_data['connectionId']
    logger.debug('Response is formed: {}'.format(answer))
    return jsonify(answer)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
