"""
config.py - Application Configuration
======================================
This file holds all the settings for our Flask app.
Think of it like a settings panel — database location, secret keys, etc.

WHY a separate config file?
- Keeps settings in one place (easy to change later)
- Lets you swap SQLite → PostgreSQL with ONE line change
- Secrets can be loaded from environment variables for security
"""

import os
from datetime import timedelta

# BASE_DIR = the folder where this file lives
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class.
    All settings live here as class variables.
    """

    # -----------------------------------------------------------------------
    # SECRET KEY — used by Flask to sign cookies and session data
    # IMPORTANT: In production, set this via an environment variable!
    # os.environ.get("SECRET_KEY", "fallback") means:
    #   "use the env var if it exists, otherwise use the fallback string"
    # -----------------------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-dev-key-change-in-production")

    # -----------------------------------------------------------------------
    # DATABASE — SQLAlchemy connection string
    # sqlite:///  means "use a local file"
    # We store the .db file inside the /database/ folder
    # -----------------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'database.db')}"
    )

    # Disable SQLAlchemy's change-tracking system (saves memory, not needed here)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------------------------------------------------
    # JWT (JSON Web Token) settings
    # JWT is how we authenticate users after login — like a digital wristband
    # -----------------------------------------------------------------------
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-dev-key-change-in-production")

    # How long a token stays valid before the user must log in again
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
