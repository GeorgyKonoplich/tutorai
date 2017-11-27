from flask import Flask, jsonify, request
from bot.bot import Bot
#import graphitesend

app = Flask(__name__)
bot = Bot(app.root_path)
#g = graphitesend.init(graphite_port=3031,graphite_server='127.0.0.1')


@app.route('/init')
def hello_world():
    return 'Hello World!'


@app.route('/get_sentence/', methods=["POST"])
def main():
    input_data = request.get_json(request.data)
    answer = bot.get_sentence(input_data['message'])
    answer['userMsgId'] = input_data['userMsgId']
    answer['connectionId'] = input_data['connectionId']
    return jsonify(answer)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
