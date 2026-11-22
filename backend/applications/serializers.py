from collections.abc import Mapping
from urllib.parse import urlsplit

from rest_framework import serializers

from .models import Application


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
