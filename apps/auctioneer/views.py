from django.db.models import Prefetch, Q
from adrf.views import APIView
from apps.common.exceptions import RequestError
from apps.common.models import File
from apps.common.responses import CustomResponse
from apps.common.utils import (
    IsAuthenticatedCustom,
    is_int,
)
from apps.listings.models import Bid, Category, Listing, WatchList
from apps.listings.serializers import BidSerializer, ListingSerializer
from .serializers import (
    ListingCreateResponseSerializer,
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
            file = user.avatar
            if not file:
                file = await File.objects.acreate(resource_type=file_type)
            data.update({"avatar": file})
            data.pop("file_type")
        for attr, value in data.items():
            setattr(user, attr, value)
        await user.asave()
        serializer = self.serializer_class(user)
        return CustomResponse.success(message="User updated!", data=serializer.data)


class AuctioneerListingsView(APIView):
    serializer_class = ListingSerializer
    permission_classes = (IsAuthenticatedCustom,)

    @extend_schema(
        summary="Retrieve all listings by the current user",
        description="This endpoint retrieves all listings by the current user",
        parameters=[
            OpenApiParameter(
                name="quantity",
                description="Retrieve a certain amount",
                required=False,
                type=int,
            )
        ],
    )
    async def get(self, request):
        client = request.user
        listings = await sync_to_async(list)(
            Listing.objects.filter(auctioneer=client)
            .select_related("auctioneer", "auctioneer__avatar", "category", "image")
            .prefetch_related(
                Prefetch(
                    "watchlists",
                    queryset=WatchList.objects.filter(
                        Q(user_id=client.id if client else None)
                        | Q(guest_id=client.id if client else None)
                    ),
                    to_attr="watchlist",
                )
            )
        )
        quantity = is_int(request.GET.get("quantity"))
        if quantity:
            # Retrieve based on amount
            listings = listings[:quantity]
        serializer = self.serializer_class(
            listings, many=True, context={"client": client}
        )
        return CustomResponse.success(
            message="Auctioneer Listings fetched", data=serializer.data
        )

    @extend_schema(
        summary="Create a listing",
        description="This endpoint creates a new listing. Note: Use the returned file_upload_data to upload image to cloudinary",
    )
    async def post(self, request):
        client = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        category = data["category"]

        if not category == "other":
            category = await Category.objects.get_or_none(slug=category)
            if not category:
                # Return a data validation error
                raise RequestError(
                    err_msg="Invalid entry",
                    data={"category": "Invalid category"},
                    status_code=422,
                )
        else:
            category = None

        data.update(
            {
                "auctioneer": client,
                "category": category,
            }
        )

        # Create file object
        file = await File.objects.acreate(resource_type=data["file_type"])
        data.update({"image": file})
        data.pop("file_type")
        listing = await Listing.objects.acreate(**data)

        serializer = ListingCreateResponseSerializer(listing)
        return CustomResponse.success(
            message="Listing created successfully",
            data=serializer.data,
            status_code=201,
        )


class UpdateListingView(APIView):
    serializer_class = ListingSerializer
    permission_classes = (IsAuthenticatedCustom,)

    @extend_schema(
        summary="Update a listing",
        description="This endpoint update a particular listing. Do note that only file type is optional.",
    )
    async def put(self, request, *args, **kwargs):
        client = request.user
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        category = data.get("category")

        listing = await Listing.objects.select_related(
            "auctioneer", "auctioneer__avatar", "category", "image"
        ).get_or_none(slug=kwargs.get("slug"))
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        if client != listing.auctioneer:
            raise RequestError(err_msg="This listing doesn't belong to you!")

        # Remove keys with values of None
        data = {k: v for k, v in data.items() if v not in (None, "")}

        if category:
            if not category == "other":
                category = await Category.objects.get_or_none(slug=category)
                if not category:
                    # Return a data validation error
                    raise RequestError(
                        err_msg="Invalid entry",
                        data={"category": "Invalid category"},
                        status_code=422,
                    )
            else:
                category = None

            data["category"] = category

        file_type = data.get("file_type")
        if file_type:
            file = listing.image
            if not file:
                file = await File.objects.acreate(resource_type=file_type)
            data.update({"image_id": file.id})
        data.pop("file_type", None)

        for attr, value in data.items():
            setattr(listing, attr, value)
        await listing.asave()
        serializer = ListingCreateResponseSerializer(listing)
        return CustomResponse.success(
            message="Listing updated successfully", data=serializer.data
        )


class AuctioneerListingBids(APIView):
    serializer_class = BidSerializer
    permission_classes = (IsAuthenticatedCustom,)

    @extend_schema(
        summary="Retrieve all bids in a listing (current user)",
        description="This endpoint retrieves all bids in a particular listing by the current user.",
    )
    async def get(self, request, *args, **kwargs):
        user = request.user
        # Get listing by slug
        listing = (
            await Listing.objects.select_related(
                "auctioneer", "auctioneer__avatar", "category", "image"
            )
            .prefetch_related("bids", "bids__user")
            .get_or_none(slug=kwargs.get("slug"))
        )
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        # Ensure the current user is the listing's owner
        if user.id != listing.auctioneer_id:
            raise RequestError(err_msg="This listing doesn't belong to you!")

        bids = listing.bids.all()
        serializer = self.serializer_class({"listing": listing.name, "bids": bids})
        return CustomResponse.success(
            message="Listing Bids fetched", data=serializer.data
        )
