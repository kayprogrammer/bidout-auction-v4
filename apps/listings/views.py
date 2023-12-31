from django.db.models import Prefetch, Q
from adrf.views import APIView
from apps.common.exceptions import RequestError
from apps.common.models import GuestUser
from apps.common.responses import CustomResponse
from apps.common.utils import (
    IsAuthenticatedCustom,
    IsGuestOrAuthenticatedCustom,
    is_int,
)
from .models import Bid, Category, Listing, WatchList
from .serializers import (
    BidDataSerializer,
    BidSerializer,
    ListingDetailSerializer,
    ListingSerializer,
    WatchlistCreateSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from asgiref.sync import sync_to_async


class ListingsView(APIView):
    serializer_class = ListingSerializer
    permission_classes = (IsGuestOrAuthenticatedCustom,)

    @extend_schema(
        summary="Retrieve all listings",
        description="This endpoint retrieves all listings",
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
            Listing.objects.select_related(
                "auctioneer", "auctioneer__avatar", "category", "image"
            ).prefetch_related(
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
        return CustomResponse.success(message="Listings fetched", data=serializer.data)


class ListingDetailView(APIView):
    serializer_class = ListingDetailSerializer
    permission_classes = (IsGuestOrAuthenticatedCustom,)

    @extend_schema(
        summary="Retrieve listing's detail",
        description="This endpoint retrieves detail of a listing",
    )
    async def get(self, request, *args, **kwargs):
        client = request.user
        prefetch_query = Prefetch(
            "watchlists",
            queryset=WatchList.objects.filter(
                Q(user_id=client.id if client else None)
                | Q(guest_id=client.id if client else None)
            ),
            to_attr="watchlist",
        )
        listing = (
            await Listing.objects.select_related(
                "auctioneer", "auctioneer__avatar", "category", "image"
            )
            .prefetch_related(prefetch_query)
            .get_or_none(slug=kwargs.get("slug"))
        )
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        related_listings = (
            await sync_to_async(list)(
                Listing.objects.filter(category_id=listing.category_id)
                .exclude(id=listing.id)
                .select_related("auctioneer", "auctioneer__avatar", "category", "image")
                .prefetch_related(prefetch_query)
            )
        )[:3]

        serializer = self.serializer_class(
            {"listing": listing, "related_listings": related_listings},
            context={"client": client},
        )
        return CustomResponse.success(
            message="Listing details fetched", data=serializer.data
        )


class ListingsByWatchListView(APIView):
    serializer_class = ListingSerializer
    permission_classes = (IsGuestOrAuthenticatedCustom,)

    @extend_schema(
        summary="Retrieve all listings by users watchlist",
        description="This endpoint retrieves all listings",
    )
    async def get(self, request):
        client = request.user
        watchlists = []
        if client:
            watchlists = await sync_to_async(list)(
                WatchList.objects.filter(Q(user_id=client.id) | Q(guest_id=client.id))
                .select_related(
                    "user",
                    "guest",
                    "listing",
                    "listing__auctioneer",
                    "listing__auctioneer__avatar",
                    "listing__category",
                    "listing__image",
                )
                .prefetch_related(
                    Prefetch(
                        "listing__watchlists",
                        queryset=WatchList.objects.filter(
                            Q(user_id=client.id if client else None)
                            | Q(guest_id=client.id if client else None)
                        ),
                        to_attr="watchlist",
                    )
                )
            )
        serializer_data = [
            self.serializer_class(watchlist.listing, context={"client": client}).data
            for watchlist in watchlists
        ]
        return CustomResponse.success(
            message="Watchlist Listings fetched", data=serializer_data
        )

    @extend_schema(
        summary="Add or Remove listing from a users watchlist",
        description="""
        This endpoint adds or removes a listing from a user's watchlist, authenticated or not....
        As a guest, ensure to store guestuser_id in localstorage and keep passing it to header 'guestuserid' in subsequent requests
        """,
        request=WatchlistCreateSerializer,
    )
    async def post(self, request):
        client = request.user

        serializer = WatchlistCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        listing = await Listing.objects.get_or_none(
            slug=serializer.validated_data["slug"]
        )
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        if not client:
            client = await GuestUser.objects.acreate()

        resp_message = "Listing added to user watchlist"
        status_code = 201
        if hasattr(client, "email"):
            watchlist, created = await WatchList.objects.aget_or_create(
                listing_id=listing.id, user_id=client.id
            )
            if not created:
                await watchlist.adelete()
                resp_message = "Listing removed from user watchlist"
                status_code = 200
        else:
            watchlist, created = await WatchList.objects.aget_or_create(
                listing_id=listing.id, guest_id=client.id
            )
            if not created:
                await watchlist.adelete()
                resp_message = "Listing removed from user watchlist"
                status_code = 200

        guestuser_id = client.id if isinstance(client, GuestUser) else None
        return CustomResponse.success(
            message=resp_message,
            data={"guestuser_id": guestuser_id},
            status_code=status_code,
        )


class CategoriesView(APIView):
    @extend_schema(
        summary="Retrieve all categories",
        description="This endpoint retrieves all categories",
    )
    async def get(self, request):
        categories = await sync_to_async(list)(Category.objects.values("name", "slug"))
        return CustomResponse.success(message="Categories fetched", data=categories)


class CategoryListingsView(APIView):
    serializer_class = ListingSerializer
    permission_classes = (IsGuestOrAuthenticatedCustom,)

    @extend_schema(
        summary="Retrieve all listings by category",
        description="This endpoint retrieves all listings in a particular category. Use slug 'other' for category other",
    )
    async def get(self, request, *args, **kwargs):
        client = request.user
        slug = kwargs.get("slug")

        # listings with category 'other' have category column as null
        category = None
        if slug != "other":
            category = await Category.objects.get_or_none(slug=slug)
            if not category:
                raise RequestError(err_msg="Invalid category", status_code=404)

        listings = await sync_to_async(list)(
            Listing.objects.filter(category=category)
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
        serializer = self.serializer_class(
            listings, many=True, context={"client": client}
        )
        return CustomResponse.success(
            message="Category Listings fetched", data=serializer.data
        )


class BidsView(APIView):
    serializer_class = BidSerializer

    @extend_schema(
        summary="Retrieve bids in a listing",
        description="This endpoint retrieves at most 3 bids from a particular listing.",
    )
    async def get(self, request, *args, **kwargs):
        listing = (
            await Listing.objects.select_related(
                "auctioneer", "auctioneer__avatar", "category", "image"
            )
            .prefetch_related(
                Prefetch(
                    "bids",
                    queryset=Bid.objects.select_related("user", "user__avatar"),
                    to_attr="all_bids",
                )
            )
            .get_or_none(slug=kwargs.get("slug"))
        )
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        bids = listing.all_bids[:3]
        serializer = self.serializer_class({"listing": listing.name, "bids": bids})
        return CustomResponse.success(
            message="Listing Bids fetched", data=serializer.data
        )

    @extend_schema(
        summary="Add a bid to a listing",
        description="This endpoint adds a bid to a particular listing.",
        request=BidDataSerializer,
    )
    async def post(self, request, *args, **kwargs):
        user = request.user

        listing = (
            await Listing.objects.select_related(
                "auctioneer", "auctioneer__avatar", "category", "image"
            )
            .prefetch_related("bids")
            .get_or_none(slug=kwargs.get("slug"))
        )
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        serializer = BidDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]

        bids_count = listing.bids_count
        if user.id == listing.auctioneer_id:
            raise RequestError(
                err_msg="You cannot bid your own product!", status_code=403
            )
        elif not listing.active:
            raise RequestError(err_msg="This auction is closed!", status_code=410)
        elif listing.time_left < 1:
            raise RequestError(
                err_msg="This auction is expired and closed!", status_code=410
            )
        elif amount < listing.price:
            raise RequestError(
                err_msg="Bid amount cannot be less than the bidding price!"
            )
        elif amount <= listing.highest_bid:
            raise RequestError(err_msg="Bid amount must be more than the highest bid!")

        bid = await Bid.objects.select_related("user", "user__avatar").get_or_none(
            user_id=user.id, listing_id=listing.id
        )
        if bid:
            # Update existing bid
            bid.amount = amount
            await bid.asave()
        else:
            # Create new bid
            bids_count += 1
            bid = await Bid.objects.acreate(user=user, listing=listing, amount=amount)
        listing.bids_count = bids_count
        listing.highest_bid = amount
        await listing.asave()
        serializer = BidDataSerializer(bid)
        return CustomResponse.success(
            message="Bid added to listing", data=serializer.data, status_code=201
        )

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticatedCustom(),
            ]
        return []
