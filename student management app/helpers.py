"""
utils/helpers.py - Reusable Helper Functions
=============================================
Helper functions are small utility tools used across multiple route files.
Keeping them here avoids repeating the same code in every route.

Think of these as your personal toolkit — grab what you need!
"""


def success_response(data=None, message="Success", status_code=200):
    """
    Build a standardized success JSON response.
    
    WHY standardize responses?
    - Every API response looks the same → frontend developers love you
    - Easier to debug — you always know where to find data vs messages
    
    Example output:
    {
        "success": true,
        "message": "Student created",
        "data": { "id": 1, "name": "Alice" }
    }
    """
    response = {
        "success": True,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    return response, status_code


def error_response(message="An error occurred", status_code=400):
    """
    Build a standardized error JSON response.
    
    Example output:
    {
        "success": false,
        "message": "Email already exists"
    }
    """
    return {
        "success": False,
        "message": message
    }, status_code


def validate_required_fields(data, required_fields):
    """
    Check that all required fields are present in the request data.
    
    Args:
        data (dict): The JSON body from the request
        required_fields (list): List of field names that must exist
    
    Returns:
        (bool, str): (True, None) if valid, (False, error_message) if invalid
    
    Example:
        valid, msg = validate_required_fields(
            {"name": "Alice"},
            ["name", "email", "age"]
        )
        # → (False, "Missing required fields: email, age")
    """
    if not data:
        return False, "Request body is empty or not valid JSON"

    missing = [field for field in required_fields if field not in data or str(data[field]).strip() == ""]

    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    return True, None


def validate_age(age):
    """
    Validate that age is a positive integer within a reasonable range.
    
    Returns:
        (bool, str): (True, None) if valid, (False, error_message) if invalid
    """
    try:
        age = int(age)
        if age < 1 or age > 120:
            return False, "Age must be between 1 and 120"
        return True, None
    except (ValueError, TypeError):
        return False, "Age must be a valid integer"


def validate_email_format(email):
    """
    Basic email format validation (checks for @ and a dot after it).
    For production, use a library like 'email-validator'.
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, None
