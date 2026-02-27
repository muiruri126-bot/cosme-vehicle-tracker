"""
Integration tests for COSME Vehicle Tracker Flask routes.
Tests authentication, authorization, CRUD operations, and business rules.
"""

import pytest
from datetime import datetime, timedelta
from models import db, User, Vehicle, Booking, Trip, MaintenanceRecord
from tests.conftest import login


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  1. AUTHENTICATION ROUTES                                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestAuthentication:
    def test_login_page_loads(self, client):
        r = client.get("/login")
        assert r.status_code == 200

    def test_login_empty_fields(self, client):
        r = client.post("/login", data={"username": "", "password": ""}, follow_redirects=True)
        assert b"please enter both" in r.data.lower()

    def test_login_wrong_password(self, client, admin_user):
        r = client.post("/login", data={"username": "testadmin", "password": "wrong"}, follow_redirects=True)
        assert b"invalid username or password" in r.data.lower()

    def test_login_success(self, client, admin_user):
        r = login(client)
        assert b"welcome back" in r.data.lower()

    def test_login_inactive_user(self, client, app, admin_user):
        """Deactivated users should be rejected at login."""
        with app.app_context():
            user = User(username="inactive1", email="inact@t.org", full_name="Inactive", role="requester", is_active_user=False)
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
        r = client.post("/login", data={"username": "inactive1", "password": "password123"}, follow_redirects=True)
        assert b"deactivated" in r.data.lower()

    def test_logout(self, client, admin_user):
        login(client)
        r = client.get("/logout", follow_redirects=True)
        assert b"logged out" in r.data.lower()

    def test_unauthenticated_redirect(self, client):
        """Accessing a protected route without login should redirect."""
        r = client.get("/", follow_redirects=True)
        assert b"login" in r.data.lower()


class TestRegistration:
    def test_register_page_loads(self, client):
        r = client.get("/register")
        assert r.status_code == 200

    def test_register_empty_fields(self, client):
        r = client.post("/register", data={
            "full_name": "", "username": "", "email": "", "password": "", "password2": ""
        }, follow_redirects=True)
        assert b"full name is required" in r.data.lower()

    def test_register_short_username(self, client):
        r = client.post("/register", data={
            "full_name": "X", "username": "ab", "email": "x@x.com",
            "password": "test1234", "password2": "test1234"
        }, follow_redirects=True)
        assert b"at least 3 characters" in r.data.lower()

    def test_register_invalid_username_chars(self, client):
        r = client.post("/register", data={
            "full_name": "X", "username": "a!b@c", "email": "x@x.com",
            "password": "test1234", "password2": "test1234"
        }, follow_redirects=True)
        assert b"letters, numbers, dots" in r.data.lower()

    def test_register_short_password(self, client):
        r = client.post("/register", data={
            "full_name": "X", "username": "shortpw", "email": "sp@x.com",
            "password": "12", "password2": "12"
        }, follow_redirects=True)
        assert b"at least 6 characters" in r.data.lower()

    def test_register_password_mismatch(self, client):
        r = client.post("/register", data={
            "full_name": "X", "username": "mismatch", "email": "mm@x.com",
            "password": "test1234", "password2": "different"
        }, follow_redirects=True)
        assert b"do not match" in r.data.lower()

    def test_register_duplicate_username(self, client, admin_user):
        r = client.post("/register", data={
            "full_name": "X", "username": "testadmin", "email": "new@x.com",
            "password": "test1234", "password2": "test1234"
        }, follow_redirects=True)
        assert b"already taken" in r.data.lower()

    def test_register_success(self, client):
        r = client.post("/register", data={
            "full_name": "New User", "username": "newuser99",
            "email": "new99@test.org", "password": "test1234", "password2": "test1234"
        }, follow_redirects=True)
        assert b"account created" in r.data.lower()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  2. AUTHORIZATION (role_required)                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestAuthorization:
    def test_requester_cannot_access_users(self, client, requester_user):
        """Non-admin users should be denied access to admin pages."""
        login(client, username="testrequester")
        r = client.get("/users", follow_redirects=True)
        assert b"do not have permission" in r.data.lower()

    def test_requester_cannot_add_vehicle(self, client, requester_user):
        login(client, username="testrequester")
        r = client.get("/vehicles/add", follow_redirects=True)
        assert b"do not have permission" in r.data.lower()

    def test_admin_can_access_users(self, client, admin_user):
        login(client)
        r = client.get("/users")
        assert r.status_code == 200


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  3. VEHICLE CRUD                                                         ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestVehicleCRUD:
    def test_add_vehicle_empty_fields(self, client, admin_user):
        login(client)
        r = client.post("/vehicles/add", data={
            "registration_number": "", "make": "", "model": "", "status": "available"
        }, follow_redirects=True)
        assert b"registration number is required" in r.data.lower()

    def test_add_vehicle_reg_too_short(self, client, admin_user):
        login(client)
        r = client.post("/vehicles/add", data={
            "registration_number": "AB", "make": "Toyota", "model": "Hilux", "status": "available"
        }, follow_redirects=True)
        assert b"too short" in r.data.lower()

    def test_add_vehicle_success(self, client, admin_user):
        login(client)
        r = client.post("/vehicles/add", data={
            "registration_number": "KCC 300C", "make": "Toyota", "model": "Hilux", "status": "available"
        }, follow_redirects=True)
        assert b"registered successfully" in r.data.lower()

    def test_add_vehicle_duplicate_reg(self, client, admin_user, vehicle):
        login(client)
        r = client.post("/vehicles/add", data={
            "registration_number": "KAA 001A", "make": "Ford", "model": "Ranger", "status": "available"
        }, follow_redirects=True)
        assert b"already exists" in r.data.lower()

    def test_vehicle_list_loads(self, client, admin_user, vehicle):
        login(client)
        r = client.get("/vehicles")
        assert r.status_code == 200
        assert b"KAA 001A" in r.data


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  4. BOOKING WORKFLOW                                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestBookingWorkflow:
    def test_add_booking_empty_fields(self, client, admin_user, vehicle):
        login(client)
        r = client.post("/bookings/add", data={
            "vehicle_id": "", "start_datetime_planned": "", "end_datetime_planned": "",
            "route_from": "", "route_to": "", "purpose": ""
        }, follow_redirects=True)
        assert b"select a vehicle" in r.data.lower()

    def test_add_booking_end_before_start(self, client, admin_user, vehicle):
        login(client)
        r = client.post("/bookings/add", data={
            "vehicle_id": vehicle.id,
            "start_datetime_planned": "2026-12-10T10:00",
            "end_datetime_planned": "2026-12-10T08:00",
            "route_from": "A", "route_to": "B", "purpose": "Test"
        }, follow_redirects=True)
        assert b"end date/time must be after start" in r.data.lower()

    def test_add_booking_past_date(self, client, admin_user, vehicle):
        login(client)
        r = client.post("/bookings/add", data={
            "vehicle_id": vehicle.id,
            "start_datetime_planned": "2020-01-01T10:00",
            "end_datetime_planned": "2020-01-01T18:00",
            "route_from": "A", "route_to": "B", "purpose": "Test"
        }, follow_redirects=True)
        assert b"cannot be in the past" in r.data.lower()

    def test_add_booking_maintenance_vehicle_blocked(self, client, app, admin_user):
        login(client)
        with app.app_context():
            mv = Vehicle(registration_number="MNT 999", make="Nissan", model="Patrol", status="maintenance")
            db.session.add(mv)
            db.session.commit()
            mv_id = mv.id
        r = client.post("/bookings/add", data={
            "vehicle_id": mv_id,
            "start_datetime_planned": "2026-12-15T08:00",
            "end_datetime_planned": "2026-12-15T18:00",
            "route_from": "A", "route_to": "B", "purpose": "Test"
        }, follow_redirects=True)
        assert b"under maintenance" in r.data.lower()

    def test_add_booking_success(self, client, admin_user, vehicle):
        login(client)
        r = client.post("/bookings/add", data={
            "vehicle_id": vehicle.id,
            "start_datetime_planned": "2027-01-15T08:00",
            "end_datetime_planned": "2027-01-15T18:00",
            "route_from": "Kilifi", "route_to": "Mombasa", "purpose": "Field visit"
        }, follow_redirects=True)
        assert b"booking request created" in r.data.lower()

    def test_add_booking_conflict_detected(self, client, app, admin_user, vehicle):
        login(client)
        # Create first booking
        client.post("/bookings/add", data={
            "vehicle_id": vehicle.id,
            "start_datetime_planned": "2027-02-01T08:00",
            "end_datetime_planned": "2027-02-01T18:00",
            "route_from": "X", "route_to": "Y", "purpose": "First"
        }, follow_redirects=True)
        # Try overlapping booking
        r = client.post("/bookings/add", data={
            "vehicle_id": vehicle.id,
            "start_datetime_planned": "2027-02-01T10:00",
            "end_datetime_planned": "2027-02-01T16:00",
            "route_from": "X", "route_to": "Y", "purpose": "Overlap"
        }, follow_redirects=True)
        assert b"already booked" in r.data.lower()

    def test_approve_pending_booking(self, client, app, admin_user, vehicle):
        login(client)
        with app.app_context():
            b = Booking(
                requester_name="Test", requester_id=admin_user.id, vehicle_id=vehicle.id,
                start_datetime_planned=datetime(2027, 3, 1, 8, 0),
                end_datetime_planned=datetime(2027, 3, 1, 18, 0),
                route_from="A", route_to="B", purpose="T", status="pending",
            )
            db.session.add(b)
            db.session.commit()
            bid = b.id
        r = client.post(f"/bookings/{bid}/approve", follow_redirects=True)
        assert b"approved" in r.data.lower()

    def test_cancel_booking(self, client, app, admin_user, vehicle):
        login(client)
        with app.app_context():
            b = Booking(
                requester_name="Test", requester_id=admin_user.id, vehicle_id=vehicle.id,
                start_datetime_planned=datetime(2027, 4, 1, 8, 0),
                end_datetime_planned=datetime(2027, 4, 1, 18, 0),
                route_from="A", route_to="B", purpose="T", status="pending",
            )
            db.session.add(b)
            db.session.commit()
            bid = b.id
        r = client.post(f"/bookings/{bid}/cancel", follow_redirects=True)
        assert b"cancelled" in r.data.lower()

    def test_cannot_cancel_completed(self, client, app, admin_user, vehicle):
        login(client)
        with app.app_context():
            b = Booking(
                requester_name="Test", requester_id=admin_user.id, vehicle_id=vehicle.id,
                start_datetime_planned=datetime(2027, 5, 1, 8, 0),
                end_datetime_planned=datetime(2027, 5, 1, 18, 0),
                route_from="A", route_to="B", purpose="T", status="completed",
            )
            db.session.add(b)
            db.session.commit()
            bid = b.id
        r = client.post(f"/bookings/{bid}/cancel", follow_redirects=True)
        assert b"cannot be cancelled" in r.data.lower()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  5. TRIP START / END                                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestTripWorkflow:
    def _create_approved_booking(self, app, admin_user, vehicle, start_offset_days=100):
        with app.app_context():
            b = Booking(
                requester_name="Test", requester_id=admin_user.id, vehicle_id=vehicle.id,
                start_datetime_planned=datetime(2027, 6, 1 + start_offset_days % 28, 8, 0),
                end_datetime_planned=datetime(2027, 6, 1 + start_offset_days % 28, 18, 0),
                route_from="A", route_to="B", purpose="T", status="approved",
            )
            db.session.add(b)
            db.session.commit()
            return b.id

    def test_trip_start_empty_fields(self, client, app, admin_user, vehicle):
        login(client)
        bid = self._create_approved_booking(app, admin_user, vehicle, 0)
        r = client.post(f"/bookings/{bid}/trip/start", data={
            "start_actual_datetime": "", "odometer_start": ""
        }, follow_redirects=True)
        assert b"start date/time is required" in r.data.lower()
        assert b"odometer reading is required" in r.data.lower()

    def test_trip_start_negative_odometer(self, client, app, admin_user, vehicle):
        login(client)
        bid = self._create_approved_booking(app, admin_user, vehicle, 1)
        r = client.post(f"/bookings/{bid}/trip/start", data={
            "start_actual_datetime": "2027-06-02T08:30", "odometer_start": "-100"
        }, follow_redirects=True)
        assert b"cannot be negative" in r.data.lower()

    def test_trip_start_success(self, client, app, admin_user, vehicle):
        login(client)
        bid = self._create_approved_booking(app, admin_user, vehicle, 2)
        r = client.post(f"/bookings/{bid}/trip/start", data={
            "start_actual_datetime": "2027-06-03T08:30", "odometer_start": "50000"
        }, follow_redirects=True)
        assert b"trip started" in r.data.lower()

    def test_trip_end_odometer_less_than_start(self, client, app, admin_user, vehicle):
        login(client)
        bid = self._create_approved_booking(app, admin_user, vehicle, 3)
        # Start the trip first
        client.post(f"/bookings/{bid}/trip/start", data={
            "start_actual_datetime": "2027-06-04T08:30", "odometer_start": "50000"
        }, follow_redirects=True)
        # Try ending with lower odometer
        r = client.post(f"/bookings/{bid}/trip/end", data={
            "end_actual_datetime": "2027-06-04T17:30", "odometer_end": "49000"
        }, follow_redirects=True)
        assert b"cannot be less than" in r.data.lower()

    def test_trip_end_before_start_time(self, client, app, admin_user, vehicle):
        login(client)
        bid = self._create_approved_booking(app, admin_user, vehicle, 4)
        client.post(f"/bookings/{bid}/trip/start", data={
            "start_actual_datetime": "2027-06-05T08:30", "odometer_start": "50000"
        }, follow_redirects=True)
        r = client.post(f"/bookings/{bid}/trip/end", data={
            "end_actual_datetime": "2027-06-05T07:00", "odometer_end": "50500"
        }, follow_redirects=True)
        assert b"must be after" in r.data.lower()

    def test_trip_end_negative_fuel(self, client, app, admin_user, vehicle):
        login(client)
        bid = self._create_approved_booking(app, admin_user, vehicle, 5)
        client.post(f"/bookings/{bid}/trip/start", data={
            "start_actual_datetime": "2027-06-06T08:30", "odometer_start": "50000"
        }, follow_redirects=True)
        r = client.post(f"/bookings/{bid}/trip/end", data={
            "end_actual_datetime": "2027-06-06T17:30", "odometer_end": "50500",
            "fuel_used": "-10", "fuel_cost": "-500"
        }, follow_redirects=True)
        assert b"cannot be negative" in r.data.lower()

    def test_trip_end_success(self, client, app, admin_user, vehicle):
        login(client)
        bid = self._create_approved_booking(app, admin_user, vehicle, 6)
        client.post(f"/bookings/{bid}/trip/start", data={
            "start_actual_datetime": "2027-06-07T08:30", "odometer_start": "50000"
        }, follow_redirects=True)
        r = client.post(f"/bookings/{bid}/trip/end", data={
            "end_actual_datetime": "2027-06-07T17:30", "odometer_end": "50480",
            "fuel_used": "45", "fuel_cost": "6750"
        }, follow_redirects=True)
        assert b"trip ended" in r.data.lower()

    def test_cannot_start_trip_on_pending_booking(self, client, app, admin_user, vehicle):
        login(client)
        with app.app_context():
            b = Booking(
                requester_name="Test", requester_id=admin_user.id, vehicle_id=vehicle.id,
                start_datetime_planned=datetime(2027, 7, 1, 8, 0),
                end_datetime_planned=datetime(2027, 7, 1, 18, 0),
                route_from="A", route_to="B", purpose="T", status="pending",
            )
            db.session.add(b)
            db.session.commit()
            bid = b.id
        r = client.post(f"/bookings/{bid}/trip/start", data={
            "start_actual_datetime": "2027-07-01T08:30", "odometer_start": "50000"
        }, follow_redirects=True)
        assert b"only approved bookings" in r.data.lower()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  6. MAINTENANCE                                                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestMaintenance:
    def test_add_maintenance_empty_fields(self, client, admin_user):
        login(client)
        r = client.post("/maintenance/add", data={
            "vehicle_id": "", "maintenance_type": "routine",
            "description": "", "scheduled_date": ""
        }, follow_redirects=True)
        assert b"select a vehicle" in r.data.lower()

    def test_add_maintenance_negative_cost(self, client, admin_user, vehicle):
        login(client)
        r = client.post("/maintenance/add", data={
            "vehicle_id": vehicle.id, "maintenance_type": "routine",
            "description": "Oil change", "scheduled_date": "2027-08-01",
            "cost": "-500"
        }, follow_redirects=True)
        assert b"cannot be negative" in r.data.lower()

    def test_add_maintenance_success(self, client, admin_user, vehicle):
        login(client)
        r = client.post("/maintenance/add", data={
            "vehicle_id": vehicle.id, "maintenance_type": "routine",
            "description": "Oil change", "scheduled_date": "2027-08-01",
            "cost": "5000"
        }, follow_redirects=True)
        assert b"maintenance record created" in r.data.lower()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  7. REPORTS & CALENDAR                                                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestReportsAndCalendar:
    def test_vehicle_report_page_loads(self, client, admin_user):
        login(client)
        r = client.get("/reports/vehicle")
        assert r.status_code == 200

    def test_budget_report_page_loads(self, client, admin_user):
        login(client)
        r = client.get("/reports/budget")
        assert r.status_code == 200

    def test_calendar_page_loads(self, client, admin_user):
        login(client)
        r = client.get("/calendar")
        assert r.status_code == 200

    def test_api_bookings_returns_json(self, client, admin_user):
        login(client)
        r = client.get("/api/bookings")
        assert r.status_code == 200
        assert r.content_type == "application/json"

    def test_audit_log_loads(self, client, admin_user):
        login(client)
        r = client.get("/audit-log")
        assert r.status_code == 200


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  8. ADMIN DELETE OPERATIONS                                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestAdminDelete:
    def test_admin_cannot_delete_self(self, client, admin_user):
        login(client)
        r = client.post(f"/users/{admin_user.id}/delete", follow_redirects=True)
        assert b"cannot delete your own" in r.data.lower()

    def test_delete_vehicle_cascades(self, client, app, admin_user):
        login(client)
        with app.app_context():
            v = Vehicle(registration_number="DEL 001", make="Del", model="Test")
            db.session.add(v)
            db.session.commit()
            vid = v.id
        r = client.post(f"/vehicles/{vid}/delete", follow_redirects=True)
        assert b"deleted" in r.data.lower()
        with app.app_context():
            assert db.session.get(Vehicle, vid) is None
