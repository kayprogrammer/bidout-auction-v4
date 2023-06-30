from typing import Optional
from rest_framework import serializers


class ListingSerializer(serializers.Serializer):
    auctioneer = serializers.SerializerMethodField()
    name = serializers.CharField()
    slug = serializers.SlugField(read_only=True)
    desc = serializers.CharField()
    category = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    closing_date = serializers.DateTimeField()
    active = serializers.BooleanField(read_only=True)
    bids_count = serializers.IntegerField(read_only=True)
    highest_bid = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    time_left_seconds = serializers.IntegerField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    watchlist = serializers.SerializerMethodField(read_only=True)
    file_type = serializers.CharField(write_only=True)

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
