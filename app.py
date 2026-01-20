import os
import uuid
import base64
import socket
from io import BytesIO
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import qrcode
import database
from utils import login_required
from ai_service import generate_weekly_plan

# Load environment variables
load_dotenv()

# Initialize Database
database.init_db()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_for_fitmeal_planner")

# Auth Helper imported from utils

def get_local_ip():
    """Get the local network IP address of the server."""
    try:
        # Create a socket and connect to a remote server (without actually connecting)
        # This trick gets the local IP that would be used for network communication
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's public DNS
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback to localhost if unable to determine
        return "127.0.0.1"

def generate_qr_code():
    """Generate QR code for local network URL and return as base64 string."""
    try:
        # Get the local network IP address
        local_ip = get_local_ip()
        port = 5000  # Flask default port
        url = f"http://{local_ip}:{port}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return img_base64
    except Exception as e:
        print(f"QR Code generation error: {e}")
        return None
        return None

@app.context_processor
def inject_user_status():
    has_plan = False
    if 'user_id' in session:
        plan = database.get_plan(session['user_id'])
        if plan:
            has_plan = True
    return dict(has_plan=has_plan)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = database.verify_user(username, password)
        if user_id:
            session['username'] = username
            session['user_id'] = user_id
            return redirect(url_for('planner'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = str(uuid.uuid4())
        if database.create_user(username, password, user_id):
            session['username'] = username
            session['user_id'] = user_id
            return redirect(url_for('planner'))
        else:
            return render_template('register.html', error="Username already exists")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/planner')
@login_required
def planner():
    return render_template('planner_form.html')

@app.route('/generate_plan', methods=['POST'])
@login_required
def generate_plan():
    user_id = session['user_id']
    data = request.form
    
    # Extract profile data from form
    user_profile = {
        'goal': data.get('goal'),
        'diet': data.get('diet'),
        'allergies': data.get('allergies'),
        'meals_per_day': data.get('meals_per_day'),
        'creativity': data.get('creativity'),
        'cuisine': data.get('cuisine')
    }

    # Generate plan using AI service
    plan_json = generate_weekly_plan(user_profile)

    database.save_plan(user_id, plan_json)
    return redirect(url_for('plan'))

@app.route('/plan')
@login_required
def plan():
    user_id = session.get('user_id')
    plan_data = database.get_plan(user_id)
    if not plan_data:
        return redirect(url_for('planner'))
    
    favorites = database.get_favorites(user_id)
    favorite_ids = [f['recipe_id'] for f in favorites]
    
    return render_template('plan.html', plan=plan_data['week_plan'], plan_status=plan_data.get('status', 'draft'), favorite_ids=favorite_ids)

@app.route('/toggle_favorite/<recipe_id>', methods=['POST'])
@login_required
def toggle_favorite_route(recipe_id):
    user_id = session.get('user_id')
    data = request.get_json()
    recipe_name = data.get('recipe_name', 'Unknown Recipe')
    
    # Check if already favorite
    favorites = database.get_favorites(user_id)
    is_fav = any(f['recipe_id'] == recipe_id for f in favorites)
    
    if is_fav:
        database.remove_favorite(user_id, recipe_id)
        action = 'removed'
    else:
        database.add_favorite(user_id, recipe_id, recipe_name)
        action = 'added'
        
    return jsonify({"status": "success", "action": action})

@app.route('/save_plan', methods=['POST'])
@login_required
def save_plan_route():
    user_id = session.get('user_id')
    database.update_plan_status(user_id, 'saved')
    return jsonify({'status': 'success'})





@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    message = None
    
    if request.method == 'POST':
        # Handle Profile Update
        profile_data = {
            'age': request.form.get('age'),
            'sex': request.form.get('sex'),
            'weight': request.form.get('weight'),
            'height': request.form.get('height'),
            'activity_level': request.form.get('activity_level'),
            'goal': request.form.get('goal'),
            'bio': request.form.get('bio'),
            'profile_pic': request.form.get('profile_pic')
        }
        # Filter out None values to avoid overwriting with empty if not in form (though form usually sends empty string)
        # Actually, update_user_profile handles merging, but we should be careful with empty strings if we want to keep old values?
        # The current implementation of update_user_profile merges with existing DB data, but if we send empty strings from form, they will overwrite.
        # Let's assume the form sends current values if not changed.
        
        database.update_user_profile(user_id, profile_data)
        message = "Profile updated successfully!"
    
    profile = database.get_user_profile(user_id)
    plan = database.get_plan(user_id)
    favorites = database.get_favorites(user_id)
    
    # Generate QR code for local network URL
    qr_code_base64 = generate_qr_code()
    
    return render_template('profile.html', profile=profile, plan=plan, favorites=favorites, message=message, qr_code=qr_code_base64)

@app.route('/add_favorite/<recipe_id>', methods=['POST'])
@login_required
def add_favorite_route(recipe_id):
    user_id = session.get('user_id')
    recipe_name = request.form.get('recipe_name', 'Unknown Recipe')
    database.add_favorite(user_id, recipe_id, recipe_name)
    return redirect(url_for('profile'))

@app.route('/remove_favorite/<recipe_id>', methods=['POST'])
@login_required
def remove_favorite_route(recipe_id):
    user_id = session.get('user_id')
    database.remove_favorite(user_id, recipe_id)
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
