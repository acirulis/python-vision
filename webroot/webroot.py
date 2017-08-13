from flask import Flask
import cv2


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Lets start developing flaskapp...'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
