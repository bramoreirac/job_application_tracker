from django.test import SimpleTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from .serializers import ApplicationSerializer
from .models import Application
from datetime import date, timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone
from datetime import datetime, timezone as datetime_timezone
from unittest.mock import patch


class ApplicationSerializerTests(SimpleTestCase):
    def test_rejects_unsupported_fields(self):
        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "salary": 50000,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("salary", serializer.errors)

    def test_rejects_server_controlled_fields(self):
        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "id": "client-supplied",
                "owner": 999,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("id", serializer.errors)
        self.assertIn("owner", serializer.errors)

    def test_rejects_only_spaces_text_fields(self):
        serializer = ApplicationSerializer(data={"company": "   ", "role": "   "})

        self.assertFalse(serializer.is_valid())
        self.assertIn("company", serializer.errors)
        self.assertIn("role", serializer.errors)

    def test_valid_text_is_trimmed(self):
        serializer = ApplicationSerializer(
            data={
                "company": "  Example Company  ",
                "role": "  Developer  ",
                "location": "  Remote  ",
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["company"], "Example Company")
        self.assertEqual(serializer.validated_data["role"], "Developer")
        self.assertEqual(serializer.validated_data["location"], "Remote")

    def test_rejects_invalid_job_url(self):
        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "job_url": "ftp://example.com/job",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("job_url", serializer.errors)

    def test_accepts_http_https_and_blank_job_urls(self):
        for url in ("http://example.com/job", "https://example.com/job", ""):
            with self.subTest(job_url=url):
                serializer = ApplicationSerializer(
                    data={
                        "company": "Example Company",
                        "role": "Developer",
                        "job_url": url,
                    }
                )

                self.assertTrue(serializer.is_valid(), serializer.errors)
                self.assertEqual(serializer.validated_data["job_url"], url)

    def test_accepts_omitted_job_url(self):
        serializer = ApplicationSerializer(
            data={"company": "Example Company", "role": "Developer"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_notes_accept_2000_characters(self):
        notes = "x" * 2000
        serializer = ApplicationSerializer(
            data={"company": "Example Company", "role": "Developer", "notes": notes}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["notes"], notes)

    def test_notes_reject_more_than_2000_characters(self):
        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "notes": "x" * 2001,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("notes", serializer.errors)

    def test_status_and_application_date_rule(self):
        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "status": "saved",
                "applied_on": "2026-01-01",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("applied_on", serializer.errors)

    def test_rejects_saved_then_patch_date_only(self):
        application = Application(
            company="Example Company",
            role="Developer",
            status="saved",
            applied_on=None,
        )

        serializer = ApplicationSerializer(
            instance=application,
            data={"applied_on": "2026-01-01"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("applied_on", serializer.errors)

    def test_rejects_patch_to_saved_without_clearing_date(self):
        application = Application(
            company="Example Company",
            role="Developer",
            status="applied",
            applied_on=date(2026, 1, 1),
        )

        serializer = ApplicationSerializer(
            instance=application,
            data={"status": "saved"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("applied_on", serializer.errors)

    def test_accepts_patch_to_saved_with_none_date(self):
        application = Application(
            company="Example Company",
            role="Developer",
            status="applied",
            applied_on=date(2026, 1, 1),
        )

        serializer = ApplicationSerializer(
            instance=application,
            data={"status": "saved", "applied_on": None},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["applied_on"], None)

    def test_rejects_saved_to_applied_without_date(self):
        application = Application(
            company="Example Company",
            role="Developer",
            status="saved",
            applied_on=None,
        )

        serializer = ApplicationSerializer(
            instance=application,
            data={"status": "applied"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("applied_on", serializer.errors)

    def test_accepts_saved_to_applied_with_date(self):
        application = Application(
            company="Example Company",
            role="Developer",
            status="saved",
            applied_on=None,
        )
        serializer = ApplicationSerializer(
            instance=application,
            data={"status": "applied", "applied_on": "2026-01-01"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["status"], "applied")
        self.assertEqual(serializer.validated_data["applied_on"], date(2026, 1, 1))

    def test_rejects_applied_date_tomorrow_managua(self):

        tomorrow = timezone.now().astimezone(
            ZoneInfo("America/Managua")
        ).date() + timedelta(days=1)

        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "status": "applied",
                "applied_on": tomorrow.isoformat(),
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("applied_on", serializer.errors)

    @patch("applications.serializers.timezone.now")
    def test_accepts_applied_date_today_managua(self, mock_now):
        mock_now.return_value = datetime(2026, 1, 2, 3, 0, tzinfo=datetime_timezone.utc)

        today = timezone.now().astimezone(ZoneInfo("America/Managua")).date()

        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "status": "applied",
                "applied_on": today.isoformat(),
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertIn("applied_on", serializer.validated_data)
        self.assertEqual(today, date(2026, 1, 1))

    def test_rejects_invalid_status_and_work_mode(self):
        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "status": "unknown",
                "work_mode": "spaceship",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)
        self.assertIn("work_mode", serializer.errors)

    def test_accepts_interviewing_without_application_date(self):
        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "status": "interviewing",
                "applied_on": None,
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["applied_on"], None)

    def test_partial_company_update_omits_unchanged_fields(self):
        application = Application(
            status="applied",
            applied_on=date(2026, 1, 1),
        )

        serializer = ApplicationSerializer(
            instance=application,
            data={"company": "Updated Company"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["company"], "Updated Company")
        self.assertNotIn("status", serializer.validated_data)
        self.assertNotIn("applied_on", serializer.validated_data)

    def test_rejects_date_when_status_defaults_to_saved(self):
        serializer = ApplicationSerializer(
            data={
                "company": "Example Company",
                "role": "Developer",
                "applied_on": "2026-01-01",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("applied_on", serializer.errors)


class ApplicationAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="application_test",
            password="Synthetic-test-passphrase-123!",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("application-list-create")

    def test_create_assigns_authenticated_user_as_owner(self):
        response = self.client.post(
            self.url,
            {"company": "Example Company", "role": "Developer"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        application = Application.objects.get(pk=response.data["id"])
        self.assertEqual(application.owner, self.user)

    def test_list_returns_only_authenticated_users_applications(self):
        other_user = get_user_model().objects.create_user(
            username="other_user",
            password="Synthetic-test-passphrase-456!",
        )

        own_application = Application.objects.create(
            owner=self.user,
            company="My Company",
            role="Developer",
        )

        Application.objects.create(
            owner=other_user,
            company="Other Company",
            role="Designer",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(own_application.id))

    def test_list_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_create_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            {"company": "Example Company", "role": "Developer"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Application.objects.count(), 0)

    def test_create_rejects_client_supplied_owner(self):
        other_user = get_user_model().objects.create_user(
            username="other_user",
            password="Synthetic-test-passphrase-456!",
        )

        response = self.client.post(
            self.url,
            {"company": "Example Company", "role": "Developer", "owner": other_user.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Application.objects.count(), 0)
        self.assertIn("owner", response.data)

    def test_retrieve_own_application(self):
        application = Application.objects.create(
            owner=self.user,
            company="My Company",
            role="Developer",
        )
        url = reverse("application-detail", kwargs={"pk": application.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(application.id))
        self.assertEqual(response.data["company"], "My Company")
