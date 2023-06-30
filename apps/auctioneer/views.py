from django.db.models import Prefetch, Q
from adrf.views import APIView
from apps.common.exceptions import RequestError
from apps.common.models import File
from apps.common.responses import CustomResponse
from apps.common.utils import (
    IsAuthenticatedCustom,
)
from apps.listings.models import Bid, Category, Listing, WatchList
from .serializers import (
    ProfileSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from asgiref.sync import sync_to_async


class ProfileView(APIView):
    permission_classes = (IsAuthenticatedCustom,)
    serializer_class = ProfileSerializer

    @extend_schema(
        summary="Get Profile",
        description="This endpoint gets the current user's profile.",
    )
    async def get(self, request):
        user = request.user
        user = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar": user.get_avatar,
        }
        return CustomResponse.success(message="User details fetched!", data=user)

    @extend_schema(
        summary="Update Profile",
        description="This endpoint updates an authenticated user's profile. Note: use the returned upload_url to upload avatar to cloudinary",
    )
    async def put(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        file_type = data.get("file_type")
        if file_type:
            # Create file object
            file = await File.objects.acreate(resource_type=file_type)
            data.update({"avatar": file})
            data.pop("file_type")
        for attr, value in data.items():
            setattr(user, attr, value)
        await user.asave()
        serializer = self.serializer_class(user)
        return CustomResponse.success(message="User updated!", data=serializer.data)
