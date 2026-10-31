# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User
import os
import re
import requests
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

def format_database_url(url: str) -> str:
    """Format and sanitize database URL for SQLAlchemy and Supabase PostgreSQL."""
    if not url:
        return url
    url = url.strip()

    # Pattern to extract credentials, handling bracketed passwords [mypassword] and special chars like '@'
    pattern = r'^(postgresql(?:\+psycopg2)?|postgres)://([^:]+):(?:\[(.*?)\]|(.*?))@([^/@]+(?::\d+)?)(/.*)?$'
    match = re.match(pattern, url)
    if match:
        _, user, bp, np, host, path = match.groups()
        password = bp if bp is not None else (np or '')
        # URL encode password to handle special characters like '@', '#', etc.
        encoded_password = urllib.parse.quote_plus(password)
        clean_path = path or '/postgres'
        return f'postgresql+psycopg2://{user}:{encoded_password}@{host}{clean_path}'

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    return url

# --- DATABASE CONFIGURATION ---
default_sqlite_uri = 'sqlite:///users.db'
raw_db_uri = os.getenv('DATABASE_URL', '').strip()

# Check if a custom DATABASE_URL is configured (e.g., Supabase PostgreSQL)
if raw_db_uri and 'YOUR_PASSWORD' not in raw_db_uri and 'YOUR_PROJECT_ID' not in raw_db_uri:
    db_uri = format_database_url(raw_db_uri)
    print(f"[*] Configured Supabase / PostgreSQL database.")
else:
    db_uri = default_sqlite_uri
    if raw_db_uri:
        print("[*] Notice: DATABASE_URL contains placeholder values. Falling back to local SQLite.")
        print("[*] To connect to Supabase, update DATABASE_URL in your .env with your actual Supabase credentials.")
    else:
        print("[*] No DATABASE_URL specified. Using default local SQLite database.")

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Create database tables inside the application context
with app.app_context():
    try:
        db.create_all()
        print("[*] Database tables verified/created successfully.")
    except Exception as e:
        print(f"[*] Database initialization notice: {e}")
        print("[*] If using Supabase, please verify network connectivity and that your DATABASE_URL in .env is valid.")

# --- CONFIGURATION ---
LAT = 12.9716   # Bangalore
LON = 77.5946

# --- ROUTES ---

@app.route('/', methods=['GET'])
def dashboard():
    """Real-time Weather + AQI via Open-Meteo (free, no key)."""
    try:
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={LAT}&longitude={LON}"
            f"&current=temperature_2m,relative_humidity_2m"
        )
        w_res = requests.get(weather_url, timeout=5).json()
        temp = w_res.get('current', {}).get('temperature_2m', 'N/A')
        hum = w_res.get('current', {}).get('relative_humidity_2m', 'N/A')

        aqi_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={LAT}&longitude={LON}&current=european_aqi"
        )
        a_res = requests.get(aqi_url, timeout=5).json()
        aqi = a_res.get('current', {}).get('european_aqi', 'N/A')

        return jsonify({
            "temperature": temp,
            "humidity": hum,
            "aqi": aqi,
            "location": "Bangalore"
        })
    except Exception as e:
        return jsonify({"error": "Failed to retrieve data", "message": str(e)})


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint that reports database connection status."""
    is_supabase = "postgresql" in app.config['SQLALCHEMY_DATABASE_URI']
    return jsonify({
        "status": "healthy",
        "database_type": "Supabase (PostgreSQL)" if is_supabase else "SQLite (Local)",
        "configured": is_supabase
    }), 200


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Check if user already exists
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(
        name=data.get('name'),
        phone=data.get('phone'),
        email=data.get('email'),
        roll_number=data.get('rollNumber'),
        school=data.get('school'),
        class_name=data.get('className')
    )

    # Ensure password is provided before hashing
    password = data.get('password')
    if not password:
        return jsonify({"error": "Password is required"}), 400

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Signup successful", "user": new_user.to_dict()}), 201


@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data.get("email")).first()

    if user and user.check_password(data.get("password")):
        return jsonify({"message": "Signin successful", "user": user.to_dict()}), 200

    return jsonify({"error": "Invalid email or password"}), 401


@app.route('/profile', methods=['POST'])
def profile():
    data = request.json
    if not data or not data.get("email"):
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=data.get("email")).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict()}), 200


@app.route("/chat", methods=["POST"])
def chat():
    """EcoBot via Pollinations.ai (free, no key)."""
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "Please provide a message."}), 400

    prompt = (
        "You are EcoBot, an environmental expert for students. "
        f"Answer briefly and helpfully: {user_message}"
    )
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        response = requests.get(url, timeout=20)

        if response.status_code == 200:
            return jsonify({"reply": response.text})
        return jsonify({"reply": "I'm having trouble connecting right now. Try again!"})
    except Exception:
        return jsonify({"reply": "Sorry, I encountered an error. Please try again."})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
