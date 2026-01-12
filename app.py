import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import database
import image_generator
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_data = database.get_user_by_id(user_id)
    if user_data:
        return User(user_data['id'], user_data['username'])
    return None

# Initialize database on startup
with app.app_context():
    database.init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        
        user_id = database.create_user(username, password)
        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        user_data = database.verify_user(username, password)
        if user_data:
            user = User(user_data['id'], user_data['username'])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_images = database.get_user_images(current_user.id)
    return render_template('dashboard.html', images=user_images, username=current_user.username)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload JPG, PNG, or GIF'}), 400
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{current_user.id}_{timestamp}_original.{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save original image
        file.save(filepath)
        
        # Analyze breed (simplified - in production use proper vision model)
        print(f"Analyzing breed for image: {filepath}")
        breed = image_generator.analyze_dog_breed(filepath)
        print(f"Detected breed: {breed}")
        
        # Generate transformation images
        print("Starting image generation...")
        trans1_path, trans2_path, final_path = image_generator.generate_transformation_images(
            filepath, breed, current_user.id, timestamp
        )
        
        print(f"Generated images - Trans1: {trans1_path}, Trans2: {trans2_path}, Final: {final_path}")
        
        # Check if files actually exist
        trans1_exists = trans1_path and os.path.exists(trans1_path)
        trans2_exists = trans2_path and os.path.exists(trans2_path)
        final_exists = final_path and os.path.exists(final_path)
        
        print(f"Files exist - Trans1: {trans1_exists}, Trans2: {trans2_exists}, Final: {final_exists}")
        
        # Save to database
        image_id = database.save_image_set(
            current_user.id,
            filename,
            breed,
            os.path.basename(trans1_path) if trans1_exists else None,
            os.path.basename(trans2_path) if trans2_exists else None,
            os.path.basename(final_path) if final_exists else None
        )
        
        # Return JSON response with image URLs
        return jsonify({
            'success': True,
            'image_id': image_id,
            'breed': breed,
            'images': {
                'original': url_for('serve_image', filename=filename),
                'transition1': url_for('serve_image', filename=os.path.basename(trans1_path)) if trans1_exists else None,
                'transition2': url_for('serve_image', filename=os.path.basename(trans2_path)) if trans2_exists else None,
                'final': url_for('serve_image', filename=os.path.basename(final_path)) if final_exists else None
            }
        })
    
    except Exception as e:
        print(f"Error processing upload: {e}")
        import traceback
        traceback.print_exc()
        # Always return valid JSON, even on error
        return jsonify({
            'success': False,
            'error': f'Error processing image: {str(e)}'
        }), 500

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve images from uploads directory"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
