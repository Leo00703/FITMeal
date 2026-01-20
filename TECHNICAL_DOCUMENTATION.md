# FITMeal - Technical Documentation

## Project Overview
FITMeal is a web-based application designed to generate personalized weekly meal plans using Artificial Intelligence. Built with Python and Flask, it allows users to create accounts, specify their dietary preferences and fitness goals, and receive a fully customized 7-day meal plan complete with recipes, macros, and ingredients.

## Architecture
The project follows a standard Model-View-Controller (MVC) pattern adapted for Flask:
- **Model**: SQLite database managed via `database.py`.
- **View**: HTML templates in `templates/` rendered with Jinja2, styled with CSS in `static/`.
- **Controller**: Route handlers in `app.py`.

## File Structure & Purpose

### Core Application Files

#### `app.py`
The entry point of the application.
- **Responsibilities**:
  - Initializes the Flask app and database.
  - Defines all web routes (`/`, `/login`, `/register`, `/planner`, etc.).
  - Manages user sessions (login/logout logic).
  - Handles form submissions and calls the AI service.
  - Injects context (like `has_plan`) into templates.
- **Key Routes**:
  - `/generate_plan`: Processes user input from the planner form and triggers AI generation.
  - `/plan`: Displays the generated meal plan.

#### `database.py`
Handles all interactions with the SQLite database (`fitmeal.db`).
- **Responsibilities**:
  - `init_db()`: Creates necessary tables (`users`, `plans`, `user_profiles`, `favorites`).
  - `create_user()` / `verify_user()`: Manages user authentication.
  - `save_plan()` / `get_plan()` / `update_plan_status()`: Stores and retrieves the JSON-formatted meal plans with status.
  - `update_user_profile()` / `get_user_profile()`: Stores and retrieves physical attributes, goals, and profile meta.
  - `add_favorite()` / `get_favorites()` / `remove_favorite()`: CRUD for user favorites.
- **Schema**:
  - **users**: id, username (unique), password (hashed).
  - **plans**: user_id (PK), plan_data (JSON), status (draft/saved).
  - **user_profiles**: user_id (PK), weight, height, sex, age, goal, activity_level, bio, profile_pic.
  - **favorites**: (user_id, recipe_id) PK, recipe_name.

#### `ai_service.py`
The interface for the AI generation logic.
- **Responsibilities**:
  - Connects to the Groq API using the `groq` python client.
  - Constructs a detailed prompt based on user inputs (goal, diet, allergies, etc.).
  - Enforces a strict JSON response format for the AI model (`openai/gpt-oss-120b`).
  - **Fallback**: If the API key is missing or the request fails, it falls back to `get_mock_plan()` to ensure the app remains functional.

#### `utils.py`
Contains helper functions.
- **Responsibilities**:
  - `login_required`: A decorator used in `app.py` to protect routes that require authentication.
  - `get_mock_plan()`: Returns a static, hardcoded weekly meal plan for testing or fallback purposes.

### Frontend

#### `templates/`
Contains HTML files using Jinja2 templating syntax.
- `base.html`: The master template containing the `<head>`, navigation bar, and footer. All other pages extend this.
- `planner_form.html`: The form where users input their dietary requirements.
- `plan.html`: The view that renders the complex JSON meal plan data into a user-friendly schedule.
- `profile.html`: Profile, stats, favorites, plan summary, and a dynamically generated QR code for mobile testing on the same network.

#### `static/`
- `styles.css`: Global styles for the application.
- `scripts.js`: Client-side logic (e.g., dynamic interactions on the plan page).

## Logic Flow

1.  **Authentication**:
    - A user registers or logs in.
    - `app.py` verifies credentials against `database.py`.
    - A session is created with the `user_id`.

2.  **Plan Request**:
    - The user navigates to `/planner` (protected by `@login_required`).
    - They fill out a form with: Goal, Diet, Allergies, Meals per day, Creativity, and Cuisine.

3.  **AI Generation**:
    - The form submits POST data to `/generate_plan`.
    - `app.py` extracts this data and calls `ai_service.generate_weekly_plan(profile)`.
    - `ai_service.py` sends a prompt to the Groq API.
    - The AI returns a structured JSON object containing a 7-day plan with meals, recipes, and macros.

4.  **Data Persistence**:
  - The JSON response is serialized and saved to the `plans` table in SQLite via `database.save_plan` (status defaults to `draft`, can be updated to `saved`).

5.  **Presentation**:
  - The user is redirected to `/plan`.
  - `app.py` fetches the plan from the database.
  - `plan.html` iterates through the JSON data to display the weekly schedule.
  - The profile page shows stats, favorites, and a QR code that encodes `http://<local_ip>:5000` for mobile access on the same WiFi.

## Technical Requirements
- **Python 3.x**
- **Flask**: Web framework.
- **SQLite3**: Database (standard library).
- **Groq**: Client library for AI model access.
- **python-dotenv**: For managing environment variables (API keys).
- **qrcode[pil]**, **Pillow**: Generate base64-encoded QR codes for mobile testing links.

## Environment Variables
The application relies on a `.env` file for configuration:
- `GROQ_API_KEY`: Required for the AI service to function (otherwise uses mock data).
- `SECRET_KEY`: Used by Flask to sign session cookies.
