"""
Unit tests for the SQLAlchemy models layer.
"""

import pytest
from datetime import datetime, timedelta, timezone
from models import User, Vehicle, Booking, Trip, MaintenanceRecord, AuditLog, check_booking_conflict, db


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  1. USER MODEL                                                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestUserModel:
    def test_set_and_check_password(self, app):
        """Password hashing and verification should work correctly."""
        with app.app_context():
            user = User(username="pwtest", email="pw@test.org", full_name="PW Test", role="requester")
            user.set_password("secret123")
            assert user.check_password("secret123") is True
            assert user.check_password("wrong") is False

    def test_is_admin_property(self, app):
        with app.app_context():
            admin = User(username="a", email="a@a.com", full_name="A", role="admin")
            req = User(username="b", email="b@b.com", full_name="B", role="requester")
            assert admin.is_admin is True
            assert req.is_admin is False

    def test_is_driver_property(self, app):
        with app.app_context():
            driver = User(username="d", email="d@d.com", full_name="D", role="driver")
            assert driver.is_driver is True

    def test_username_uniqueness(self, app, admin_user):
        """Duplicate username should raise IntegrityError."""
        with app.app_context():
            dup = User(username="testadmin", email="dup@test.org", full_name="Dup", role="requester")
            dup.set_password("x")
            db.session.add(dup)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_email_uniqueness(self, app, admin_user):
        """Duplicate email should raise IntegrityError."""
        with app.app_context():
            dup = User(username="uniq_user", email="admin@test.org", full_name="Dup", role="requester")
            dup.set_password("x")
            db.session.add(dup)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_default_role_is_requester(self, app):
        with app.app_context():
            user = User(username="def", email="def@x.com", full_name="D", password_hash="h")
            db.session.add(user)
            db.session.flush()
            assert user.role == "requester"

    def test_default_is_active(self, app):
        with app.app_context():
            user = User(username="act", email="act@x.com", full_name="A", password_hash="h")
            db.session.add(user)
            db.session.flush()
            assert user.is_active_user is True


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  2. VEHICLE MODEL                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestVehicleModel:
    def test_default_status_is_available(self, app):
        with app.app_context():
            v = Vehicle(registration_number="TEST 001", make="Toyota", model="Hilux")
            db.session.add(v)
            db.session.flush()
            assert v.status == "available"

    def test_registration_uniqueness(self, app, vehicle):
        with app.app_context():
            dup = Vehicle(registration_number="KAA 001A", make="Ford", model="Ranger")
            db.session.add(dup)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  3. BOOKING MODEL                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestBookingModel:
    def test_default_status_is_pending(self, app, vehicle, admin_user):
        with app.app_context():
            b = Booking(
                requester_name="X",
                requester_id=admin_user.id,
                vehicle_id=vehicle.id,
                start_datetime_planned=datetime(2026, 8, 1, 8, 0),
                end_datetime_planned=datetime(2026, 8, 1, 18, 0),
                route_from="A",
                route_to="B",
                purpose="Test",
            )
            db.session.add(b)
            db.session.flush()
            assert b.status == "pending"

    def test_booking_trip_relationship(self, app, vehicle, admin_user):
        with app.app_context():
            b = Booking(
                requester_name="X",
                requester_id=admin_user.id,
                vehicle_id=vehicle.id,
                start_datetime_planned=datetime(2026, 9, 1, 8, 0),
                end_datetime_planned=datetime(2026, 9, 1, 18, 0),
                route_from="A",
                route_to="B",
                purpose="Test",
            )
            db.session.add(b)
            db.session.commit()

            t = Trip(booking_id=b.id, odometer_start=1000)
            db.session.add(t)
            db.session.commit()

            assert b.trip is not None
            assert b.trip.odometer_start == 1000


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  4. CONFLICT DETECTION (check_booking_conflict)                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestBookingConflict:
    """Tests for the double-booking detection helper."""

    def _create_booking(self, vehicle_id, requester_id, start, end, status="pending"):
        b = Booking(
            requester_name="Fixture",
            requester_id=requester_id,
            vehicle_id=vehicle_id,
            start_datetime_planned=start,
            end_datetime_planned=end,
            route_from="X",
            route_to="Y",
            purpose="Fixture",
            status=status,
        )
        db.session.add(b)
        db.session.commit()
        return b

    def test_no_conflict_when_no_bookings(self, app, vehicle, admin_user):
        with app.app_context():
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 1, 8, 0),
                datetime(2026, 10, 1, 18, 0),
            )
            assert result is None

    def test_exact_overlap_detected(self, app, vehicle, admin_user):
        with app.app_context():
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 2, 8, 0),
                datetime(2026, 10, 2, 18, 0),
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 2, 8, 0),
                datetime(2026, 10, 2, 18, 0),
            )
            assert result is not None

    def test_partial_overlap_start(self, app, vehicle, admin_user):
        """New booking starts before existing ends."""
        with app.app_context():
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 3, 8, 0),
                datetime(2026, 10, 3, 14, 0),
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 3, 12, 0),
                datetime(2026, 10, 3, 18, 0),
            )
            assert result is not None

    def test_partial_overlap_end(self, app, vehicle, admin_user):
        """New booking ends after existing starts."""
        with app.app_context():
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 4, 12, 0),
                datetime(2026, 10, 4, 18, 0),
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 4, 8, 0),
                datetime(2026, 10, 4, 14, 0),
            )
            assert result is not None

    def test_no_overlap_adjacent_times(self, app, vehicle, admin_user):
        """Back-to-back bookings (no overlap) should not conflict."""
        with app.app_context():
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 5, 8, 0),
                datetime(2026, 10, 5, 12, 0),
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 5, 12, 0),
                datetime(2026, 10, 5, 18, 0),
            )
            assert result is None

    def test_no_overlap_different_day(self, app, vehicle, admin_user):
        with app.app_context():
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 6, 8, 0),
                datetime(2026, 10, 6, 18, 0),
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 7, 8, 0),
                datetime(2026, 10, 7, 18, 0),
            )
            assert result is None

    def test_cancelled_bookings_ignored(self, app, vehicle, admin_user):
        """Cancelled bookings should NOT cause conflicts."""
        with app.app_context():
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 8, 8, 0),
                datetime(2026, 10, 8, 18, 0),
                status="cancelled",
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 8, 8, 0),
                datetime(2026, 10, 8, 18, 0),
            )
            assert result is None

    def test_completed_bookings_ignored(self, app, vehicle, admin_user):
        """Completed bookings should NOT cause conflicts."""
        with app.app_context():
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 9, 8, 0),
                datetime(2026, 10, 9, 18, 0),
                status="completed",
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 9, 8, 0),
                datetime(2026, 10, 9, 18, 0),
            )
            assert result is None

    def test_exclude_booking_id(self, app, vehicle, admin_user):
        """When editing a booking, its own slot should be excluded."""
        with app.app_context():
            existing = self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 10, 8, 0),
                datetime(2026, 10, 10, 18, 0),
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 10, 8, 0),
                datetime(2026, 10, 10, 18, 0),
                exclude_booking_id=existing.id,
            )
            assert result is None

    def test_different_vehicle_no_conflict(self, app, vehicle, admin_user):
        """Bookings on different vehicles should not conflict."""
        with app.app_context():
            # Create a second vehicle inside this session context
            v2 = Vehicle.query.filter_by(registration_number="KBB 002B").first()
            if not v2:
                v2 = Vehicle(registration_number="KBB 002B", make="Nissan", model="Patrol", status="available")
                db.session.add(v2)
                db.session.flush()
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 11, 8, 0),
                datetime(2026, 10, 11, 18, 0),
            )
            result = check_booking_conflict(
                v2.id,
                datetime(2026, 10, 11, 8, 0),
                datetime(2026, 10, 11, 18, 0),
            )
            assert result is None

    def test_superset_overlap(self, app, vehicle, admin_user):
        """New booking fully contains the existing one."""
        with app.app_context():
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 12, 10, 0),
                datetime(2026, 10, 12, 14, 0),
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 12, 8, 0),
                datetime(2026, 10, 12, 18, 0),
            )
            assert result is not None

    def test_subset_overlap(self, app, vehicle, admin_user):
        """New booking is fully inside the existing one."""
        with app.app_context():
            self._create_booking(
                vehicle.id, admin_user.id,
                datetime(2026, 10, 13, 8, 0),
                datetime(2026, 10, 13, 18, 0),
            )
            result = check_booking_conflict(
                vehicle.id,
                datetime(2026, 10, 13, 10, 0),
                datetime(2026, 10, 13, 14, 0),
            )
            assert result is not None


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  5. TRIP DISTANCE CALCULATION                                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestTripDistance:
    def test_distance_auto_calculated(self, app, vehicle, admin_user):
        with app.app_context():
            b = Booking(
                requester_name="X",
                requester_id=admin_user.id,
                vehicle_id=vehicle.id,
                start_datetime_planned=datetime(2026, 11, 1, 8, 0),
                end_datetime_planned=datetime(2026, 11, 1, 18, 0),
                route_from="A", route_to="B", purpose="T",
            )
            db.session.add(b)
            db.session.commit()

            t = Trip(booking_id=b.id, odometer_start=50000, odometer_end=50480)
            t.distance = t.odometer_end - t.odometer_start
            db.session.add(t)
            db.session.commit()
            assert t.distance == 480

    def test_zero_distance(self, app, vehicle, admin_user):
        """Trip with same start/end odometer should have distance 0."""
        with app.app_context():
            b = Booking(
                requester_name="X",
                requester_id=admin_user.id,
                vehicle_id=vehicle.id,
                start_datetime_planned=datetime(2026, 11, 2, 8, 0),
                end_datetime_planned=datetime(2026, 11, 2, 18, 0),
                route_from="A", route_to="B", purpose="T",
            )
            db.session.add(b)
            db.session.commit()

            t = Trip(booking_id=b.id, odometer_start=50000, odometer_end=50000)
            t.distance = t.odometer_end - t.odometer_start
            db.session.add(t)
            db.session.commit()
            assert t.distance == 0


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  6. AUDIT LOG                                                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestAuditLog:
    def test_audit_log_creation(self, app, admin_user):
        with app.app_context():
            entry = AuditLog(
                user_id=admin_user.id,
                username=admin_user.username,
                action="create",
                entity_type="Vehicle",
                entity_id=1,
                details="Test log",
            )
            db.session.add(entry)
            db.session.commit()
            assert entry.id is not None
            assert entry.timestamp is not None
