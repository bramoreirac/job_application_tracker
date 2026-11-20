from rest_framework import serializers
from .models import Application
from urllib.parse import urlsplit


class ApplicationSerializer(serializers.ModelSerializer):
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

        errors = {
            field: "This field is controlled by the server"
            for field in self.Meta.read_only_fields
            if field in data
        }

        if errors:
            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)

    def validate_job_url(self, value):
        if value and urlsplit(value).scheme.lower() not in ("http", "https"):
            raise serializers.ValidationError("Use an HTTP or HTTPS URL.")

        return value
