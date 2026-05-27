"""
models.py - Database Models
============================
Models define the shape of our database tables using Python classes.
SQLAlchemy translates these classes into actual SQL CREATE TABLE statements.

CONCEPT: ORM (Object-Relational Mapping)
Instead of writing raw SQL like:
    INSERT INTO students (name, age) VALUES ('Alice', 20)
We write Python like:
    student = Student(name='Alice', age=20)
    db.session.add(student)

SQLAlchemy handles the SQL for us!
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# db is the SQLAlchemy instance — we import this everywhere we need DB access
db = SQLAlchemy()


class User(db.Model):
    """
    User Model — represents the 'users' table in our database.
    Users can register and log in to get a JWT token.
    
    Table: users
    Columns: id, username, email, password_hash, created_at
    """

    __tablename__ = "users"  # explicit table name (optional but clear)

    # PRIMARY KEY — unique identifier for each row, auto-increments
    id = db.Column(db.Integer, primary_key=True)

    # UNIQUE constraints prevent two users with the same username/email
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # We NEVER store plain passwords — only the hash!
    password_hash = db.Column(db.String(256), nullable=False)

    # Automatically record when the user registered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -------------------------------------------------------------------
    # Password methods
    # We use werkzeug's security functions which use PBKDF2-SHA256 hashing
    # -------------------------------------------------------------------

    def set_password(self, password):
        """
        Hash the plain-text password and store it.
        generate_password_hash("mypassword") → "pbkdf2:sha256:260000$..."
        The hash is one-way — you can't reverse it to get the original!
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if a plain-text password matches the stored hash.
        Returns True if correct, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert the User object to a dictionary (for JSON responses)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        """String representation — useful for debugging."""
        return f"<User {self.username}>"


class Student(db.Model):
    """
    Student Model — represents the 'students' table in our database.
    
    Table: students
    Columns: id, name, age, course, email, created_at, updated_at
    """

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    # nullable=False means this field is REQUIRED
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    course = db.Column(db.String(100), nullable=False)

    # Email must be unique — no two students can share an email
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Timestamps for record-keeping
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """
        Convert Student object → Python dict → JSON response.
        Flask's jsonify() can only serialize dicts/lists, not SQLAlchemy objects.
        """
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "course": self.course,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Student {self.name}>"
