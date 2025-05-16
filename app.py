from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to something secure

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store 100 slots in a list (indexed 0–99)
slots = [None] * 100

# --- Helper function to check allowed file extensions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Homepage ---
@app.route('/')
def index():
    return render_template('index.html', slots=slots)

# --- Admin login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == '1234':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            flash('Wrong password')
    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# --- Admin dashboard ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        slot_number = int(request.form['slot_number']) - 1  # Make it 0-indexed
        file = request.files['brand_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            slots[slot_number] = filename
            flash('Brand image uploaded successfully.')

    return render_template('admin.html', slots=slots)

# --- Remove image from a slot ---
@app.route('/remove/<int:slot>')
def remove(slot):
    if not session.get('admin'):
        return redirect(url_for('login'))
    slot = slot - 1  # Make it 0-indexed
    slots[slot] = None
    flash(f'Slot #{slot+1} cleared.')
    return redirect(url_for('admin'))

# --- Serve uploaded files ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Run the app ---
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

