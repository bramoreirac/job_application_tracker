from django.test import SimpleTestCase
from .serializers import ApplicationSerializer


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
