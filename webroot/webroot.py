import os, sys, pip

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Markup
from werkzeug import secure_filename
import subprocess
import cv2
from random import randint

os.chdir(os.path.dirname(__file__))
os.environ['LD_LIBRARY_PATH'] = '/opt/project/darknet'

app = Flask(__name__, static_url_path='/static')

# app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'bmp'])
app.config['OUTPUT_FOLDER'] = 'output/'


def adaptive_resize(filename, max_size=1024):
    img = cv2.imread(filename, 1)
    h, w, _ = img.shape
    ratio1 = float(max_size) / h
    ratio2 = float(max_size) / w
    ratio = min(ratio1, ratio2)
    if ratio >= 1:
        return
    img = cv2.resize(img, (int(ratio * w), int(ratio * h)))
    cv2.imwrite(filename, img)

def draw_object(filename, crd, name = 'Car'):
    img = cv2.imread(filename, 1)
    imh, imw, _ = img.shape
    x = float(crd[0]) # - 120
    y = float(crd[1]) #- 250
    w = float(crd[2])
    h = float(crd[3])
    top_left = (int((x-w/2.)*imw), int((y-h/2.)*imh))
    bottom_right = ( int((x+w/2.)*imw), int((y+h/2.)*imh) )
    img = cv2.rectangle(img, top_left, bottom_right,(0,255,220), 4)

    cv2.imwrite(filename, img)

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           (filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS'] or
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'])

@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        adaptive_resize(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        sys.path.append(os.path.join(os.path.dirname(__file__), 'darknet'))
        import darknet.darknet as dn
        #net = dn.load_net(bytes("darknet/cfg/tiny-yolo.cfg", 'ascii'), bytes("darknet/tiny-yolo.weights", 'ascii'), 0)
        net = dn.load_net(bytes("darknet/cfg/yolo.cfg", 'ascii'), bytes("darknet/yolo.weights", 'ascii'), 0)
        meta = dn.load_meta(bytes("darknet/cfg/coco.data", 'ascii'))
        r = dn.detect(net, meta, bytes(app.config['UPLOAD_FOLDER'] + filename, 'ascii'), thresh=.5)
        res = ''
        for object in r:
            name = object[0].decode('utf-8')
            prob = float(object[1])
            rct  = object[2]
            res += 'Detected <b>' + name + '</b> with probability of ' + str(round(prob,2))
            #res += ' ' + str(rct)
            res += '<br />'
            draw_object(app.config['UPLOAD_FOLDER'] + filename, rct)
        return render_template('result.html', filename='uploads/' + filename + '?' + str(randint(0,999)), result_text=res)
    else:
        return 'invalid data';


@app.route('/sysinfo')
def sysinfo():
    s = ''
    for dist in pip.get_installed_distributions():
        s = s + '<br />' + dist.project_name
    z = os.path.join(os.path.dirname(__file__))
    return '<a href="/">Index</a><br><code>Python version: ' + sys.version + '<br /> Installed packages: ' + s + '<br > ' + z

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
