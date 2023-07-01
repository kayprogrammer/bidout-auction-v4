from typing import Optional
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.common.file_processors import FileProcessor
from apps.common.file_types import ALLOWED_IMAGE_TYPES
import pytz


class ProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        max_length=50, error_messages={"max_length": _("{max_length} characters max.")}
    )
    last_name = serializers.CharField(
        max_length=50, error_messages={"max_length": _("{max_length} characters max.")}
    )
    file_type = serializers.CharField(write_only=True, required=False)
    file_upload_data = serializers.SerializerMethodField()

    def validate(self, attrs):
        first_name = attrs["first_name"]
        last_name = attrs["last_name"]
        file_type = attrs.get("file_type")

        if len(first_name.split(" ")) > 1:
            raise serializers.ValidationError({"first_name": "No spacing allowed"})

        if len(last_name.split(" ")) > 1:
            raise serializers.ValidationError({"last_name": "No spacing allowed"})

        if file_type and not file_type in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError({"file_type": "Image type not allowed!"})
        return attrs

    def get_file_upload_data(self, obj) -> Optional[dict]:
        avatar_id = obj.avatar_id
        if avatar_id:
            return FileProcessor.generate_file_signature(
                key=avatar_id,
                folder="avatars",
            )
        return None


class ListingCreateResponseSerializer(serializers.Serializer):
    auctioneer = serializers.SerializerMethodField()
    name = serializers.CharField()
    slug = serializers.SlugField()
    desc = serializers.CharField()
    category = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    closing_date = serializers.DateTimeField(default_timezone=pytz.timezone("UTC"))
    active = serializers.BooleanField(read_only=True)
    bids_count = serializers.IntegerField(read_only=True)
    file_upload_data = serializers.SerializerMethodField()

    def get_auctioneer(self, obj) -> dict:
        auctioneer = obj.auctioneer
        return {
            "id": auctioneer.id,
            "name": auctioneer.full_name,
            "avatar": auctioneer.get_avatar,
        }

    def get_file_upload_data(self, obj) -> dict:
        return FileProcessor.generate_file_signature(
            key=obj.image_id,
            folder="listings",
        )
