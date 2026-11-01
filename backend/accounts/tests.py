from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


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
