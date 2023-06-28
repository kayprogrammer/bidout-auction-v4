from rest_framework.test import APITestCase
from apps.accounts.auth import Authentication
from apps.accounts.models import Jwt, Otp

from apps.common.utils import TestUtil
from unittest import mock


class TestAccounts(APITestCase):
    register_url = "/api/v4/auth/register/"
    verify_email_url = "/api/v4/auth/verify-email/"
    resend_verification_email_url = "/api/v4/auth/resend-verification-email/"
    send_password_reset_otp_url = "/api/v4/auth/send-password-reset-otp/"
    set_new_password_url = "/api/v4/auth/set-new-password/"
    login_url = "/api/v4/auth/login/"
    refresh_url = "/api/v4/auth/refresh/"
    logout_url = "/api/v4/auth/logout/"

    def setUp(self):
        self.new_user = TestUtil.new_user()
        self.verified_user = TestUtil.verified_user()

    def test_register(self):
        email = "testregisteruser@example.com"
        password = "testregisteruserpassword"
        user_in = {
            "first_name": "Testregister",
            "last_name": "User",
            "email": email,
            "password": password,
            "terms_agreement": True,
        }

        # Verify that a new user can be registered successfully
        mock.patch("apps.accounts.emails.Util", new="")
        response = self.client.post(self.register_url, user_in)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Registration successful",
                "data": {"email": user_in["email"]},
            },
        )

        # Verify that a user with the same email cannot be registered again
        mock.patch("apps.accounts.emails.Util", new="")
        response = self.client.post(self.register_url, user_in)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "Invalid Entry",
                "data": {"email": "Email already registered!"},
            },
        )

    def test_verify_email(self):
        new_user = self.new_user
        otp = "111111"
        # Verify that the email verification fails with an invalid otp
        response = self.client.post(
            self.verify_email_url, {"email": new_user.email, "otp": otp}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(), {"status": "failure", "message": "Incorrect Otp"}
        )

        # Verify that the email verification succeeds with a valid otp
        otp = Otp.objects.create(user_id=new_user.id, code=otp)
        mock.patch("apps.accounts.emails.Util", new="")
        response = self.client.post(
            self.verify_email_url,
            {"email": new_user.email, "otp": otp.code},
        )
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "success", "message": "Account verification successful"},
        )

    def test_resend_verification_email(self):
        new_user = self.new_user
        user_in = {"email": new_user.email}

        # Verify that an unverified user can get a new email
        mock.patch("apps.accounts.emails.Util", new="")
        # Then, attempt to resend the verification email
        response = self.client.post(self.resend_verification_email_url, user_in)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"status": "success", "message": "Verification email sent"}
        )

        # Verify that a verified user cannot get a new email
        new_user.is_email_verified = True
        new_user.save()
        mock.patch("apps.accounts.emails.Util", new="")
        response = self.client.post(
            self.resend_verification_email_url,
            {"email": new_user.email},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"status": "success", "message": "Email already verified"}
        )

        # Verify that an error is raised when attempting to resend the verification email for a user that doesn't exist
        mock.patch("apps.accounts.emails.Util", new="")
        response = self.client.post(
            self.resend_verification_email_url,
            {"email": "invalid@example.com"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(), {"status": "failure", "message": "Incorrect Email"}
        )

    def test_login(self):
        new_user = self.new_user

        # Test for invalid credentials
        response = self.client.post(
            self.login_url,
            {"email": "invalid@email.com", "password": "invalidpassword"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(), {"status": "failure", "message": "Invalid credentials"}
        )

        # Test for unverified credentials (email)
        response = self.client.post(
            self.login_url,
            {"email": new_user.email, "password": "testpassword"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(), {"status": "failure", "message": "Verify your email first"}
        )

        # Test for valid credentials and verified email address
        new_user.is_email_verified = True
        new_user.save()
        response = self.client.post(
            self.login_url,
            {"email": new_user.email, "password": "testpassword"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Login successful",
                "data": {"access": mock.ANY, "refresh": mock.ANY},
            },
        )

    def test_refresh_token(self):
        verified_user = self.verified_user

        jwt_obj = Jwt.objects.create(
            user_id=verified_user.id,
            access="access",
            refresh="refresh",
        )

        # Test for invalid refresh token (not found)
        response = self.client.post(
            self.refresh_url, {"refresh": "invalid_refresh_token"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"status": "failure", "message": "Refresh token does not exist"},
        )

        # Test for invalid refresh token (invalid or expired)
        response = self.client.post(self.refresh_url, {"refresh": jwt_obj.refresh})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"status": "failure", "message": "Refresh token is invalid or expired"},
        )

        # Test for valid refresh token
        refresh = Authentication.create_refresh_token()
        jwt_obj.refresh = refresh
        jwt_obj.save()
        mock.patch("apps.accounts.auth.Authentication.decode_jwt", return_value=True)
        response = self.client.post(self.refresh_url, {"refresh": jwt_obj.refresh})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Tokens refresh successful",
                "data": {"access": mock.ANY, "refresh": mock.ANY},
            },
        )
