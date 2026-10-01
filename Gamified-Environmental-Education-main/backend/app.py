# app.py
from datetime import date, datetime, time, timedelta
from functools import wraps

from flask import Flask, g, request, jsonify
from flask_cors import CORS
from sqlalchemy import and_, desc, func, inspect, text
from sqlalchemy.exc import IntegrityError
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from models import db, Mission, MissionCompletion, User
import os
import requests
import urllib.parse

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or os.urandom(32)
CORS(app)
token_serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# --- DATABASE CONFIGURATION ---
default_sqlite_uri = 'sqlite:///users.db'
db_uri = os.getenv('DATABASE_URL', default_sqlite_uri)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Create database tables inside the application context
with app.app_context():
    db.create_all()
    user_columns = {column["name"] for column in inspect(db.engine).get_columns(User.__tablename__)}
    if "role" not in user_columns or "username" not in user_columns:
        user_table = db.engine.dialect.identifier_preparer.quote(User.__tablename__)
    if "role" not in user_columns:
        db.session.execute(text(
            f"ALTER TABLE {user_table} ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'student'"
        ))
    if "username" not in user_columns:
        db.session.execute(text(
            f"ALTER TABLE {user_table} ADD COLUMN username VARCHAR(50)"
        ))
        db.session.commit()
    for legacy_user in User.query.filter(
        (User.username.is_(None)) | (User.username == "")
    ).all():
        legacy_user.username = f"eco{legacy_user.id}"
    db.session.commit()

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


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    class_name = data.get("className")
    school = data.get("school")
    role = data.get("role", "student")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name is required"}), 400
    if not isinstance(username, str) or not 3 <= len(username.strip()) <= 30:
        return jsonify({"error": "Username must be between 3 and 30 characters"}), 400
    username = username.strip().lower()
    if not all(character.isalnum() or character in "_-" for character in username):
        return jsonify({"error": "Username may only contain letters, numbers, underscores, and hyphens"}), 400
    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "Email is required"}), 400
    if not isinstance(class_name, str) or not class_name.strip():
        return jsonify({"error": "Class is required"}), 400
    if not isinstance(school, str) or not school.strip():
        return jsonify({"error": "School is required"}), 400
    if role not in ("student", "teacher"):
        return jsonify({"error": "Role must be student or teacher"}), 400
    email = email.strip().lower()

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409
    if User.query.filter(func.lower(User.username) == username).first():
        return jsonify({"error": "Username already exists"}), 409

    new_user = User(
        name=name.strip(),
        username=username,
        phone=data.get('phone'),
        email=email,
        roll_number=data.get('rollNumber'),
        school=school.strip(),
        class_name=class_name.strip(),
        role=role
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
    if (not data or not isinstance(data.get("email"), str)
            or not data.get("email").strip()
            or not isinstance(data.get("password"), str)
            or not data.get("password")):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data.get("email").strip().lower()).first()

    if user and user.check_password(data.get("password")):
        token = token_serializer.dumps({"user_id": user.id})
        return jsonify({
            "message": "Signin successful",
            "user": user.to_dict(),
            "token": token
        }), 200
    
    return jsonify({"error": "Invalid email or password"}), 401


def mission_period_key(frequency, current_date=None):
    current_date = current_date or datetime.utcnow().date()
    if frequency == "daily":
        return current_date.isoformat()
    iso_year, iso_week, _ = current_date.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def require_authenticated_user(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        scheme, separator, token = request.headers.get(
            "Authorization", ""
        ).partition(" ")
        if scheme.lower() != "bearer" or not separator or not token:
            return jsonify({"error": "Sign in to access this information"}), 401
        try:
            token_data = token_serializer.loads(token, max_age=60 * 60 * 24 * 30)
        except (BadSignature, SignatureExpired):
            return jsonify({"error": "Session expired; please sign in again"}), 401

        user = User.query.get(token_data.get("user_id"))
        if not user:
            return jsonify({"error": "User not found"}), 401
        g.current_user = user
        return view(*args, **kwargs)
    return wrapped


def require_mission_role(role):
    def decorator(view):
        @wraps(view)
        @require_authenticated_user
        def wrapped(*args, **kwargs):
            if g.current_user.role != role:
                return jsonify({"error": f"A {role} account is required"}), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


def student_mission_stats(student):
    completions = MissionCompletion.query.filter_by(student_id=student.id).all()
    completion_dates = sorted({
        completion.completed_at.date()
        for completion in completions
    }, reverse=True)
    today = datetime.utcnow().date()
    if completion_dates and completion_dates[0] == today - timedelta(days=1):
        today -= timedelta(days=1)
    streak = 0
    expected_day = today
    for completed_day in completion_dates:
        if completed_day == expected_day:
            streak += 1
            expected_day -= timedelta(days=1)
        elif completed_day < expected_day:
            break

    return {
        "points": sum(completion.points_earned for completion in completions),
        "completedCount": len(completions),
        "streak": streak
    }


@app.route("/missions", methods=["GET"])
@require_mission_role("student")
def get_student_missions():
    student = g.current_user

    missions = Mission.query.filter_by(
        class_name=student.class_name, school=student.school, active=True
    ).order_by(Mission.created_at.desc()).all()
    completions = MissionCompletion.query.filter_by(student_id=student.id).all()
    completion_lookup = {
        (completion.mission_id, completion.period_key): completion
        for completion in completions
    }
    mission_data = []
    for mission in missions:
        completion = completion_lookup.get(
            (mission.id, mission_period_key(mission.frequency))
        )
        mission_data.append({
            **mission.to_dict(),
            "completed": completion is not None,
            "reflection": completion.reflection if completion else ""
        })

    return jsonify({
        "missions": mission_data,
        "stats": student_mission_stats(student)
    })


@app.route("/missions", methods=["POST"])
@require_mission_role("teacher")
def create_mission():
    data = request.get_json(silent=True) or {}
    teacher = g.current_user

    title = data.get("title")
    description = data.get("description")
    frequency = data.get("frequency")
    points = data.get("points")
    if not isinstance(title, str) or not title.strip() or len(title.strip()) > 120:
        return jsonify({"error": "Title is required and must be 120 characters or fewer"}), 400
    if not isinstance(description, str) or not description.strip() or len(description.strip()) > 1000:
        return jsonify({"error": "Description is required and must be 1000 characters or fewer"}), 400
    if frequency not in ("daily", "weekly"):
        return jsonify({"error": "Frequency must be daily or weekly"}), 400
    if isinstance(points, bool) or not isinstance(points, int) or not 5 <= points <= 500:
        return jsonify({"error": "Points must be a whole number between 5 and 500"}), 400

    mission = Mission(
        title=title.strip(),
        description=description.strip(),
        frequency=frequency,
        points=points,
        class_name=teacher.class_name,
        school=teacher.school,
        created_by=teacher.id
    )
    db.session.add(mission)
    db.session.commit()
    return jsonify({"mission": mission.to_dict()}), 201


@app.route("/missions/<int:mission_id>/complete", methods=["POST"])
@require_mission_role("student")
def complete_mission(mission_id):
    data = request.get_json(silent=True) or {}
    student = g.current_user

    reflection = data.get("reflection")
    if not isinstance(reflection, str) or not 10 <= len(reflection.strip()) <= 500:
        return jsonify({"error": "Reflection must be between 10 and 500 characters"}), 400
    mission = Mission.query.filter_by(
        id=mission_id, class_name=student.class_name,
        school=student.school, active=True
    ).first()
    if not mission:
        return jsonify({"error": "Mission not found"}), 404

    period_key = mission_period_key(mission.frequency)
    existing = MissionCompletion.query.filter_by(
        mission_id=mission.id,
        student_id=student.id,
        period_key=period_key
    ).first()
    if existing:
        return jsonify({"error": "You have already completed this mission for this period"}), 409

    completion = MissionCompletion(
        mission_id=mission.id,
        student_id=student.id,
        period_key=period_key,
        reflection=reflection.strip(),
        points_earned=mission.points
    )
    db.session.add(completion)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "You have already completed this mission for this period"}), 409

    return jsonify({
        "message": "Mission completed",
        "stats": student_mission_stats(student)
    }), 201


@app.route("/teacher/missions", methods=["GET"])
@require_mission_role("teacher")
def get_teacher_missions():
    teacher = g.current_user

    students = User.query.filter_by(
        class_name=teacher.class_name, school=teacher.school, role="student"
    ).order_by(User.name).all()
    missions = Mission.query.filter_by(
        class_name=teacher.class_name, school=teacher.school, active=True
    ).order_by(Mission.created_at.desc()).all()
    student_data = []
    for student in students:
        student_data.append({
            "id": student.id,
            "name": student.name,
            "email": student.email,
            **student_mission_stats(student)
        })

    mission_data = []
    for mission in missions:
        period_key = mission_period_key(mission.frequency)
        completions = MissionCompletion.query.filter_by(
            mission_id=mission.id, period_key=period_key
        ).order_by(MissionCompletion.completed_at.desc()).all()
        mission_data.append({
            **mission.to_dict(),
            "completedCount": len(completions),
            "studentCount": len(students),
            "submissions": [{
                "studentName": completion.student.name,
                "reflection": completion.reflection,
                "completedAt": completion.completed_at.isoformat()
            } for completion in completions]
        })

    return jsonify({"missions": mission_data, "students": student_data})


@app.route("/leaderboard", methods=["GET"])
@require_mission_role("student")
def get_leaderboard():
    period = request.args.get("period", "weekly")
    today = datetime.utcnow().date()
    if period == "weekly":
        period_start = today - timedelta(days=today.weekday())
    elif period == "monthly":
        period_start = today.replace(day=1)
    elif period == "allTime":
        period_start = None
    else:
        return jsonify({"error": "Period must be weekly, monthly, or allTime"}), 400

    current_user = g.current_user
    completion_join = MissionCompletion.student_id == User.id
    if period_start is not None:
        completion_join = and_(
            completion_join,
            MissionCompletion.completed_at >= datetime.combine(period_start, time.min)
        )

    rows = db.session.query(
        User.id,
        User.username,
        func.coalesce(func.sum(MissionCompletion.points_earned), 0).label("points"),
        func.count(MissionCompletion.id).label("completed_count")
    ).outerjoin(
        MissionCompletion, completion_join
    ).filter(
        User.role == "student",
        User.school == current_user.school,
        User.class_name == current_user.class_name
    ).group_by(
        User.id, User.username
    ).order_by(
        desc("points"), User.username
    ).all()

    return jsonify({
        "bots": [{
            "id": row.id,
            "username": row.username,
            "name": f"BOT {row.username}",
            "ecoPoints": row.points,
            "missionsCompleted": row.completed_count,
            "isCurrentUser": row.id == current_user.id
        } for row in rows]
    })


@app.route('/profile', methods=['GET'])
@require_authenticated_user
def profile():
    return jsonify({"user": g.current_user.to_dict()}), 200


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