from rest_framework import serializers
from apps.common.file_processors import FileProcessor


class SiteDetailSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    address = serializers.CharField()
    fb = serializers.CharField()
    tw = serializers.CharField()
    wh = serializers.CharField()
    ig = serializers.CharField()


class SubscriberSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ReviewsSerializer(serializers.Serializer):
    reviewer = serializers.SerializerMethodField()
    text = serializers.CharField()

    def get_reviewer(self, obj):
        reviewer = obj.reviewer
        return {
            "name": reviewer.full_name,
            "avatar": reviewer.avatar,
        }
