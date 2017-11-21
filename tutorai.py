from flask import Flask, jsonify, request
from bot.bot import Bot

app = Flask(__name__)
bot = Bot(app.root_path)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/get_sentence', methods=["POST"])
def main():
    input_data = request.get_json(request.data)

    return jsonify({'input': bot.get_sentence(input_data['message'])})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
