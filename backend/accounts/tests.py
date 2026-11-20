from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

@override_settings(CACHES={
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "auth-throttle-tests",
    },
})

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
        self.assertEqual(response.data["user"], {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
        })
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
