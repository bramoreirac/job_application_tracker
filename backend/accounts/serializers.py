from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError as DjangoValidationError

class RegisterSerializer(serializers.Serializer):
    username_validator = UnicodeUsernameValidator()

    username = serializers.CharField(max_length=150, trim_whitespace=True, validators=[username_validator])
    email = serializers.EmailField(allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})

        candidate_user = get_user_model()(
            username=attrs["username"],
            email=attrs.get("email", ""),
        )

        try:
            validate_password(password=attrs["password"], user=candidate_user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from exc

        return attrs

    def validate_username(self, value):
        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is taken.")
        return value
