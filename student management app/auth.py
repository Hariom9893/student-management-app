"""
routes/auth.py - Authentication Routes
========================================
This Blueprint handles:
  POST /api/auth/register  → Create a new user account
  POST /api/auth/login     → Log in and receive a JWT token
  GET  /api/auth/me        → Get currently logged-in user info (protected)

CONCEPT: Flask Blueprint
A Blueprint is like a mini-app inside your main app.
It groups related routes together so your code stays organized.
We register it in app.py with a URL prefix like /api/auth

CONCEPT: JWT Authentication Flow
1. User registers (password gets hashed and stored)
2. User logs in → server verifies password → server creates a JWT token
3. User sends the JWT token in the Authorization header for protected routes
4. Server validates the token → grants or denies access
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from models import db, User
from utils.helpers import (
    success_response,
    error_response,
    validate_required_fields,
    validate_email_format
)

# Create the Blueprint
# "auth" is the blueprint's name (used internally by Flask)
# __name__ helps Flask find the template/static folder (not needed here but good practice)
auth_bp = Blueprint("auth", __name__)


# =============================================================================
# ROUTE: Register a new user
# METHOD: POST
# URL: /api/auth/register
# BODY: { "username": "...", "email": "...", "password": "..." }
# =============================================================================
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.
    
    Steps:
    1. Get JSON data from request body
    2. Validate required fields
    3. Check for duplicate username/email
    4. Hash the password
    5. Save user to database
    6. Return success response
    """

    # request.get_json() parses the JSON body sent by the client
    # silent=True means it returns None instead of raising an error for bad JSON
    data = request.get_json(silent=True)

    # Step 1: Validate required fields using our helper
    is_valid, error_msg = validate_required_fields(data, ["username", "email", "password"])
    if not is_valid:
        return jsonify(error_response(error_msg)[0]), 400

    # Step 2: Validate email format
    is_valid_email, email_error = validate_email_format(data["email"])
    if not is_valid_email:
        return jsonify(error_response(email_error)[0]), 400

    # Step 3: Validate password length
    if len(data["password"]) < 6:
        return jsonify(error_response("Password must be at least 6 characters")[0]), 400

    # Step 4: Check for duplicate username
    # db.session.query(User) builds a SELECT query
    # .filter_by(username=...) adds a WHERE clause
    # .first() returns the first result or None
    if User.query.filter_by(username=data["username"].strip()).first():
        return jsonify(error_response("Username already taken")[0]), 409  # 409 = Conflict

    # Step 5: Check for duplicate email
    if User.query.filter_by(email=data["email"].strip().lower()).first():
        return jsonify(error_response("Email already registered")[0]), 409

    # Step 6: Create the new User object
    new_user = User(
        username=data["username"].strip(),
        email=data["email"].strip().lower()
    )

    # set_password() hashes the password before storing
    new_user.set_password(data["password"])

    # Step 7: Save to database
    # db.session is like a "pending changes" basket
    # .add() puts the new user in the basket
    # .commit() actually saves it to the database file
    db.session.add(new_user)
    db.session.commit()

    return jsonify(success_response(
        data=new_user.to_dict(),
        message="User registered successfully",
        status_code=201
    )[0]), 201  # 201 = Created


# =============================================================================
# ROUTE: Login
# METHOD: POST
# URL: /api/auth/login
# BODY: { "username": "...", "password": "..." }
# =============================================================================
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Log in and receive a JWT access token.
    
    Steps:
    1. Get JSON data from request body
    2. Validate required fields
    3. Find user by username
    4. Verify password
    5. Generate JWT token
    6. Return token to client
    """

    data = request.get_json(silent=True)

    # Validate required fields
    is_valid, error_msg = validate_required_fields(data, ["username", "password"])
    if not is_valid:
        return jsonify(error_response(error_msg)[0]), 400

    # Find the user by username
    user = User.query.filter_by(username=data["username"].strip()).first()

    # Check if user exists AND password is correct
    # We use 'not user' to avoid leaking whether the username exists
    if not user or not user.check_password(data["password"]):
        # Same error message for both cases — security best practice!
        return jsonify(error_response("Invalid username or password")[0]), 401  # 401 = Unauthorized

    # Generate JWT token
    # identity is a string that uniquely identifies the user
    # We use str(user.id) — we can retrieve this later with get_jwt_identity()
    access_token = create_access_token(identity=str(user.id))

    return jsonify(success_response(
        data={
            "access_token": access_token,
            "token_type": "Bearer",
            "user": user.to_dict()
        },
        message="Login successful"
    )[0]), 200


# =============================================================================
# ROUTE: Get current logged-in user
# METHOD: GET
# URL: /api/auth/me
# HEADERS: Authorization: Bearer <token>
# =============================================================================
@auth_bp.route("/me", methods=["GET"])
@jwt_required()  # 🔒 This decorator PROTECTS the route — token required!
def get_current_user():
    """
    Returns the profile of the currently authenticated user.
    
    @jwt_required() automatically:
    - Checks that the Authorization header exists
    - Validates the JWT token
    - Rejects expired or tampered tokens
    
    get_jwt_identity() extracts the user ID we stored when creating the token
    """

    # Get the user ID from the JWT token
    current_user_id = get_jwt_identity()

    # Fetch the user from the database
    user = db.session.get(User, int(current_user_id))

    if not user:
        return jsonify(error_response("User not found")[0]), 404

    return jsonify(success_response(
        data=user.to_dict(),
        message="User profile retrieved"
    )[0]), 200
