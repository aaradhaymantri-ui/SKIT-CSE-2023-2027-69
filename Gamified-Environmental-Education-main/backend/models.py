# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# 1. Initialize the database
db = SQLAlchemy()

# 2. Define the User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    roll_number = db.Column(db.String(50))
    school = db.Column(db.String(100))
    class_name = db.Column(db.String(50))
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default="student")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "roll_number": self.roll_number,
            "school": self.school,
            "class_name": self.class_name,
            "role": self.role
            # Removed password_hash for security!
        }


class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    frequency = db.Column(db.String(10), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    class_name = db.Column(db.String(50), nullable=False, index=True)
    school = db.Column(db.String(100), nullable=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    active = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "frequency": self.frequency,
            "points": self.points,
            "className": self.class_name,
            "school": self.school,
            "createdAt": self.created_at.isoformat()
        }


class MissionCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey("mission.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    period_key = db.Column(db.String(10), nullable=False)
    reflection = db.Column(db.String(500), nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    mission = db.relationship("Mission")
    student = db.relationship("User")
    __table_args__ = (
        db.UniqueConstraint("mission_id", "student_id", "period_key"),
    )