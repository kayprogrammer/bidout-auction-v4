from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from django.utils.translation import gettext_lazy as _

from typing import Optional
from rest_framework import serializers

from apps.common.file_types import ALLOWED_IMAGE_TYPES
import pytz


class ListingSerializer(serializers.Serializer):
    auctioneer = serializers.SerializerMethodField()
    name = serializers.CharField(
        max_length=70, error_messages={"max_length": _("{max_length} characters max.")}
    )
    slug = serializers.SlugField(read_only=True)
    desc = serializers.CharField()
    category = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    closing_date = serializers.DateTimeField(default_timezone=pytz.timezone("UTC"))
    active = serializers.SerializerMethodField()
    bids_count = serializers.IntegerField(read_only=True)
    highest_bid = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    time_left_seconds = serializers.IntegerField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True, default="https://img.url")
    watchlist = serializers.SerializerMethodField(read_only=True)
    file_type = serializers.CharField(write_only=True)

    def get_auctioneer(self, obj) -> dict:
        auctioneer = obj.auctioneer
        return {
            "id": auctioneer.id,
            "name": auctioneer.full_name,
            "avatar": auctioneer.get_avatar,
        }

    def get_image(self, obj) -> str:
        return obj.get_image

    def get_watchlist(self, obj) -> bool:
        client = self.context["client"]
        watchlist_status = False
        if client:
            watchlist_status = True if len(obj.watchlist) > 0 else False
        return watchlist_status

    def get_active(self, obj) -> bool:
        if obj.active and obj.time_left_seconds > 0:
            return True
        return False

    def validate_file_type(self, value):
        if value and not value in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError("Image type not allowed!")
        return value

    def validate_closing_date(self, value):
        if timezone.now() >= value:
            raise serializers.ValidationError(
                "Closing date must be beyond the current datetime!"
            )
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price should be greater than zero!")
        return value


class ListingDetailSerializer(serializers.Serializer):
    listing = ListingSerializer()
    related_listings = ListingSerializer(many=True)


class WatchlistCreateSerializer(serializers.Serializer):
    slug = serializers.SlugField()


class BidDataSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def get_user(self, obj) -> dict:
        return {"name": obj.user.full_name, "avatar": obj.user.get_avatar}


class BidSerializer(serializers.Serializer):
    listing = serializers.CharField()
    bids = BidDataSerializer(many=True)
