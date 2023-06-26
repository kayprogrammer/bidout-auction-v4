from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        max_length=50, error_messages={"max_length": _("{max_length} characters max.")}
    )
    last_name = serializers.CharField(
        max_length=50, error_messages={"max_length": _("{max_length} characters max.")}
    )
    email = serializers.EmailField()
    password = serializers.CharField(
        min_length=8, error_messages={"min_length": _("{min_length} characters max.")}
    )
    terms_agreement = serializers.BooleanField()

    def validate(self, attrs):
        first_name = attrs["first_name"]
        last_name = attrs["last_name"]
        terms_agreement = attrs["terms_agreement"]

        if len(first_name.split(" ")) > 1:
            raise serializers.ValidationError({"first_name": "No spacing allowed"})

        if len(last_name.split(" ")) > 1:
            raise serializers.ValidationError({"last_name": "No spacing allowed"})

        if terms_agreement != True:
            raise serializers.ValidationError(
                {"terms_agreement": "You must agree to terms and conditions"}
            )
        return attrs


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()


class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
