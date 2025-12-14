from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_mock_plan():
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
