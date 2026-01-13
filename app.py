import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import database
import openai_generator
from datetime import datetime
import threading

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

def process_image_generation(filepath, filename, breed, user_id, timestamp, image_id):
    """Background function to generate transformation images"""
    try:
        print(f"Background: Starting image generation for {filename}")
        
        # Generate transformation images using DALL-E 3
        print("Background: Starting image generation with DALL-E 3...")
        trans1_path, final_path, full_dog_path = openai_generator.generate_transformation_images(
            filepath, breed, user_id, timestamp
        )
        
        print(f"Background: Generated images - Trans1: {trans1_path}, Final: {final_path}, Full Dog: {full_dog_path}")
        
        # Check if files actually exist
        trans1_exists = trans1_path and os.path.exists(trans1_path)
        final_exists = final_path and os.path.exists(final_path)
        full_dog_exists = full_dog_path and os.path.exists(full_dog_path)
        
        print(f"Background: Files exist - Trans1: {trans1_exists}, Final: {final_exists}, Full Dog: {full_dog_exists}")
        
        # Update database with generated images
        if trans1_exists and final_exists and full_dog_exists:
            # Update the database record with the generated images
            database.update_image_set(
                image_id,
                os.path.basename(trans1_path),
                os.path.basename(final_path),
                os.path.basename(full_dog_path)
            )
            print(f"Background: Successfully updated database for image_id {image_id}")
        else:
            print(f"Background: WARNING - Not all images generated. Trans1: {trans1_exists}, Final: {final_exists}, Full Dog: {full_dog_exists}")
    except Exception as e:
        print(f"Background: Error processing image generation: {e}")
        import traceback
        traceback.print_exc()

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
        
        # Analyze breed using OpenAI GPT-4 Vision (quick operation)
        print(f"Analyzing breed for image: {filepath}")
        breed = openai_generator.analyze_dog_breed(filepath)
        print(f"Detected breed: {breed}")
        
        # Save initial record to database (without transformation images yet)
        image_id = database.save_image_set(
            current_user.id,
            filename,
            breed,
            None,  # transition1 - will be updated later
            None,  # final - will be updated later
            None   # full_dog - will be updated later
        )
        
        # Start background thread for image generation
        thread = threading.Thread(
            target=process_image_generation,
            args=(filepath, filename, breed, current_user.id, timestamp, image_id),
            daemon=True
        )
        thread.start()
        
        # Return immediately with original image and processing status
        return jsonify({
            'success': True,
            'image_id': image_id,
            'breed': breed,
            'status': 'processing',
            'images': {
                'original': url_for('serve_image', filename=filename),
                'transition1': None,
                'final': None,
                'full_dog': None
            },
            'message': 'Image uploaded successfully. Transformations are being generated in the background.'
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

@app.route('/check-status/<int:image_id>')
@login_required
def check_status(image_id):
    """Check if images are ready for a given image_id"""
    try:
        image_data = database.get_image_by_id(image_id)
        if not image_data or image_data['user_id'] != current_user.id:
            return jsonify({'error': 'Image not found'}), 404
        
        # Check if all images are ready
        trans1_exists = image_data.get('transition1_image') and os.path.exists(
            os.path.join(app.config['UPLOAD_FOLDER'], image_data['transition1_image'])
        )
        final_exists = image_data.get('final_dog_image') and os.path.exists(
            os.path.join(app.config['UPLOAD_FOLDER'], image_data['final_dog_image'])
        )
        full_dog_exists = image_data.get('transition2_image') and os.path.exists(
            os.path.join(app.config['UPLOAD_FOLDER'], image_data['transition2_image'])
        )
        original_exists = image_data.get('original_image') and os.path.exists(
            os.path.join(app.config['UPLOAD_FOLDER'], image_data['original_image'])
        )
        
        all_ready = original_exists and trans1_exists and final_exists and full_dog_exists
        
        if all_ready:
            return jsonify({
                'success': True,
                'status': 'complete',
                'images': {
                    'original': url_for('serve_image', filename=image_data['original_image']),
                    'transition1': url_for('serve_image', filename=image_data['transition1_image']),
                    'final': url_for('serve_image', filename=image_data['final_dog_image']),
                    'full_dog': url_for('serve_image', filename=image_data['transition2_image'])
                }
            })
        else:
            return jsonify({
                'success': True,
                'status': 'processing',
                'message': 'Images are still being generated...'
            })
    except Exception as e:
        print(f"Error checking status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve images from uploads directory"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
