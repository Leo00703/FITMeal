# FITMeal Planner

FITMeal Planner is an intelligent, AI-powered web application designed to help users generate personalized weekly meal plans. By leveraging the power of Large Language Models (LLMs) via the Groq API, FITMeal creates tailored nutrition plans based on individual goals, dietary restrictions, and culinary preferences.

## 🚀 Features

- **AI-Powered Meal Generation**: Generates complete 7-day meal plans based on user inputs.
- **Personalized Preferences**: Supports customization for:
  - Fitness Goals (e.g., Weight Loss, Muscle Gain)
  - Dietary Types (e.g., Vegan, Keto, Paleo)
  - Allergies & Exclusions
  - Cuisine Preferences
  - Meals per day
- **Interactive Planner UI**:
  - Modern "Glassmorphism" design with an Orange/Food-themed aesthetic.
  - Carousel view for navigating through the week's meals.
  - Detailed recipe modals with ingredients, instructions, and macro-nutrient breakdowns.
- **User Accounts**: Secure login and registration system.
- **Plan Management**:
  - Save generated plans.
  - "Regenerate" option to get a fresh plan.
- **Favorites System**: Save individual recipes to your profile for quick access.
- **Profile Management**: Update personal stats (Age, Weight, Height, Activity Level).

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3 (Custom Glassmorphism), JavaScript (Vanilla)
- **AI Integration**: Groq API (using `openai/gpt-oss-120b` or similar models)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FITMeal
   ```

2. **Create a Virtual Environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

5. **Initialize Database**
   The application automatically initializes the SQLite database (`fitmeal.db`) on the first run.

## 🏃‍♂️ Usage

1. **Run the Application**
   ```bash
   python app.py
   ```

2. **Access the App**
   Open your browser and navigate to `http://127.0.0.1:5000`.

3. **Get Started**
   - Register for a new account.
   - Navigate to the Planner.
   - Fill in your preferences and click "Generate Plan".
   - View your personalized weekly meal plan!

## 📂 Project Structure

```
FITMeal/
├── app.py              # Main Flask application entry point
├── ai_service.py       # AI integration logic (Groq API)
├── database.py         # Database connection and helper functions
├── utils.py            # Helper functions and mock data
├── requirements.txt    # Python dependencies
├── static/
│   └── styles.css      # Global styles and themes
├── templates/          # HTML Templates (Jinja2)
│   ├── base.html       # Base layout
│   ├── index.html      # Landing page
│   ├── plan.html       # Weekly planner view
│   ├── planner_form.html # Preferences form
│   ├── profile.html    # User profile and favorites
│   └── ...
└── fitmeal.db          # SQLite Database (generated)
```

## 📄 License

This project is for educational purposes.
