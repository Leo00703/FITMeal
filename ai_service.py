import os
import json
from groq import Groq
from utils import get_mock_plan

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
groq_client = None
if api_key:
    groq_client = Groq(api_key=api_key)

MODEL_ID = "openai/gpt-oss-120b"

def generate_weekly_plan(user_profile):
    """
    Generates a weekly meal plan based on user profile using Groq API.
    Falls back to mock plan if API fails or is not configured.
    """
    if not groq_client:
        return get_mock_plan()

    goal = user_profile.get('goal')
    diet = user_profile.get('diet')
    allergies = user_profile.get('allergies')
    meals = user_profile.get('meals_per_day')
    creativity = user_profile.get('creativity')
    cuisine = user_profile.get('cuisine')

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

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a nutritionist AI. Output only JSON."},
                {"role": "user", "content": prompt}
            ],
            model=MODEL_ID,
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"AI Error: {e}")
        return get_mock_plan()
