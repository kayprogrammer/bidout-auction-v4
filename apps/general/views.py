from adrf.views import APIView
from drf_spectacular.utils import extend_schema
from apps.common.responses import CustomResponse

from apps.general.models import Review, SiteDetail, Subscriber
from apps.general.serializers import (
    ReviewsSerializer,
    SiteDetailSerializer,
    SubscriberSerializer,
)
from asgiref.sync import sync_to_async


class SiteDetailView(APIView):
    serializer_class = SiteDetailSerializer

    @extend_schema(
        summary="Retrieve site details",
        description="This endpoint retrieves few details of the site/application",
    )
    async def get(self, request):
        sitedetail, created = await SiteDetail.objects.aget_or_create()
        serializer = self.serializer_class(sitedetail)
        return CustomResponse.success(
            message="Site Details fetched", data=serializer.data
        )


class SubscriberCreateView(APIView):
    serializer_class = SubscriberSerializer

    @extend_schema(
        summary="Add a subscriber",
        description="This endpoint creates a newsletter subscriber in our application",
    )
    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        await Subscriber.objects.aget_or_create(email=email)
        return CustomResponse.success(
            message="Subscription successful", data={"email": email}, status_code=201
        )


class ReviewsView(APIView):
    serializer_class = ReviewsSerializer

    @extend_schema(
        summary="Retrieve site reviews",
        description="This endpoint retrieves a few reviews of the application",
    )
    async def get(self, request):
        reviews = (
            await sync_to_async(list)(
                Review.objects.filter(show=True).select_related("reviewer")
            )
        )[:3]
        serializer = self.serializer_class(reviews, many=True)
        return CustomResponse.success(message="Reviews fetched", data=serializer.data)
