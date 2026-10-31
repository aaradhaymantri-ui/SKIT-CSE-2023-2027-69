# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# 1. Initialize the database
db = SQLAlchemy()

# 2. Define the User Model
class User(db.Model):
    # Explicit table name avoids collision with PostgreSQL's reserved 'user' keyword in Supabase
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    roll_number = db.Column(db.String(50))
    school = db.Column(db.String(100))
    class_name = db.Column(db.String(50))
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "roll_number": self.roll_number,
            "school": self.school,
            "class_name": self.class_name
            # Removed password_hash for security!
        }
