from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '1234'

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
REQUESTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'requests')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REQUESTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'HEAD'])
def index():
    try:
        images = sorted([
            f for f in os.listdir(app.config['UPLOAD_FOLDER'])
            if allowed_file(f)
        ])
        slots = images + [None] * (100 - len(images))  # Fill remaining slots
        return render_template('index.html', slots=slots)
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == '1234':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Wrong password")
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('admin'))

    images = sorted([
        f for f in os.listdir(app.config['UPLOAD_FOLDER'])
        if allowed_file(f)
    ])
    return render_template('admin.html', images=images)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/rent_request/<int:slot_index>', methods=['POST'])
def rent_request(slot_index):
    file = request.files.get('image')
    comment = request.form.get('comment')

    if not file or not allowed_file(file.filename):
        return "Invalid file format", 400

    filename = secure_filename(file.filename)

    import time
    timestamp = int(time.time())
    saved_filename = f"slot{slot_index}_{timestamp}_{filename}"

    # Save image to requests folder
    file.save(os.path.join(REQUESTS_FOLDER, saved_filename))

    # Save comment as a .txt file
    comment_file = saved_filename + ".txt"
    with open(os.path.join(REQUESTS_FOLDER, comment_file), "w") as f:
        f.write(comment)

    flash("Your request has been submitted successfully!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
@app.route('/admin/requests')
def view_requests():
    if not session.get('admin'):
        return redirect(url_for('login'))

    requests_data = []
    for filename in os.listdir(REQUESTS_FOLDER):
        if allowed_file(filename):
            comment_file = filename + ".txt"
            comment_path = os.path.join(REQUESTS_FOLDER, comment_file)
            comment = ""
            if os.path.exists(comment_path):
                with open(comment_path, "r") as f:
                    comment = f.read()
            requests_data.append({
                'image': filename,
                'comment': comment
            })

    return render_template('requests.html', requests=requests_data)

