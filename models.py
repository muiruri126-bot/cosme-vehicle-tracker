"""
COSME Project – Vehicle Tracker
SQLAlchemy models for User, Vehicle, Booking, Trip, and MaintenanceRecord.
"""

from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# User  (authentication + roles)
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(
        db.String(20), nullable=False, default="requester"
    )  # admin | driver | requester
    is_active_user = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    bookings_requested = db.relationship(
        "Booking", backref="requester", foreign_keys="Booking.requester_id", lazy=True
    )
    bookings_driven = db.relationship(
        "Booking", backref="driver", foreign_keys="Booking.driver_id", lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_driver(self):
        return self.role == "driver"

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ---------------------------------------------------------------------------
# Vehicle
# ---------------------------------------------------------------------------
class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="available"
    )  # available | in_use | maintenance

    # Relationships
    bookings = db.relationship("Booking", backref="vehicle", lazy=True)
    maintenance_records = db.relationship(
        "MaintenanceRecord", backref="vehicle", lazy=True
    )

    def __repr__(self):
        return f"<Vehicle {self.registration_number}>"


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------
class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    # Legacy text field kept for backwards compatibility / quick entry
    requester_name = db.Column(db.String(100), nullable=False)

    # FK links to User table
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    vehicle_id = db.Column(
        db.Integer, db.ForeignKey("vehicles.id"), nullable=False
    )

    start_datetime_planned = db.Column(db.DateTime, nullable=False)
    end_datetime_planned = db.Column(db.DateTime, nullable=False)

    route_from = db.Column(db.String(200), nullable=False)
    route_to = db.Column(db.String(200), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    activity_code = db.Column(db.String(50), nullable=True)
    project_code = db.Column(db.String(50), nullable=True)

    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # pending | approved | completed | cancelled

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    trip = db.relationship("Trip", backref="booking", uselist=False, lazy=True)

    def __repr__(self):
        return f"<Booking {self.id} – {self.requester_name}>"


# ---------------------------------------------------------------------------
# Trip
# ---------------------------------------------------------------------------
class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.id"), nullable=False, unique=True
    )

    start_actual_datetime = db.Column(db.DateTime, nullable=True)
    end_actual_datetime = db.Column(db.DateTime, nullable=True)

    odometer_start = db.Column(db.Integer, nullable=True)
    odometer_end = db.Column(db.Integer, nullable=True)
    distance = db.Column(db.Integer, nullable=True)  # auto‑calculated

    fuel_used = db.Column(db.Float, nullable=True)
    fuel_cost = db.Column(db.Float, nullable=True)  # cost of fuel in local currency
    remarks = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Trip {self.id} for Booking {self.booking_id}>"


# ---------------------------------------------------------------------------
# MaintenanceRecord
# ---------------------------------------------------------------------------
class MaintenanceRecord(db.Model):
    __tablename__ = "maintenance_records"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(
        db.Integer, db.ForeignKey("vehicles.id"), nullable=False
    )

    maintenance_type = db.Column(
        db.String(50), nullable=False
    )  # routine | repair | inspection | tyre | other
    description = db.Column(db.Text, nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    completed_date = db.Column(db.Date, nullable=True)
    cost = db.Column(db.Float, nullable=True)
    status = db.Column(
        db.String(20), nullable=False, default="scheduled"
    )  # scheduled | in_progress | completed | cancelled
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    created_by = db.relationship("User", backref="maintenance_created", lazy=True)

    def __repr__(self):
        return f"<Maintenance {self.id} – {self.maintenance_type} for Vehicle {self.vehicle_id}>"


# ---------------------------------------------------------------------------
# AuditLog  (tracks who edited/deleted what and when)
# ---------------------------------------------------------------------------
class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    action = db.Column(
        db.String(20), nullable=False
    )  # create | edit | delete | approve | cancel | assign | complete
    entity_type = db.Column(
        db.String(50), nullable=False
    )  # User | Vehicle | Booking | Trip | MaintenanceRecord
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationship (nullable – the user might have been deleted)
    user = db.relationship("User", backref="audit_logs", lazy=True)

    def __repr__(self):
        return f"<AuditLog {self.id} – {self.action} {self.entity_type} #{self.entity_id} by {self.username}>"


# ---------------------------------------------------------------------------
# Helper: Conflict Detection
# ---------------------------------------------------------------------------
def check_booking_conflict(vehicle_id, start_dt, end_dt, exclude_booking_id=None):
    """
    Return a conflicting Booking if *vehicle_id* already has an approved (or
    pending) booking whose planned window overlaps [start_dt, end_dt].

    Two intervals [A_start, A_end] and [B_start, B_end] overlap when:
        A_start < B_end  AND  B_start < A_end

    Parameters
    ----------
    vehicle_id : int
        The vehicle to check.
    start_dt : datetime
        Proposed booking start.
    end_dt : datetime
        Proposed booking end.
    exclude_booking_id : int | None
        If provided, ignore this booking (useful when editing an existing one).

    Returns
    -------
    Booking | None
        The first conflicting booking found, or None if there is no conflict.
    """
    query = Booking.query.filter(
        Booking.vehicle_id == vehicle_id,
        # Only consider bookings that are still "active" (pending or approved)
        Booking.status.in_(["pending", "approved"]),
        # Overlap condition
        Booking.start_datetime_planned < end_dt,
        Booking.end_datetime_planned > start_dt,
    )

    if exclude_booking_id is not None:
        query = query.filter(Booking.id != exclude_booking_id)

    return query.first()
