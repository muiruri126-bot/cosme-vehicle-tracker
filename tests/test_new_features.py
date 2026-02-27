"""
Tests for new features: Change Password, Password Reset, User Profile, Admin Reset.
"""

import pytest
from models import db, User
from tests.conftest import login


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CHANGE PASSWORD                                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestChangePassword:
    def test_change_password_page_requires_login(self, client):
        r = client.get("/change-password", follow_redirects=True)
        assert b"login" in r.data.lower()

    def test_change_password_page_loads(self, client, admin_user):
        login(client)
        r = client.get("/change-password")
        assert r.status_code == 200
        assert b"change password" in r.data.lower()

    def test_change_password_wrong_current(self, client, admin_user):
        login(client)
        r = client.post("/change-password", data={
            "current_password": "wrongpassword",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }, follow_redirects=True)
        assert b"current password is incorrect" in r.data.lower()

    def test_change_password_too_short(self, client, admin_user):
        login(client)
        r = client.post("/change-password", data={
            "current_password": "password123",
            "new_password": "abc",
            "confirm_password": "abc",
        }, follow_redirects=True)
        assert b"at least 6 characters" in r.data.lower()

    def test_change_password_mismatch(self, client, admin_user):
        login(client)
        r = client.post("/change-password", data={
            "current_password": "password123",
            "new_password": "newpass123",
            "confirm_password": "different",
        }, follow_redirects=True)
        assert b"do not match" in r.data.lower()

    def test_change_password_same_as_current(self, client, admin_user):
        login(client)
        r = client.post("/change-password", data={
            "current_password": "password123",
            "new_password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=True)
        assert b"must be different" in r.data.lower()

    def test_change_password_success(self, client, admin_user, app):
        login(client)
        r = client.post("/change-password", data={
            "current_password": "password123",
            "new_password": "newsecure456",
            "confirm_password": "newsecure456",
        }, follow_redirects=True)
        assert b"changed successfully" in r.data.lower()
        # Verify the password was actually changed
        with app.app_context():
            user = User.query.filter_by(username="testadmin").first()
            assert user.check_password("newsecure456")
            # Reset password back so later tests aren't affected
            user.set_password("password123")
            db.session.commit()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  FORCED PASSWORD CHANGE                                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestForcedPasswordChange:
    def test_forced_user_redirected_to_change_password(self, client, app):
        """A user with must_change_password=True should be redirected to change-password."""
        with app.app_context():
            user = User.query.filter_by(username="forceduser").first()
            if not user:
                user = User(
                    username="forceduser",
                    email="forced@test.org",
                    full_name="Forced User",
                    role="requester",
                    must_change_password=True,
                )
                user.set_password("temppass123")
                db.session.add(user)
                db.session.commit()

        login(client, username="forceduser", password="temppass123")
        r = client.get("/", follow_redirects=True)
        assert b"must change your password" in r.data.lower()

    def test_forced_user_can_access_change_password(self, client, app):
        with app.app_context():
            user = User.query.filter_by(username="forceduser2").first()
            if not user:
                user = User(
                    username="forceduser2",
                    email="forced2@test.org",
                    full_name="Forced User 2",
                    role="requester",
                    must_change_password=True,
                )
                user.set_password("temppass123")
                db.session.add(user)
                db.session.commit()

        login(client, username="forceduser2", password="temppass123")
        r = client.get("/change-password")
        assert r.status_code == 200

    def test_forced_flag_cleared_after_change(self, client, app):
        with app.app_context():
            user = User.query.filter_by(username="forceduser3").first()
            if not user:
                user = User(
                    username="forceduser3",
                    email="forced3@test.org",
                    full_name="Forced User 3",
                    role="requester",
                    must_change_password=True,
                )
                user.set_password("temppass123")
                db.session.add(user)
                db.session.commit()

        login(client, username="forceduser3", password="temppass123")
        r = client.post("/change-password", data={
            "current_password": "temppass123",
            "new_password": "permanentpass",
            "confirm_password": "permanentpass",
        }, follow_redirects=True)
        assert b"changed successfully" in r.data.lower()
        with app.app_context():
            user = User.query.filter_by(username="forceduser3").first()
            assert not user.must_change_password


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PASSWORD RESET (FORGOT PASSWORD)                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestPasswordReset:
    def test_forgot_password_page_loads(self, client):
        r = client.get("/forgot-password")
        assert r.status_code == 200
        assert b"forgot password" in r.data.lower()

    def test_forgot_password_submit(self, client, admin_user):
        """Submitting an email should always show the same success message (prevent enumeration)."""
        r = client.post("/forgot-password", data={"email": "admin@test.org"}, follow_redirects=True)
        assert b"if that email is registered" in r.data.lower()

    def test_forgot_password_unknown_email(self, client):
        r = client.post("/forgot-password", data={"email": "nobody@test.org"}, follow_redirects=True)
        assert b"if that email is registered" in r.data.lower()

    def test_reset_token_generated(self, client, admin_user, app):
        """Submitting a valid email should generate a reset token."""
        client.post("/forgot-password", data={"email": "admin@test.org"}, follow_redirects=True)
        with app.app_context():
            user = User.query.filter_by(email="admin@test.org").first()
            assert user.password_reset_token is not None
            assert user.password_reset_expiry is not None

    def test_reset_password_invalid_token(self, client):
        r = client.get("/reset-password/invalidtoken", follow_redirects=True)
        assert b"invalid or expired" in r.data.lower()

    def test_reset_password_valid_token(self, client, admin_user, app):
        """A valid token should show the reset form."""
        with app.app_context():
            user = User.query.filter_by(username="testadmin").first()
            token = user.generate_reset_token()
            db.session.commit()
        r = client.get(f"/reset-password/{token}")
        assert r.status_code == 200
        assert b"reset password" in r.data.lower()

    def test_reset_password_success(self, client, admin_user, app):
        with app.app_context():
            user = User.query.filter_by(username="testadmin").first()
            token = user.generate_reset_token()
            db.session.commit()
        r = client.post(f"/reset-password/{token}", data={
            "new_password": "resetpass456",
            "confirm_password": "resetpass456",
        }, follow_redirects=True)
        assert b"has been reset" in r.data.lower()
        with app.app_context():
            user = User.query.filter_by(username="testadmin").first()
            assert user.check_password("resetpass456")
            assert user.password_reset_token is None
            # Reset password back so later tests aren't affected
            user.set_password("password123")
            db.session.commit()

    def test_reset_password_mismatch(self, client, admin_user, app):
        with app.app_context():
            user = User.query.filter_by(username="testadmin").first()
            token = user.generate_reset_token()
            db.session.commit()
        r = client.post(f"/reset-password/{token}", data={
            "new_password": "resetpass456",
            "confirm_password": "differentpass",
        }, follow_redirects=True)
        assert b"do not match" in r.data.lower()

    def test_reset_password_too_short(self, client, admin_user, app):
        with app.app_context():
            user = User.query.filter_by(username="testadmin").first()
            token = user.generate_reset_token()
            db.session.commit()
        r = client.post(f"/reset-password/{token}", data={
            "new_password": "abc",
            "confirm_password": "abc",
        }, follow_redirects=True)
        assert b"at least 6 characters" in r.data.lower()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  USER PROFILE                                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestProfile:
    def test_profile_requires_login(self, client):
        r = client.get("/profile", follow_redirects=True)
        assert b"login" in r.data.lower()

    def test_profile_page_loads(self, client, admin_user):
        login(client)
        r = client.get("/profile")
        assert r.status_code == 200
        assert b"my profile" in r.data.lower()
        assert b"testadmin" in r.data.lower()

    def test_profile_update_success(self, client, admin_user, app):
        login(client)
        r = client.post("/profile", data={
            "full_name": "Updated Name",
            "email": "updated@test.org",
        }, follow_redirects=True)
        assert b"profile updated" in r.data.lower()
        with app.app_context():
            user = User.query.filter_by(username="testadmin").first()
            assert user.full_name == "Updated Name"
            assert user.email == "updated@test.org"

    def test_profile_update_empty_name(self, client, admin_user):
        login(client)
        r = client.post("/profile", data={
            "full_name": "",
            "email": "admin@test.org",
        }, follow_redirects=True)
        assert b"full name is required" in r.data.lower()

    def test_profile_update_invalid_email(self, client, admin_user):
        login(client)
        r = client.post("/profile", data={
            "full_name": "Test Admin",
            "email": "invalidemail",
        }, follow_redirects=True)
        assert b"valid email" in r.data.lower()

    def test_profile_update_duplicate_email(self, client, admin_user, driver_user):
        login(client)
        r = client.post("/profile", data={
            "full_name": "Test Admin",
            "email": "driver@test.org",  # already used by driver_user
        }, follow_redirects=True)
        assert b"already used" in r.data.lower()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ADMIN PASSWORD RESET                                                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class TestAdminResetPassword:
    def test_admin_reset_requires_admin(self, client, driver_user):
        login(client, username="testdriver", password="password123")
        r = client.post("/users/1/reset-password", data={"new_password": "newpass123"}, follow_redirects=True)
        assert b"do not have permission" in r.data.lower()

    def test_admin_reset_password_too_short(self, client, admin_user, driver_user, app):
        login(client)
        with app.app_context():
            driver = User.query.filter_by(username="testdriver").first()
            driver_id = driver.id
        r = client.post(f"/users/{driver_id}/reset-password", data={"new_password": "abc"}, follow_redirects=True)
        assert b"at least 6 characters" in r.data.lower()

    def test_admin_reset_password_success(self, client, admin_user, driver_user, app):
        login(client)
        with app.app_context():
            driver = User.query.filter_by(username="testdriver").first()
            driver_id = driver.id
        r = client.post(f"/users/{driver_id}/reset-password", data={"new_password": "adminreset789"}, follow_redirects=True)
        assert b"has been reset" in r.data.lower()
        with app.app_context():
            driver = User.query.filter_by(username="testdriver").first()
            assert driver.check_password("adminreset789")
            assert driver.must_change_password  # forced to change on next login
            # Reset back so later tests aren't affected
            driver.set_password("password123")
            driver.must_change_password = False
            db.session.commit()
