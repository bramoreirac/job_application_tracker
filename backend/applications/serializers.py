from collections.abc import Mapping
from urllib.parse import urlsplit
from rest_framework import serializers
from .models import Application
from zoneinfo import ZoneInfo
from django.utils import timezone


class ApplicationSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(max_length=2000, required=False, allow_blank=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "owner",
            "company",
            "role",
            "job_url",
            "location",
            "work_mode",
            "status",
            "applied_on",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def to_internal_value(self, data):
        # Let DRF report its normal validation error for non-object input.
        if not isinstance(data, Mapping):
            return super().to_internal_value(data)

        errors = {
            field: "This field is controlled by the server"
            for field in self.Meta.read_only_fields
            if field in data
        }
        errors.update(
            {
                field: "This field is not supported."
                for field in data
                if field not in self.fields
            }
        )

        if errors:
            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)

    def validate_job_url(self, value):
        if value and urlsplit(value).scheme.lower() not in ("http", "https"):
            raise serializers.ValidationError("Use an HTTP or HTTPS URL.")

        return value

    def validate(self, attrs):
        status = attrs.get(
            "status",
            self.instance.status if self.instance else "saved",
        )
        applied_on = attrs.get(
            "applied_on",
            self.instance.applied_on if self.instance else None,
        )

        if status == "saved" and applied_on:
            raise serializers.ValidationError(
                {"applied_on": "A saved application cannot have an application date"}
            )

        if (
            self.instance
            and self.instance.status == "saved"
            and status == "applied"
            and not applied_on
        ):
            raise serializers.ValidationError(
                {"applied_on": "Provide an application date when moving to applied."}
            )

        return attrs

    def validate_applied_on(self, value):
        today = timezone.now().astimezone(ZoneInfo("America/Managua")).date()

        if value is not None and value > today:
            raise serializers.ValidationError(
                "The application date cannot be in the future."
            )

        return value