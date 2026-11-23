from django.test import SimpleTestCase
from .serializers import ApplicationSerializer
from .models import Application
from datetime import date, timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone


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

    def test_calculate_tomorrow_managua(self):

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