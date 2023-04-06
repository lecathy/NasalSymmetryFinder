import os
from flask import Flask, send_file, render_template, request, abort
from nasal_sym import DorsumSymmetryFinder

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.stl', '.obj']

@app.route('/')
def home():
    return f'Nasal Symmetry Finder'


@app.route('/test')
def test():
    d = DorsumSymmetryFinder(image_path='head3d_Zach.stl', avg_path='avg_head.stl')
    d.run(color='grey')
    return send_file('plots\\birds-eye.png', mimetype='image/png')


@app.route('/upload')
def upload_file_screen():
   return render_template('upload.html')


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        f = request.files['file']
        filename = f.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
        f.save('current.stl')
        d = DorsumSymmetryFinder(image_path='current.stl', avg_path='avg_head.stl')
        d.run(color='grey')

        return render_images()
        

def return_img_stream(img_local_path):
    import base64
    img_stream = ''
    with open(img_local_path, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream).decode()
    return img_stream


def render_images():
    img_paths = ['plots\\birds-eye.png',
              'plots\\centre.png',
              'plots\\L-45.png',
              'plots\\L-90.png',
              'plots\\R-45.png',
              'plots\\R-90.png',
              'plots\\worms-eye.png'
            ]
    imgs = []
    for img_path in img_paths:
        imgs.append(return_img_stream(img_path))

    return render_template('images.html', imgs=imgs)