"""
Shared pytest fixtures for COSME Vehicle Tracker tests.
Uses an in-memory SQLite database so tests never touch production data.
"""

import pytest
from datetime import datetime, timedelta

from app import app as flask_app, limiter
from models import db as _db, User, Vehicle, Booking, Trip, MaintenanceRecord


@pytest.fixture(scope="session")
def app():
    """Create the Flask application with a test config."""
    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret",
            "MAIL_ENABLED": False,
            "LOGIN_DISABLED": False,
            "RATELIMIT_ENABLED": False,
        }
    )
    limiter.enabled = False
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Roll back every transaction so each test starts fresh."""
    with app.app_context():
        yield
        _db.session.rollback()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_session(app):
    """Provide the SQLAlchemy session for direct model tests."""
    with app.app_context():
        yield _db.session


# ── Helper: Create Users ────────────────────────────────────────────────────


@pytest.fixture()
def admin_user(app):
    with app.app_context():
        user = User.query.filter_by(username="testadmin").first()
        if not user:
            user = User(
                username="testadmin",
                email="admin@test.org",
                full_name="Test Admin",
                role="admin",
            )
            user.set_password("password123")
            _db.session.add(user)
            _db.session.commit()
        return user


@pytest.fixture()
def driver_user(app):
    with app.app_context():
        user = User.query.filter_by(username="testdriver").first()
        if not user:
            user = User(
                username="testdriver",
                email="driver@test.org",
                full_name="Test Driver",
                role="driver",
            )
            user.set_password("password123")
            _db.session.add(user)
            _db.session.commit()
        return user


@pytest.fixture()
def requester_user(app):
    with app.app_context():
        user = User.query.filter_by(username="testrequester").first()
        if not user:
            user = User(
                username="testrequester",
                email="req@test.org",
                full_name="Test Requester",
                role="requester",
            )
            user.set_password("password123")
            _db.session.add(user)
            _db.session.commit()
        return user


@pytest.fixture()
def vehicle(app):
    with app.app_context():
        v = Vehicle.query.filter_by(registration_number="KAA 001A").first()
        if not v:
            v = Vehicle(
                registration_number="KAA 001A",
                make="Toyota",
                model="Land Cruiser",
                status="available",
            )
            _db.session.add(v)
            _db.session.commit()
        return v


@pytest.fixture()
def maintenance_vehicle(app):
    with app.app_context():
        v = Vehicle.query.filter_by(registration_number="KBB 002B").first()
        if not v:
            v = Vehicle(
                registration_number="KBB 002B",
                make="Nissan",
                model="Patrol",
                status="maintenance",
            )
            _db.session.add(v)
            _db.session.commit()
        return v


# ── Helper: Login ────────────────────────────────────────────────────────────


def login(client, username="testadmin", password="password123"):
    """Log in via the login form and return the response."""
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
