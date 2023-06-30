from django.db.models import Q
from typing import Optional
from rest_framework import serializers

from apps.listings.models import Listing

class ListingSerializer(serializers.Serializer):
    auctioneer = serializers.SerializerMethodField()
    name = serializers.CharField()
    slug = serializers.SlugField()
    desc = serializers.CharField()
    category = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    highest_bid = serializers.DecimalField(max_digits=10, decimal_places=2)
    bids_count = serializers.IntegerField()
    closing_date = serializers.DateTimeField()
    active = serializers.BooleanField()
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
            watchlist_status = Listing.objects.filter(slug="aaa").first()
        return watchlist_status


class ListingDetailSerializer(serializers.Serializer):
    listing = ListingSerializer()
    related_listings = ListingSerializer(many=True)


class WatchlistCreateSerializer(serializers.Serializer):
    slug = serializers.SlugField()