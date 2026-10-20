from django.db import models
from django.conf import settings
import uuid


# Create your models here.

class WorkMode(models.TextChoices):
    REMOTE = "remote", "Remote"
    HYBRID = "hybrid", "Hybrid"
    ONSITE = "onsite", "On-site"

class Status(models.TextChoices):
    SAVED = "saved", "Saved"
    APPLIED = "applied", "Applied"
    INTERVIEWING = "interviewing", "Interviewing"
    OFFER = "offer", "Offer"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"

class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.CharField(null=False, max_length=120)
    role = models.CharField(null=False, max_length=160)
    job_url = models.URLField(blank=True, max_length=500)
    location = models.CharField(blank=True, max_length=120)
    notes = models.TextField(blank=True)
    work_mode = models.CharField(choices=WorkMode.choices, default=WorkMode.REMOTE, max_length=10)
    status = models.CharField(choices=Status.choices, default=Status.SAVED, max_length=14)
    applied_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["owner", "created_at"])
        ]
        ordering = ["-created_at", "-id"]