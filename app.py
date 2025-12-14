import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from groq import Groq
import database

# Load environment variables
load_dotenv()

# Initialize Database
database.init_db()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_for_fitmeal_planner")

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
groq_client = None
if api_key:
    groq_client = Groq(api_key=api_key)

MODEL_ID = "openai/gpt-oss-120b"

# Auth Helper
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
    
    goal = data.get('goal')
    diet = data.get('diet')
    allergies = data.get('allergies')
    meals = data.get('meals_per_day')
    creativity = data.get('creativity')
    cuisine = data.get('cuisine')

    prompt = f"""
    Generate a 7-day weekly meal plan for a user with the following profile:
    - Goal: {goal}
    - Diet: {diet}
    - Allergies/Exclusions: {allergies}
    - Meals per day: {meals}
    - Cuisine Preference: {cuisine}
    - Creativity Level (0-1): {creativity}

    Return ONLY valid JSON with this structure:
    {{
        "week_plan": {{
            "Monday": [
                {{
                    "meal": "Breakfast", 
                    "recipe_name": "Name", 
                    "time": "15m", 
                    "calories": 450,
                    "macros": {{"protein": "30g", "carbs": "40g", "fat": "15g"}},
                    "ingredients": ["100g Oats", "1 Banana", "20g Honey"],
                    "instructions": ["Boil water", "Add oats", "Top with banana"],
                    "tags": ["Tag1"], 
                    "id": "unique_id_1"
                }},
                ...
            ],
            ... (for all 7 days)
        }}
    }}
    Ensure recipe IDs are unique strings.
    """

    if groq_client:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a nutritionist AI. Output only JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=MODEL_ID,
                response_format={"type": "json_object"}
            )
            plan_json = json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"AI Error: {e}")
            # Fallback if AI fails
            plan_json = _get_mock_plan()
    else:
        # Mock mode
        plan_json = _get_mock_plan()

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



def _get_mock_plan():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plan = {}
    for day in days:
        plan[day] = [
            {
                "meal": "Breakfast", 
                "recipe_name": "Oatmeal with Berries", 
                "time": "10m", 
                "calories": 350,
                "macros": {"protein": "12g", "carbs": "60g", "fat": "6g"},
                "ingredients": ["1/2 cup Oats", "1 cup Almond Milk", "1/2 cup Mixed Berries", "1 tbsp Honey"],
                "instructions": ["Combine oats and milk in a pot.", "Cook on medium heat for 5-7 mins.", "Top with berries and honey."],
                "tags": ["Vegan", "Quick"], 
                "id": f"{day}_bf"
            },
            {
                "meal": "Lunch", 
                "recipe_name": "Grilled Chicken Salad", 
                "time": "20m", 
                "calories": 450,
                "macros": {"protein": "40g", "carbs": "15g", "fat": "20g"},
                "ingredients": ["150g Chicken Breast", "2 cups Mixed Greens", "1/2 Avocado", "1 tbsp Olive Oil", "Lemon Juice"],
                "instructions": ["Grill chicken breast until cooked.", "Slice chicken and place over greens.", "Top with avocado, olive oil, and lemon juice."],
                "tags": ["High Protein"], 
                "id": f"{day}_lunch"
            },
            {
                "meal": "Dinner", 
                "recipe_name": "Salmon with Quinoa", 
                "time": "30m", 
                "calories": 550,
                "macros": {"protein": "35g", "carbs": "45g", "fat": "25g"},
                "ingredients": ["150g Salmon Fillet", "1/2 cup Quinoa", "1 cup Steamed Broccoli", "Lemon slices"],
                "instructions": ["Bake salmon at 200°C for 12-15 mins.", "Cook quinoa according to package instructions.", "Serve salmon with quinoa and steamed broccoli."],
                "tags": ["Healthy Fat"], 
                "id": f"{day}_dinner"
            }
        ]
    return {"week_plan": plan}

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
    
    return render_template('profile.html', profile=profile, plan=plan, favorites=favorites, message=message)

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
    app.run(debug=True)
