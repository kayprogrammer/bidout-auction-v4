from rest_framework.test import APITestCase

from apps.general.models import Review
from apps.common.utils import TestUtil
from unittest import mock


class TestGeneral(APITestCase):
    sitedetail_url = "/api/v4/general/site-detail/"
    subscriber_url = "/api/v4/general/subscribe/"
    reviews_url = "/api/v4/general/reviews/"

    def setUp(self):
        verified_user = TestUtil.verified_user()
        review_dict = {
            "reviewer_id": verified_user.id,
            "show": True,
            "text": "This is a nice new platform",
        }
        review = Review.objects.create(**review_dict)
        self.review = review

    def test_retrieve_sitedetail(self):
        response = self.client.get(self.sitedetail_url)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Site Details fetched")
        keys = ["name", "email", "phone", "address", "fb", "tw", "wh", "ig"]
        self.assertTrue(all(item in result["data"] for item in keys))

    def test_subscribe(self):
        # Check response validity
        response = self.client.post(
            self.subscriber_url, {"email": "test_subscriber@example.com"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Subscription successful",
                "data": {"email": "test_subscriber@example.com"},
            },
        )

    def test_retrieve_reviews(self):
        # Check response validity
        response = self.client.get(self.reviews_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Reviews fetched",
                "data": [{"reviewer": mock.ANY, "text": "This is a nice new platform"}],
            },
        )
