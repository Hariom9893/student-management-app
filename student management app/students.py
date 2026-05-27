"""
routes/students.py - Student CRUD Routes
==========================================
This Blueprint handles all student-related operations.
Every route here is PROTECTED — you need a valid JWT token.

Routes:
  POST   /api/students/          → Add a new student
  GET    /api/students/          → Get all students (with search, filter, pagination)
  GET    /api/students/<id>      → Get a specific student by ID
  PUT    /api/students/<id>      → Update a student's information
  DELETE /api/students/<id>      → Delete a student

CONCEPT: HTTP Methods
  GET    → Read data (safe, no side effects)
  POST   → Create new data
  PUT    → Update/replace existing data
  DELETE → Remove data

CONCEPT: Query Parameters vs Body
  GET /api/students/?course=Python&age=20&page=1&per_page=5
  These are QUERY PARAMETERS — appended to the URL after '?'
  
  POST /api/students/ with body { "name": "Alice" }
  This is a REQUEST BODY — used for creating/updating data
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from models import db, Student
from helpers import ( 
    success_response,
    error_response,
    validate_required_fields,
    validate_age,
    validate_email_format
)

students_bp = Blueprint("students", __name__)


# =============================================================================
# ROUTE: Add a new student
# METHOD: POST
# URL: /api/students/
# HEADERS: Authorization: Bearer <token>
# BODY: { "name": "...", "age": 20, "course": "...", "email": "..." }
# =============================================================================
@students_bp.route("/", methods=["POST"])
@jwt_required()  # 🔒 Protected — must be logged in
def add_student():
    """
    Create a new student record in the database.
    
    Validations:
    - All 4 fields (name, age, course, email) must be present
    - Age must be a valid integer between 1 and 120
    - Email must be a valid format
    - Email must be unique (no two students with same email)
    """

    data = request.get_json(silent=True)

    # Validate all required fields are present
    is_valid, error_msg = validate_required_fields(data, ["name", "age", "course", "email"])
    if not is_valid:
        return jsonify(error_response(error_msg)[0]), 400

    # Validate age
    is_valid_age, age_error = validate_age(data["age"])
    if not is_valid_age:
        return jsonify(error_response(age_error)[0]), 400

    # Validate email format
    is_valid_email, email_error = validate_email_format(data["email"])
    if not is_valid_email:
        return jsonify(error_response(email_error)[0]), 400

    # Check for duplicate email — emails must be unique per student
    email = data["email"].strip().lower()
    if Student.query.filter_by(email=email).first():
        return jsonify(error_response("A student with this email already exists")[0]), 409

    # Create the student object
    new_student = Student(
        name=data["name"].strip(),
        age=int(data["age"]),
        course=data["course"].strip(),
        email=email
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify(success_response(
        data=new_student.to_dict(),
        message="Student added successfully",
        status_code=201
    )[0]), 201


# =============================================================================
# ROUTE: Get all students (with Search, Filter, Pagination)
# METHOD: GET
# URL: /api/students/?course=Python&age=20&page=1&per_page=5&search=Alice
# HEADERS: Authorization: Bearer <token>
# =============================================================================
@students_bp.route("/", methods=["GET"])
@jwt_required()
def get_all_students():
    """
    Retrieve all students with optional filtering, searching, and pagination.
    
    Query Parameters (all optional):
    - search     : Search by name (partial match, case-insensitive)
    - course     : Filter by exact course name
    - age        : Filter by exact age
    - min_age    : Filter students older than or equal to this age
    - max_age    : Filter students younger than or equal to this age
    - page       : Page number (default: 1)
    - per_page   : Results per page (default: 10, max: 50)
    
    CONCEPT: Pagination
    Imagine 1000 students — returning all at once is slow and wasteful.
    Pagination splits results into "pages" of N items each.
    page=1&per_page=10 → first 10 students
    page=2&per_page=10 → students 11-20
    """

    # -----------------------------------------------------------------------
    # Start with a base query — we'll add filters to it step by step
    # query = SELECT * FROM students
    # -----------------------------------------------------------------------
    query = Student.query

    # --- SEARCH by name (partial, case-insensitive) ---
    # request.args.get() reads query parameters from the URL
    search = request.args.get("search", "").strip()
    if search:
        # ilike = case-insensitive LIKE
        # '%Alice%' matches "Alice", "alice", "ALICE Smith" etc.
        query = query.filter(Student.name.ilike(f"%{search}%"))

    # --- FILTER by course (exact match) ---
    course = request.args.get("course", "").strip()
    if course:
        # Use ilike for case-insensitive course matching too
        query = query.filter(Student.course.ilike(course))

    # --- FILTER by exact age ---
    age = request.args.get("age", "").strip()
    if age:
        is_valid_age, _ = validate_age(age)
        if is_valid_age:
            query = query.filter(Student.age == int(age))

    # --- FILTER by age range ---
    min_age = request.args.get("min_age", "").strip()
    if min_age:
        is_valid, _ = validate_age(min_age)
        if is_valid:
            query = query.filter(Student.age >= int(min_age))

    max_age = request.args.get("max_age", "").strip()
    if max_age:
        is_valid, _ = validate_age(max_age)
        if is_valid:
            query = query.filter(Student.age <= int(max_age))

    # --- PAGINATION ---
    # Get page number (default 1) and per_page (default 10, capped at 50)
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(50, max(1, int(request.args.get("per_page", 10))))
    except (ValueError, TypeError):
        page, per_page = 1, 10

    # paginate() does the LIMIT/OFFSET SQL for us
    # paginate(page=1, per_page=10) → LIMIT 10 OFFSET 0
    # paginate(page=2, per_page=10) → LIMIT 10 OFFSET 10
    pagination = query.order_by(Student.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False  # Don't raise 404 if page is empty
    )

    students = [student.to_dict() for student in pagination.items]

    return jsonify(success_response(
        data={
            "students": students,
            "pagination": {
                "total": pagination.total,       # total matching students
                "pages": pagination.pages,       # total pages
                "current_page": page,
                "per_page": per_page,
                "has_next": pagination.has_next, # is there a next page?
                "has_prev": pagination.has_prev  # is there a previous page?
            },
            "filters_applied": {
                "search": search or None,
                "course": course or None,
                "age": age or None,
                "min_age": min_age or None,
                "max_age": max_age or None
            }
        },
        message="Students retrieved successfully"
    )[0]), 200


# =============================================================================
# ROUTE: Get a single student by ID
# METHOD: GET
# URL: /api/students/1
# HEADERS: Authorization: Bearer <token>
# =============================================================================
@students_bp.route("/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):
    """
    Retrieve a single student by their ID.
    
    CONCEPT: URL Parameters
    <int:student_id> is a URL variable — Flask extracts it from the URL
    /api/students/5  →  student_id = 5
    
    db.session.get() is the modern way to do a primary key lookup.
    It returns None if not found (we handle that below).
    """

    student = db.session.get(Student, student_id)

    if not student:
        return jsonify(error_response(f"Student with ID {student_id} not found")[0]), 404  # 404 = Not Found

    return jsonify(success_response(
        data=student.to_dict(),
        message="Student retrieved successfully"
    )[0]), 200


# =============================================================================
# ROUTE: Update a student
# METHOD: PUT
# URL: /api/students/1
# HEADERS: Authorization: Bearer <token>
# BODY: { "name": "Updated Name", "age": 22 }  (only fields you want to change)
# =============================================================================
@students_bp.route("/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id):
    """
    Update an existing student's information.
    
    This is a PARTIAL update — you only need to send the fields you want to change.
    For example: { "age": 22 } will only update the age.
    
    Steps:
    1. Find the student by ID
    2. Validate any provided fields
    3. Check email uniqueness (if email is being changed)
    4. Update only the provided fields
    5. Commit and return updated student
    """

    # Find the student first
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify(error_response(f"Student with ID {student_id} not found")[0]), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify(error_response("Request body is empty or not valid JSON")[0]), 400

    # Check if at least one valid field was provided
    allowed_fields = {"name", "age", "course", "email"}
    provided_fields = set(data.keys()) & allowed_fields
    if not provided_fields:
        return jsonify(error_response(
            f"No valid fields provided. Allowed fields: {', '.join(allowed_fields)}"
        )[0]), 400

    # --- Validate and update 'name' if provided ---
    if "name" in data:
        name = str(data["name"]).strip()
        if not name:
            return jsonify(error_response("Name cannot be empty")[0]), 400
        student.name = name

    # --- Validate and update 'age' if provided ---
    if "age" in data:
        is_valid_age, age_error = validate_age(data["age"])
        if not is_valid_age:
            return jsonify(error_response(age_error)[0]), 400
        student.age = int(data["age"])

    # --- Validate and update 'course' if provided ---
    if "course" in data:
        course = str(data["course"]).strip()
        if not course:
            return jsonify(error_response("Course cannot be empty")[0]), 400
        student.course = course

    # --- Validate and update 'email' if provided ---
    if "email" in data:
        email = str(data["email"]).strip().lower()

        # Validate format
        is_valid_email, email_error = validate_email_format(email)
        if not is_valid_email:
            return jsonify(error_response(email_error)[0]), 400

        # Check if the new email is already used by ANOTHER student
        # We exclude the current student from this check (their current email is fine)
        existing = Student.query.filter_by(email=email).first()
        if existing and existing.id != student_id:
            return jsonify(error_response("A student with this email already exists")[0]), 409

        student.email = email

    # Commit changes to the database
    db.session.commit()

    return jsonify(success_response(
        data=student.to_dict(),
        message="Student updated successfully"
    )[0]), 200


# =============================================================================
# ROUTE: Delete a student
# METHOD: DELETE
# URL: /api/students/1
# HEADERS: Authorization: Bearer <token>
# =============================================================================
@students_bp.route("/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    """
    Permanently delete a student from the database.
    
    Returns 204 No Content on success (standard REST convention for DELETE).
    But we return 200 with a message so it's easier to see in Postman.
    """

    student = db.session.get(Student, student_id)
    if not student:
        return jsonify(error_response(f"Student with ID {student_id} not found")[0]), 404

    # Store the student data before deleting (to include in response)
    student_data = student.to_dict()

    # Delete from database
    db.session.delete(student)
    db.session.commit()

    return jsonify(success_response(
        data=student_data,
        message=f"Student '{student_data['name']}' deleted successfully"
    )[0]), 200


# =============================================================================
# ROUTE: Get all unique courses (bonus helper endpoint)
# METHOD: GET
# URL: /api/students/courses
# HEADERS: Authorization: Bearer <token>
# =============================================================================
@students_bp.route("/courses", methods=["GET"])
@jwt_required()
def get_courses():
    """
    Returns a list of all unique course names.
    Useful for building dropdown menus in a frontend.
    """

    # db.session.query(Student.course) → SELECT course FROM students
    # .distinct() → SELECT DISTINCT course FROM students
    courses = db.session.query(Student.course).distinct().all()

    # Each result is a tuple like ('Python',), so we unpack with [0]
    course_list = sorted([c[0] for c in courses])

    return jsonify(success_response(
        data={"courses": course_list, "total": len(course_list)},
        message="Courses retrieved successfully"
    )[0]), 200


# =============================================================================
# ROUTE: Get student statistics
# METHOD: GET
# URL: /api/students/stats
# HEADERS: Authorization: Bearer <token>
# =============================================================================
@students_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    """
    Returns summary statistics about the student database.
    Great for building dashboard widgets!
    """
    from sqlalchemy import func

    total_students = Student.query.count()

    # Average age using SQL AVG function
    avg_age_result = db.session.query(func.avg(Student.age)).scalar()
    avg_age = round(float(avg_age_result), 1) if avg_age_result else 0

    # Count students per course
    course_counts = db.session.query(
        Student.course,
        func.count(Student.id).label("count")
    ).group_by(Student.course).all()

    course_distribution = {course: count for course, count in course_counts}

    return jsonify(success_response(
        data={
            "total_students": total_students,
            "average_age": avg_age,
            "course_distribution": course_distribution,
            "total_courses": len(course_distribution)
        },
        message="Statistics retrieved successfully"
    )[0]), 200
