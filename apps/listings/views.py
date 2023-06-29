from django.db.models import Q
from adrf.views import APIView
from apps.common.exceptions import RequestError
from apps.common.models import GuestUser
from apps.common.responses import CustomResponse
from apps.common.utils import IsGuestOrAuthenticatedCustom, is_int
from .models import Listing, WatchList
from .serializers import (
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

        listings = await sync_to_async(list)(
            Listing.objects.select_related(
                "auctioneer", "auctioneer__avatar", "category", "image"
            )
        )
        quantity = is_int(request.GET.get("quantity"))
        if quantity:
            # Retrieve based on amount
            listings = listings[:quantity]
        serializer = self.serializer_class(
            listings, many=True, context={"request": request}
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
        listing = await Listing.objects.select_related(
            "auctioneer", "auctioneer__avatar", "category", "image"
        ).get_or_none(slug=kwargs.get("slug"))
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        related_listings = (
            await sync_to_async(list)(
                Listing.objects.filter(category_id=listing.category_id)
                .exclude(id=listing.id)
                .select_related("auctioneer", "auctioneer__avatar", "category", "image")
            )
        )[:3]
        serializer = self.serializer_class(
            {"listing": listing, "related_listings": related_listings},
            context={"request": request},
        )
        return CustomResponse.success(
            message="Listing details fetched", data=serializer.data
        )


class ListingsByWatchListView(APIView):
    serializer = ListingSerializer
    permission_classes = (IsGuestOrAuthenticatedCustom,)

    @extend_schema(
        summary="Retrieve all listings by users watchlist",
        description="This endpoint retrieves all listings",
    )
    async def get(self, request):
        user = request.user
        watchlists = []
        if user:
            watchlists = await sync_to_async(list)(
                WatchList.objects.filter(
                    Q(user_id=user.id) | Q(guest_id=user.id)
                ).select_related("user", "guest", "listing")
            )

        serializer_data = [
            self.serializer_class(watchlist.listing).data for watchlist in watchlists
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


# class CategoryListingsView(Controller):
#     path = "/categories"

#     @get(
#         summary="Retrieve all categories",
#         description="This endpoint retrieves all categories",
#     )
#     async def retrieve_categories(self, db: AsyncSession) -> CategoriesResponseSchema:
#         categories = await category_manager.get_all(db)
#         return CategoriesResponseSchema(message="Categories fetched", data=categories)

#     @get(
#         "/{slug:str}",
#         summary="Retrieve all listings by category",
#         description="This endpoint retrieves all listings in a particular category. Use slug 'other' for category other",
#     )
#     async def retrieve_category_listings(
#         self, slug: str, db: AsyncSession, client: Optional[Union["User", "GuestUser"]]
#     ) -> ListingsResponseSchema:
#         # listings with category 'other' have category column as null
#         category = None
#         if slug != "other":
#             category = await category_manager.get_by_slug(db, slug)
#             if not category:
#                 raise RequestError(err_msg="Invalid category", status_code=404)

#         listings = await listing_manager.get_by_category(db, category)
#         data = [
#             ListingDataSchema(
#                 watchlist=True
#                 if await watchlist_manager.get_by_client_id_and_listing_id(
#                     db, client.id if client else None, listing.id
#                 )
#                 else False,
#                 time_left_seconds=listing.time_left_seconds,
#                 **listing.dict()
#             )
#             for listing in listings
#         ]
#         return ListingsResponseSchema(message="Category Listings fetched", data=data)


# class BidsView(Controller):
#     path = "/{slug:str}/bids"

#     @get(
#         summary="Retrieve bids in a listing",
#         description="This endpoint retrieves at most 3 bids from a particular listing.",
#     )
#     async def retrieve_listing_bids(
#         self, db: AsyncSession, slug: str
#     ) -> BidsResponseSchema:
#         listing = await listing_manager.get_by_slug(db, slug)
#         if not listing:
#             raise RequestError(err_msg="Listing does not exist!", status_code=404)

#         bids = (await bid_manager.get_by_listing_id(db, listing.id))[:3]

#         data = BidsResponseDataSchema(
#             listing=listing.name,
#             bids=bids,
#         )
#         return BidsResponseSchema(message="Listing Bids fetched", data=data)

#     @post(
#         summary="Add a bid to a listing",
#         description="This endpoint adds a bid to a particular listing.",
#     )
#     async def post(
#         self, slug: str, data: CreateBidSchema, db: AsyncSession, user: User
#     ) -> BidResponseSchema:
#         listing = await listing_manager.get_by_slug(db, slug)
#         if not listing:
#             raise RequestError(err_msg="Listing does not exist!", status_code=404)

#         amount = data.amount
#         bids_count = listing.bids_count
#         if user.id == listing.auctioneer_id:
#             raise RequestError(
#                 err_msg="You cannot bid your own product!", status_code=403
#             )
#         elif not listing.active:
#             raise RequestError(err_msg="This auction is closed!", status_code=410)
#         elif listing.time_left < 1:
#             raise RequestError(
#                 err_msg="This auction is expired and closed!", status_code=410
#             )
#         elif amount < listing.price:
#             raise RequestError(
#                 err_msg="Bid amount cannot be less than the bidding price!"
#             )
#         elif amount <= listing.highest_bid:
#             raise RequestError(err_msg="Bid amount must be more than the highest bid!")

#         bid = await bid_manager.get_by_user_and_listing_id(db, user.id, listing.id)
#         if bid:
#             # Update existing bid
#             bid = await bid_manager.update(db, bid, {"amount": amount})
#         else:
#             # Create new bid
#             bids_count += 1
#             bid = await bid_manager.create(
#                 db,
#                 {"user_id": user.id, "listing_id": listing.id, "amount": amount},
#             )

#         await listing_manager.update(
#             db, listing, {"highest_bid": amount, "bids_count": bids_count}
#         )
#         return BidResponseSchema(message="Bid added to listing", data=bid)


# listings_handlers = [
#     ListingsView,
#     ListingsByWatchListView,
#     CategoryListingsView,
#     BidsView,
# ]
