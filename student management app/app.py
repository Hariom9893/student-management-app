"""
app.py - Main Application Entry Point
=======================================
This is where everything comes together.

WHAT THIS FILE DOES:
1. Creates the Flask app
2. Loads configuration (from config.py)
3. Initializes extensions (SQLAlchemy, JWT)
4. Registers Blueprints (auth routes, student routes)
5. Creates database tables if they don't exist
6. Starts the development server

RUN WITH:
    python app.py

Or with Flask CLI:
    flask run
"""

import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from config import Config
from models import db

# ─── Import Blueprints ────────────────────────────────────────────────────────
# Each blueprint is a group of related routes
from auth import auth_bp
from students import students_bp

def create_app(config_class=Config):
    """
    Application Factory Pattern
    ============================
    Instead of creating the app at module level, we use a function.
    
    WHY?
    - Easier to test (you can create multiple app instances)
    - Avoids circular imports
    - More flexible configuration
    
    This is the recommended Flask pattern for any non-trivial app.
    """

    app = Flask(__name__)

    # Load settings from our Config class
    app.config.from_object(config_class)

    # ─── Initialize Extensions ────────────────────────────────────────────────
    # Extensions need to be "told" about our app before they can work

    # SQLAlchemy — connects our models to the database
    db.init_app(app)

    # JWTManager — handles token validation, expiry errors, etc.
    jwt = JWTManager(app)

    # ─── Register Blueprints ──────────────────────────────────────────────────
    # url_prefix means every route in auth_bp starts with /api/auth
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Every route in students_bp starts with /api/students
    app.register_blueprint(students_bp, url_prefix="/api/students")

    # ─── JWT Error Handlers ───────────────────────────────────────────────────
    # These run when JWT validation fails — return clean JSON errors instead
    # of Flask's default HTML error pages

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Runs when no Authorization header is provided."""
        return jsonify({
            "success": False,
            "message": "Authorization token is missing. Include 'Authorization: Bearer <token>' header."
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Runs when the token is malformed or has an invalid signature."""
        return jsonify({
            "success": False,
            "message": "Invalid token. Please log in again."
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Runs when the token has expired (after 24 hours by default)."""
        return jsonify({
            "success": False,
            "message": "Token has expired. Please log in again."
        }), 401

    # ─── Global Error Handlers ────────────────────────────────────────────────
    # These catch common HTTP errors and return JSON instead of HTML

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "The requested URL was not found on this server."
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "message": "HTTP method not allowed for this endpoint."
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "message": "An internal server error occurred. Please try again later."
        }), 500

    # ─── Health Check Route ───────────────────────────────────────────────────
    # A simple endpoint to verify the server is running
    # Useful for deployment monitoring and load balancers

    @app.route("/")
    def index():
        return jsonify({
            "success": True,
            "message": "Student Management System API is running!",
            "version": "1.0.0",
            "endpoints": {
                "auth": {
                    "register": "POST /api/auth/register",
                    "login": "POST /api/auth/login",
                    "profile": "GET /api/auth/me  [protected]"
                },
                "students": {
                    "create": "POST /api/students/  [protected]",
                    "list": "GET /api/students/  [protected]",
                    "detail": "GET /api/students/<id>  [protected]",
                    "update": "PUT /api/students/<id>  [protected]",
                    "delete": "DELETE /api/students/<id>  [protected]",
                    "courses": "GET /api/students/courses  [protected]",
                    "stats": "GET /api/students/stats  [protected]"
                }
            }
        })

    # ─── Create Database Tables ───────────────────────────────────────────────
    # This runs ONCE when the app starts
    # db.create_all() looks at all models and creates their tables if they don't exist
    # It WON'T delete existing tables — safe to run repeatedly

    with app.app_context():
        # Make sure the database directory exists
        db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "database")
        os.makedirs(db_dir, exist_ok=True)

        db.create_all()
        print("✅ Database tables created (or already exist)")

    return app


# ─── Run the App ──────────────────────────────────────────────────────────────
# This block only runs when you execute: python app.py
# When imported (e.g., by tests or a WSGI server), it won't run

app = create_app()

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  Student Management System API")
    print("="*55)
    app.run(debug=True, host="0.0.0.0", port=5000)

    print("\n" + "="*55)
    print("  🎓 Student Management System API")
    print("="*55)
    print("  Server running at: http://127.0.0.1:5000")
    print("  Health check:      GET  /")
    print("  Register:          POST /api/auth/register")
    print("  Login:             POST /api/auth/login")
    print("  Students:          /api/students/")
    print("="*55 + "\n")

    # debug=True enables:
    # - Auto-reload when you change code
    # - Detailed error pages
    # NEVER use debug=True in production!
    app.run(debug=True, host="0.0.0.0", port=5000)
