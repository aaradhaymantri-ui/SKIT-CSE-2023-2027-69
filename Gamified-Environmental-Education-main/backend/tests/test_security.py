import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import requests
import jwt

os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import (
    ACCESS_TOKEN_MINUTES,
    JWT_AUDIENCE,
    JWT_ISSUER,
    app,
    create_access_token,
    db,
    get_security_settings,
    set_auth_cookies,
)
from models import AuthSession, Mission, User


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.original_teacher_signup_code = app.config["TEACHER_SIGNUP_CODE"]
        app.config.update(TESTING=True)
        with app.app_context():
            db.drop_all()
            db.create_all()
            self.teacher = self.create_user(
                "teacher@example.test", "teacher", "teacher", "Class 1", "School A"
            )
            self.student = self.create_user(
                "student@example.test", "student", "student", "Class 1", "School A"
            )
            self.other_student = self.create_user(
                "other@example.test", "other", "student", "Class 2", "School B"
            )
            self.mission = Mission(
                title="Save water",
                description="Use less water at home.",
                frequency="daily",
                points=10,
                class_name="Class 1",
                school="School A",
                created_by=self.teacher.id,
            )
            db.session.add(self.mission)
            db.session.commit()
            self.teacher_id = self.teacher.id
            self.student_id = self.student.id
            self.other_student_id = self.other_student.id
            self.mission_id = self.mission.id
        self.client = app.test_client()

    def tearDown(self):
        app.config["TEACHER_SIGNUP_CODE"] = self.original_teacher_signup_code
        with app.app_context():
            db.session.remove()
            db.drop_all()

    @staticmethod
    def create_user(email, username, role, class_name, school):
        user = User(
            name=username.title(),
            username=username,
            email=email,
            class_name=class_name,
            school=school,
            role=role,
        )
        user.set_password("correct horse battery staple")
        db.session.add(user)
        db.session.flush()
        return user

    @staticmethod
    def auth_header(user_id):
        with app.app_context():
            user = db.session.get(User, user_id)
        return {
            "Authorization": f"Bearer {create_access_token(user)}"
        }

    def test_production_requires_long_secret_and_explicit_origins(self):
        with self.assertRaisesRegex(RuntimeError, "SECRET_KEY"):
            get_security_settings({"APP_ENV": "production"})
        with self.assertRaisesRegex(RuntimeError, "CORS_ORIGINS"):
            get_security_settings({
                "APP_ENV": "production",
                "SECRET_KEY": "s" * 32,
            })

    def test_production_security_settings_are_strict_and_disable_debug(self):
        settings = get_security_settings({
            "APP_ENV": "production",
            "FLASK_DEBUG": "1",
            "SECRET_KEY": "s" * 32,
            "CORS_ORIGINS": "https://ecoquest.example",
        })
        self.assertEqual(settings["cors_origins"], ["https://ecoquest.example"])
        self.assertFalse(settings["debug"])
        with self.assertRaisesRegex(RuntimeError, "Invalid CORS origin"):
            get_security_settings({
                "APP_ENV": "production",
                "SECRET_KEY": "s" * 32,
                "CORS_ORIGINS": "*",
            })

    def test_cors_allowlist_allows_frontend_and_rejects_unknown_origin(self):
        allowed = self.client.options(
            "/profile",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )
        denied = self.client.options(
            "/profile",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(
            allowed.headers.get("Access-Control-Allow-Origin"),
            "http://localhost:5173",
        )
        self.assertEqual(
            allowed.headers.get("Access-Control-Allow-Credentials"),
            "true",
        )
        self.assertIsNone(denied.headers.get("Access-Control-Allow-Origin"))

    def test_security_headers_are_added(self):
        response = self.client.get("/")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(
            response.headers["Referrer-Policy"],
            "strict-origin-when-cross-origin",
        )

    def test_profile_requires_a_valid_session_payload(self):
        unauthenticated = self.client.get("/profile")
        malformed = self.client.get(
            "/profile",
            headers={"Authorization": "Bearer not.a.valid.jwt"},
        )
        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(malformed.status_code, 401)

    def test_profile_rejects_expired_jwt(self):
        now = datetime.now(timezone.utc)
        expired_token = jwt.encode(
            {
                "sub": str(self.student_id),
                "iat": now - timedelta(minutes=2),
                "exp": now - timedelta(minutes=1),
                "iss": JWT_ISSUER,
                "aud": JWT_AUDIENCE,
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        response = self.client.get(
            "/profile",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        self.assertEqual(response.status_code, 401)

    def test_signin_issues_short_lived_jwt_and_httponly_refresh_cookie(self):
        response = self.client.post(
            "/signin",
            headers={"Origin": "http://localhost:5173"},
            json={
                "email": "student@example.test",
                "password": "correct horse battery staple",
            },
        )
        data = response.get_json()
        decoded = jwt.decode(
            data["accessToken"],
            app.config["SECRET_KEY"],
            algorithms=["HS256"],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
        refresh_cookie = next(
            cookie for cookie in response.headers.getlist("Set-Cookie")
            if cookie.startswith("ecoquest_refresh=")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(decoded["sub"], str(self.student_id))
        self.assertLessEqual(decoded["exp"] - decoded["iat"], ACCESS_TOKEN_MINUTES * 60)
        self.assertIn("HttpOnly", refresh_cookie)
        self.assertNotIn("refreshToken", data)
        self.assertNotIn("token", data)

    def test_production_auth_cookies_are_secure_httponly_and_samesite(self):
        original_cookie_secure = app.config["COOKIE_SECURE"]
        try:
            app.config["COOKIE_SECURE"] = True
            response = set_auth_cookies(
                app.response_class(), "refresh-placeholder", "csrf-placeholder"
            )
        finally:
            app.config["COOKIE_SECURE"] = original_cookie_secure

        refresh_cookie = next(
            cookie for cookie in response.headers.getlist("Set-Cookie")
            if cookie.startswith("ecoquest_refresh=")
        )
        csrf_cookie = next(
            cookie for cookie in response.headers.getlist("Set-Cookie")
            if cookie.startswith("ecoquest_csrf=")
        )
        self.assertIn("Secure", refresh_cookie)
        self.assertIn("HttpOnly", refresh_cookie)
        self.assertIn("SameSite=Lax", refresh_cookie)
        self.assertIn("Secure", csrf_cookie)
        self.assertNotIn("HttpOnly", csrf_cookie)
        self.assertIn("SameSite=Lax", csrf_cookie)

    def test_signin_rejects_untrusted_origin(self):
        response = self.client.post(
            "/signin",
            headers={"Origin": "https://untrusted.example"},
            json={
                "email": "student@example.test",
                "password": "correct horse battery staple",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_refresh_rotates_tokens_and_requires_csrf_protection(self):
        signin = self.client.post(
            "/signin",
            headers={"Origin": "http://localhost:5173"},
            json={
                "email": "student@example.test",
                "password": "correct horse battery staple",
            },
        )
        original = signin.get_json()
        old_refresh_cookie = next(
            cookie for cookie in signin.headers.getlist("Set-Cookie")
            if cookie.startswith("ecoquest_refresh=")
        ).split(";", 1)[0].split("=", 1)[1]
        csrf_only = self.client.post(
            "/auth/refresh",
            headers={"Origin": "http://localhost:5173"},
        )
        self.assertEqual(csrf_only.status_code, 403)

        refreshed = self.client.post(
            "/auth/refresh",
            headers={
                "Origin": "http://localhost:5173",
                "X-CSRF-Token": original["csrfToken"],
            },
        )
        rotated = refreshed.get_json()
        self.assertEqual(refreshed.status_code, 200)
        self.assertNotEqual(rotated["accessToken"], original["accessToken"])
        self.assertNotEqual(rotated["csrfToken"], original["csrfToken"])

        stale_csrf = self.client.post(
            "/auth/refresh",
            headers={
                "Origin": "http://localhost:5173",
                "X-CSRF-Token": original["csrfToken"],
            },
        )
        self.assertEqual(stale_csrf.status_code, 403)
        replay_client = app.test_client()
        replay_client.set_cookie("ecoquest_refresh", old_refresh_cookie, path="/auth")
        replay_client.set_cookie("ecoquest_csrf", original["csrfToken"], path="/")
        replay = replay_client.post(
            "/auth/refresh",
            headers={
                "Origin": "http://localhost:5173",
                "X-CSRF-Token": original["csrfToken"],
            },
        )
        self.assertEqual(replay.status_code, 401)

    def test_refresh_rejects_untrusted_origin(self):
        signin = self.client.post(
            "/signin",
            headers={"Origin": "http://localhost:5173"},
            json={
                "email": "student@example.test",
                "password": "correct horse battery staple",
            },
        )
        response = self.client.post(
            "/auth/refresh",
            headers={
                "Origin": "https://untrusted.example",
                "X-CSRF-Token": signin.get_json()["csrfToken"],
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_logout_revokes_refresh_session(self):
        signin = self.client.post(
            "/signin",
            headers={"Origin": "http://localhost:5173"},
            json={
                "email": "student@example.test",
                "password": "correct horse battery staple",
            },
        )
        logout = self.client.post(
            "/auth/logout",
            headers={
                "Origin": "http://localhost:5173",
                "X-CSRF-Token": signin.get_json()["csrfToken"],
            },
        )
        csrf = self.client.get(
            "/auth/csrf",
            headers={"Origin": "http://localhost:5173"},
        )
        with app.app_context():
            self.assertEqual(AuthSession.query.filter_by(revoked_at=None).count(), 0)
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(csrf.status_code, 401)

    def test_student_cannot_access_teacher_dashboard(self):
        response = self.client.get(
            "/teacher/missions",
            headers=self.auth_header(self.student_id),
        )
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_complete_mission_from_another_class(self):
        response = self.client.post(
            f"/missions/{self.mission_id}/complete",
            headers=self.auth_header(self.other_student_id),
            json={"reflection": "I saved water by using less today."},
        )
        self.assertEqual(response.status_code, 404)

    def test_public_signup_cannot_assign_teacher_role_without_invitation(self):
        payload = {
            "name": "New Teacher",
            "username": "newteacher",
            "email": "newteacher@example.test",
            "className": "Class 1",
            "school": "School A",
            "role": "teacher",
            "password": "a secure password",
        }
        response = self.client.post("/signup", json=payload)
        self.assertEqual(response.status_code, 403)
        self.assertIn("invitation code", response.get_json()["error"])

    def test_teacher_signup_requires_and_accepts_configured_invitation(self):
        app.config["TEACHER_SIGNUP_CODE"] = "invite-code-with-at-least-24-chars"
        payload = {
            "name": "New Teacher",
            "username": "newteacher",
            "email": "newteacher@example.test",
            "className": "Class 1",
            "school": "School A",
            "role": "teacher",
            "teacherSignupCode": app.config["TEACHER_SIGNUP_CODE"],
            "password": "a secure password",
        }
        response = self.client.post("/signup", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["user"]["role"], "teacher")

    def test_signup_rejects_short_passwords(self):
        response = self.client.post("/signup", json={
            "name": "New Student",
            "username": "newstudent",
            "email": "newstudent@example.test",
            "className": "Class 1",
            "school": "School A",
            "role": "student",
            "password": "short",
        })
        self.assertEqual(response.status_code, 400)

    def test_signup_rejects_non_object_json(self):
        response = self.client.post("/signup", json=["not", "an", "object"])
        self.assertEqual(response.status_code, 400)

    @patch("app.requests.get", side_effect=requests.RequestException("private upstream detail"))
    def test_dashboard_does_not_expose_upstream_exception(self, _mock_get):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("private upstream detail", response.get_data(as_text=True))

    @patch("app.requests.get", side_effect=requests.RequestException("private upstream detail"))
    def test_chat_reports_upstream_failure_without_details(self, _mock_get):
        response = self.client.post("/chat", json={"message": "How can I save water?"})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("private upstream detail", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
