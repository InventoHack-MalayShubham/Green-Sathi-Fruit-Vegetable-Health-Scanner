import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from models import db, User, ScanHistory
from werkzeug.utils import secure_filename
from services.gemini_service import GeminiHealthAnalyzer
from services.usda_service import USDAClient
from services.deepseek_service import DeepSeekRecommender
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import markdown


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Add custom filters
@app.template_filter('markdown')
def markdown_filter(text):
    if not text:
        return ''
    return markdown.markdown(text, extensions=['extra', 'nl2br'])

@app.template_filter('replace')
def replace_filter(value, old, new):
    if not value:
        return ''
    return value.replace(old, new)

@app.template_filter('format_nutrition')
def format_nutrition(value):
    if not value:
        return "No nutrition data available"
    try:
        if isinstance(value, str):
            nutrition_data = json.loads(value)
        else:
            nutrition_data = value
        
        formatted = []
        for key, value in nutrition_data.items():
            # Replace underscores with spaces and capitalize each word
            formatted_key = ' '.join(word.capitalize() for word in key.split('_'))
            # Format the value with appropriate units
            if key in ['calories', 'protein', 'carbs', 'fiber', 'sugars', 'fat']:
                formatted_value = f"{value}g"
            elif key in ['vitamin_c', 'iron', 'calcium', 'potassium']:
                formatted_value = f"{value}mg"
            else:
                formatted_value = str(value)
            formatted.append(f'<div class="nutrition-item"><span class="nutrition-key">{formatted_key}</span><span class="nutrition-value">{formatted_value}</span></div>')
        return '\n'.join(formatted)
    except (json.JSONDecodeError, AttributeError):
        return "Invalid nutrition data format"

@app.template_filter('json_decode')
def json_decode(value):
    """Safely decode JSON data."""
    if not value:
        return None
    
    if isinstance(value, dict):
        return value
        
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            try:
                # Try to clean the string if it's double-encoded
                cleaned = value.strip('"\'')
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return None
    return None

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
# @login_required
def home():
    return render_template('home.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@app.route('/scan', methods=['GET', 'POST'])
# @login_required
def scan():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("Please log in to analyze images.")
            return redirect(url_for('login'))
        file = request.files.get('image')
        if not file or file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('Allowed file types: png, jpg, jpeg')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Create result object early with default values
        result = type('Result', (), {
            'image_filename': filename,
            'date': datetime.now(),
            'fruit_name': '',
            'status': '',
            # 'nutrition': {},
            'synergic_fruits': '',
            'analysis': ''
        })()
        
        try:
            # Analyze with Gemini
            gemini = GeminiHealthAnalyzer()
            analysis = gemini.analyze_image(filepath)
            result.fruit_name = analysis.get('item', '') if analysis and 'item' in analysis else ''
            result.status = analysis.get('status', '') if analysis else ''
            
            # Nutrition with USDA
            usda = USDAClient()
            nutrition = usda.get_nutrition(result.fruit_name)
            result.nutrition = nutrition if nutrition else {}
            
            # DeepSeek recommendations
            user_data = {
                'weight': current_user.weight,
                'height': current_user.height,
                'diet_plan': current_user.diet_goal,
                'diet_type': current_user.diet_type,
                'age': current_user.age,
                'region': request.form.get('region', 'India'),
                'allergies': current_user.allergies,
                'activity_level': current_user.activity_level,
                'gender': current_user.gender,
                'current_fruit': result.fruit_name
            }
            deepseek = DeepSeekRecommender()
            synergic_fruits = deepseek.generate_recommendations(user_data)
            result.synergic_fruits = synergic_fruits
            
            # Format the analysis
            result.analysis = f"**{result.fruit_name}**\n\n"
            result.analysis += f"Date: {result.date.strftime('%Y-%m-%d %H:%M')}\n\n"
            result.analysis += f"Status: {result.status}\n\n"
            
            # Save to DB
            scan = ScanHistory(
                user_id=current_user.id,
                image_filename=filename,
                fruit_name=result.fruit_name,
                health_status=result.status,
                nutrition=json.dumps(result.nutrition),
                synergic_fruits=result.synergic_fruits
            )
            db.session.add(scan)
            db.session.commit()
            
        except Exception as e:
            print(f"Error processing scan: {str(e)}")
            flash('Error processing the scan. Please try again.')
            return redirect(request.url)
            
        return render_template('scan.html', result=result)
        
    return render_template('scan.html', result=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        height = request.form['height']
        weight = request.form['weight']
        age = request.form['age']
        diet_goal = request.form['diet_goal']
        diet_type = request.form['diet_type']
        gender = request.form['gender']
        activity_level = request.form['activity_level']
        allergies = request.form['allergies']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        user = User(
            username=username,
            password=generate_password_hash(password),
            height=height,
            weight=weight,
            age=age,
            diet_goal=diet_goal,
            diet_type=diet_type,
            gender=gender,
            activity_level=activity_level,
            allergies=allergies
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    if request.method == 'POST':
        user.height = request.form['height']
        user.weight = request.form['weight']
        user.age = request.form['age']
        user.diet_goal = request.form['diet_goal']
        user.diet_type = request.form['diet_type']
        user.gender = request.form['gender']
        user.activity_level = request.form['activity_level']
        user.allergies = request.form['allergies']
        db.session.commit()
        flash('Profile updated!')
    return render_template('profile.html', user=user)

@app.route('/history', methods=['GET'])
@login_required
def history():
    scans = ScanHistory.query.filter_by(user_id=current_user.id).order_by(ScanHistory.date.desc()).all()
    return render_template('history.html', scans=scans)

@app.route('/history/delete/<int:scan_id>', methods=['POST'])
@login_required
def delete_scan(scan_id):
    scan = ScanHistory.query.filter_by(id=scan_id, user_id=current_user.id).first()
    if scan:
        db.session.delete(scan)
        db.session.commit()
        flash('Scan deleted.')
    return redirect(url_for('history'))

@app.route('/about')
def about():
    return render_template('about.html')

# TODO: Register blueprints for auth, scan, history, profile, about

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=5000,debug=True) 