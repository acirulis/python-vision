from flask import Flask
import cv2
import sys
import pip

app = Flask(__name__)


@app.route('/')
def hello_world():
    s = ''
    for dist in pip.get_installed_distributions():
        s = s + '<br />' + dist.project_name
    return 'Lets start developing flaskapp...<br>' + sys.version + '<br />' + s


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
