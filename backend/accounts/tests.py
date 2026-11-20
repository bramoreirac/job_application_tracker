from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "auth-throttle-tests",
        },
    }
)
class AuthenticationThrottleTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_login_and_registration_share_limit(self):
        for i in range(10):
            if i < 5:
                response = self.client.post("/api/auth/register/", {}, format="json")
                self.assertEqual(response.status_code, 400)
            else:
                response = self.client.post("/api/auth/login/", {}, format="json")
                self.assertEqual(response.status_code, 401)

        response = self.client.post("/api/auth/login/", {}, format="json")
        self.assertEqual(response.status_code, 429)


class LoginContractTests(APITestCase):
    def setUp(self):
        self.password = "Synthetic-test-passphrase-732!"
        self.user = get_user_model().objects.create_user(
            username="login_contract_test",
            email="login@example.com",
            password=self.password,
        )
        self.url = reverse("login")

    def test_success_returns_token_and_public_user(self):
        response = self.client.post(
            self.url,
            {"username": self.user.username, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {"token", "user"})
        self.assertEqual(
            response.data["user"],
            {
                "id": self.user.id,
                "username": self.user.username,
                "email": self.user.email,
            },
        )
        self.assertTrue(
            Token.objects.filter(user=self.user, key=response.data["token"]).exists()
        )

    def test_invalid_credentials_return_same_generic_401(self):
        wrong_password = self.client.post(
            self.url,
            {"username": self.user.username, "password": "incorrect"},
            format="json",
        )
        unknown_user = self.client.post(
            self.url,
            {"username": "unknown_login_user", "password": "incorrect"},
            format="json",
        )

        for response in (wrong_password, unknown_user):
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data, {"detail": "Invalid credentials"})
            self.assertEqual(response["WWW-Authenticate"], "Token")


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="logout_test", password="Synthetic-test-passphrase-723!"
        )
        self.token = Token.objects.create(user=self.user)

    def test_logout_invalidates_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 204)

        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, 401)


class RegisterTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.username = "register_test"
        self.password = "Synthetic-test-passphrase-723!"

    def test_registration_creates_user_and_returns_public_fields(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": self.username,
                "password": self.password,
                "password_confirm": self.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(username=self.username)
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(
            response.data,
            {"id": user.id, "username": self.username, "email": ""},
        )

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": self.username,
                "password": self.password,
                "password_confirm": "Synthetic-test-passphrase-227!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("password_confirm", response.data)
        self.assertFalse(
            get_user_model().objects.filter(username=self.username).exists()
        )

    def test_registration_rejects_weak_password(self):
        weak_password = "123"
        response = self.client.post(
            reverse("register"),
            {
                "username": self.username,
                "password": weak_password,
                "password_confirm": weak_password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)
        self.assertFalse(
            get_user_model().objects.filter(username=self.username).exists()
        )


class CurrentUserTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_request_without_token(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, 401)

    def test_request_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid-token")

        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, 401)
