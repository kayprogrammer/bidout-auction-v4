from django.db.models import Q
from typing import Optional
from rest_framework import serializers

from asgiref.sync import sync_to_async

from apps.listings.models import WatchList


class ListingSerializer(serializers.Serializer):
    auctioneer = serializers.SerializerMethodField()
    name = serializers.CharField()
    slug = serializers.SlugField()
    desc = serializers.CharField()
    category = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    closing_date = serializers.DateTimeField()
    active = serializers.BooleanField()
    bids_count = serializers.IntegerField()
    highest_bid = serializers.DecimalField(max_digits=10, decimal_places=2)
    time_left_seconds = serializers.IntegerField()
    image = serializers.SerializerMethodField()
    watchlist = serializers.SerializerMethodField()

    def get_auctioneer(self, obj) -> dict:
        auctioneer = obj.auctioneer
        return {
            "id": auctioneer.id,
            "name": auctioneer.full_name,
            "avatar": auctioneer.get_avatar,
        }

    def get_image(self, obj) -> Optional[str]:
        return obj.get_image

    def get_watchlist(self, obj) -> bool:
        client = self.context["client"]
        watchlist_status = False
        if client:
            watchlist_status = True if len(obj.watchlist) > 0 else False
        return watchlist_status


class ListingDetailSerializer(serializers.Serializer):
    listing = ListingSerializer()
    related_listings = ListingSerializer(many=True)


class WatchlistCreateSerializer(serializers.Serializer):
    slug = serializers.SlugField()


class BidDataSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def get_user(self, obj):
        return {"name": obj.user.full_name, "avatar": obj.user.get_avatar}


class BidSerializer(serializers.Serializer):
    listing = serializers.CharField()
    bids = BidDataSerializer(many=True)
