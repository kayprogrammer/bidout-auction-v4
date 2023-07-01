from django.utils import timezone
from rest_framework.test import APITestCase
from apps.accounts.auth import Authentication
from apps.accounts.models import Jwt

from apps.common.utils import TestUtil
from apps.listings.models import Bid, Category
from unittest import mock
from datetime import timedelta


class TestAuctioneer(APITestCase):
    profile_url = "/api/v4/auctioneer/"
    listings_url = "/api/v4/auctioneer/listings/"

    def setUp(self):
        verified_user = TestUtil.verified_user()
        auth_token = TestUtil.auth_token(verified_user)
        self.bearer = {"HTTP_AUTHORIZATION": f"Bearer {auth_token}"}
        self.verified_user = verified_user
        self.listing = TestUtil.create_listing(verified_user)["listing"]

    def test_profile_view(self):
        verified_user = self.verified_user
        response = self.client.get(self.profile_url, **self.bearer)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "User details fetched!",
                "data": {
                    "first_name": verified_user.first_name,
                    "last_name": verified_user.last_name,
                    "avatar": mock.ANY,
                },
            },
        )

    def test_profile_update(self):
        user_dict = {
            "first_name": "VerifiedUser",
            "last_name": "Update",
            "file_type": "image/jpeg",
        }
        response = self.client.put(self.profile_url, data=user_dict, **self.bearer)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "User updated!",
                "data": {
                    "first_name": "VerifiedUser",
                    "last_name": "Update",
                    "file_upload_data": mock.ANY,
                },
            },
        )

    def test_auctioneer_retrieve_listings(self):
        # Verify that all listings by a particular auctioneer is fetched
        response = self.client.get(self.listings_url, **self.bearer)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Auctioneer Listings fetched")
        data = result["data"]
        self.assertGreater(len(data), 0)
        self.assertTrue(any(isinstance(obj["name"], str) for obj in data))

    def test_auctioneer_create_listings(self):
        # Create Category
        Category.objects.create(name="Test Category")
        listing_dict = {
            "name": "Test Listing",
            "desc": "Test description",
            "category": "test-category",
            "price": 1000.00,
            "closing_date": timezone.now() + timedelta(days=1),
            "file_type": "image/jpeg",
        }

        # Verify that create listing succeeds with a valid category
        response = self.client.post(self.listings_url, data=listing_dict, **self.bearer)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Listing created successfully",
                "data": {
                    "name": "Test Listing",
                    "auctioneer": mock.ANY,
                    "slug": "test-listing",
                    "desc": "Test description",
                    "category": "Test Category",
                    "price": "1000.00",
                    "closing_date": mock.ANY,
                    "active": True,
                    "bids_count": 0,
                    "file_upload_data": mock.ANY,
                },
            },
        )

        # Verify that create listing failed with invalid category
        listing_dict.update({"category": "invalidcategory"})
        response = self.client.post(self.listings_url, data=listing_dict, **self.bearer)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "Invalid entry",
                "data": {"category": "Invalid category"},
            },
        )

    def test_auctioneer_update_listing(self):
        listing = self.listing

        listing_dict = {
            "name": "Test Listing Updated",
            "desc": "Test description Updated",
            "category": "invalidcategory",
            "price": 2000.00,
            "closing_date": timezone.now() + timedelta(days=1),
            "file_type": "image/png",
        }

        # Verify that update listing failed with invalid listing slug
        response = self.client.put(
            f"{self.listings_url}invalid_slug/", data=listing_dict, **self.bearer
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "Listing does not exist!",
            },
        )

        # Verify that update listing failed with invalid category
        response = self.client.put(
            f"{self.listings_url}{listing.slug}/", data=listing_dict, **self.bearer
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "Invalid entry",
                "data": {"category": "Invalid category"},
            },
        )

        # Verify that update listing succeeds with a valid category
        listing_dict.update({"category": "testcategory"})
        response = self.client.put(
            f"{self.listings_url}{listing.slug}/", data=listing_dict, **self.bearer
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Listing updated successfully",
                "data": {
                    "name": "Test Listing Updated",
                    "auctioneer": mock.ANY,
                    "slug": "test-listing-updated",
                    "desc": "Test description Updated",
                    "category": "TestCategory",
                    "price": "2000.00",
                    "closing_date": mock.ANY,
                    "active": True,
                    "bids_count": 0,
                    "file_upload_data": mock.ANY,
                },
            },
        )

        # You can also test for invalid users yourself.....

    def test_auctioneer_listings_bids(self):
        listing = self.listing
        another_verified_user = TestUtil.another_verified_user()

        # Create Bid
        Bid.objects.create(user=another_verified_user, listing=listing, amount=5000.00)

        # Verify that auctioneer listing bids retrieval succeeds with a valid slug and owner
        response = self.client.get(
            f"{self.listings_url}{listing.slug}/bids/", **self.bearer
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Listing Bids fetched")
        data = result["data"]
        self.assertTrue(isinstance(data["listing"], str))

        # Verify that the auctioneer listing bids retrieval failed with invalid listing slug
        response = self.client.get(
            f"{self.listings_url}invalid_slug/bids/", **self.bearer
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "Listing does not exist!",
            },
        )

        # Verify that the auctioneer listing bids retrieval failed with invalid owner
        access = Authentication.create_access_token(
            {"user_id": str(another_verified_user.id)}
        )
        refresh = Authentication.create_refresh_token()
        Jwt.objects.create(
            user_id=another_verified_user.id, access=access, refresh=refresh
        )

        bearer = {"HTTP_AUTHORIZATION": f"Bearer {access}"}
        response = self.client.get(f"{self.listings_url}{listing.slug}/bids/", **bearer)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "message": "This listing doesn't belong to you!",
            },
        )
