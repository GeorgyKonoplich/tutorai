import logging

from flask import Flask, jsonify, request
from flask_cors import CORS
from bot.bot import Bot
from common.log import configure_loggers_with_file

app = Flask(__name__)
CORS(app)
configure_loggers_with_file(app.root_path)
logger = logging.getLogger('tutor')
bot = Bot(app.root_path)


@app.route('/get_sentence/', methods=["POST"])
def reply():
    input_data = request.get_json(request.data)
    logger.debug('Request received: {}'.format(input_data))
    answer = bot.get_sentence(input_data)
    logger.debug('Response is formed: {}'.format(answer))
    return jsonify(answer)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
