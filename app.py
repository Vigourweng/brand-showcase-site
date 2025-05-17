from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '1234'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'HEAD'])
def index():
    try:
        image_files = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
        image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        slots = image_files + [None] * (100 - len(image_files))
        return render_template('index.html', slots=slots)
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == '1234':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return 'Wrong password'
    return '''
        <form method="post">
            Password: <input type="password" name="password">
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('admin'))
    image_files = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
    image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return '''
        <h1>Upload Brand Image</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="image">
            <input type="submit" value="Upload">
        </form>
        <p><a href="/">Back to Home</a></p>
        <p>Current Images:</p>
        <ul>{}</ul>
    '''.format(''.join(f'<li>{f}</li>' for f in image_files))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
