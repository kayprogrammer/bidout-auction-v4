from rest_framework.test import APITestCase
from apps.accounts.auth import Authentication
from apps.accounts.models import Jwt, Otp

from apps.common.utils import TestUtil
from unittest import mock

from apps.listings.models import WatchList


class TestListings(APITestCase):
    listings_url = "/api/v4/listings/"
    listing_detail_url = "/api/v4/listings/detail/"
    watchlist_url = "/api/v4/listings/watchlist/"
    categories_url = "/api/v4/listings/categories/"
    category_listings_url = "/api/v4/categories/"
    maxDiff = None

    def setUp(self):
        verified_user = TestUtil.verified_user()
        self.verified_user = verified_user
        self.listing = TestUtil.create_listing(verified_user)["listing"]
        self.auth_token = TestUtil.auth_token(verified_user)

    def test_retrieve_all_listings(self):
        # Verify that all listings are retrieved successfully
        response = self.client.get(self.listings_url)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Listings fetched")
        data = result["data"]
        self.assertGreater(len(data), 0)
        self.assertTrue(any(isinstance(obj["name"], str) for obj in data))

    def test_retrieve_particular_listng(self):
        listing = self.listing
        # Verify that a particular listing retrieval fails with an invalid slug
        response = self.client.get(f"{self.listing_detail_url}invalid_slug/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "Listing does not exist!",
            },
        )

        # Verify that a particular listing is retrieved successfully
        response = self.client.get(f"{self.listing_detail_url}{listing.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Listing details fetched",
                "data": {
                    "listing": {
                        "auctioneer": mock.ANY,
                        "name": listing.name,
                        "slug": listing.slug,
                        "desc": listing.desc,
                        "category": "TestCategory",
                        "price": mock.ANY,
                        "closing_date": mock.ANY,
                        "active": True,
                        "bids_count": 0,
                        "highest_bid": "0.00",
                        "time_left_seconds": mock.ANY,
                        "image": mock.ANY,
                        "watchlist": False,
                    },
                    "related_listings": [],
                },
            },
        )

    def test_get_user_watchlists_listng(self):
        listing = self.listing
        user_id = self.verified_user.id

        WatchList.objects.create(user_id=user_id, listing_id=listing.id)
        bearer = {"HTTP_AUTHORIZATION": f"Bearer {self.auth_token}"}

        response = self.client.get(self.watchlist_url, **bearer)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Watchlist Listings fetched")
        data = result["data"]
        self.assertGreater(len(data), 0)
        self.assertTrue(any(isinstance(obj["name"], str) for obj in data))

    def test_create_or_remove_user_watchlists_listng(self):
        listing = self.listing

        # Verify that the endpoint fails with an invalid slug
        bearer = {"HTTP_AUTHORIZATION": f"Bearer {self.auth_token}"}
        response = self.client.post(
            self.watchlist_url, data={"slug": "invalid_slug"}, **bearer
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "Listing does not exist!",
            },
        )

        # Verify that the watchlist was created successfully
        response = self.client.post(
            self.watchlist_url, data={"slug": listing.slug}, **bearer
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Listing added to user watchlist",
                "data": {"guestuser_id": None},
            },
        )
