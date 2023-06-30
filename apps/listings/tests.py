from rest_framework.test import APITestCase
from apps.accounts.auth import Authentication
from apps.accounts.models import Jwt, Otp

from apps.common.utils import TestUtil
from unittest import mock


class TestListings(APITestCase):
    listings_url = "/api/v4/listings/"
    listing_detail_url = "/api/v4/listings/detail/"
    watchlist_url = "/api/v4/listings/watchlist/"
    categories_url = "/api/v4/listings/categories/"
    category_listings_url = "/api/v4/categories/"

    def setUp(self):
        verified_user = TestUtil.verified_user()
        listing = TestUtil.create_listing(verified_user)

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
