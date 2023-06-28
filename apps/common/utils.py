from django.utils import timezone
from rest_framework.permissions import BasePermission
from apps.accounts.auth import Authentication
from apps.accounts.models import User, Jwt
from apps.listings.models import Category, Listing
from apps.common.models import File
from apps.common.exceptions import RequestError

from datetime import timedelta
from uuid import UUID


class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        http_auth = request.META.get("HTTP_AUTHORIZATION")
        if not http_auth:
            raise RequestError(err_msg="Auth Bearer not provided!", status_code=401)
        user = Authentication.decodeAuthorization(http_auth)
        if not user:
            raise RequestError(
                err_msg="Auth token invalid or expired!", status_code=401
            )
        request.user = user
        if request.user and request.user.is_authenticated:
            return True
        return False


def is_uuid(value):
    try:
        return str(UUID(value))
    except:
        return None


# Test Utils
class TestUtil:
    def new_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Name",
            "email": "test@example.com",
        }
        user = User(**user_dict)
        user.set_password("testpassword")
        user.save()
        return user

    def verified_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Verified",
            "email": "testverifieduser@example.com",
            "is_email_verified": True,
        }
        user = User(**user_dict)
        user.set_password("testpassword")
        user.save()
        return user

    def another_verified_user():
        create_user_dict = {
            "first_name": "AnotherTest",
            "last_name": "UserVerified",
            "email": "anothertestverifieduser@example.com",
            "is_email_verified": True,
        }
        user = User(**create_user_dict)
        user.set_password("anothertestverifieduser123")
        user.save()
        return user

    async def authorized_client(verified_user, client):
        access = await Authentication.create_access_token(
            {"user_id": str(verified_user.id)}
        )
        refresh = await Authentication.create_refresh_token()
        await Jwt.objects.acreate(
            user_id=verified_user.id, access=access, refresh=refresh
        )
        client.headers = {**client.headers, "Authorization": f"Bearer {access}"}
        return client

    async def create_listing(verified_user):
        # Create Category
        category = await Category.objects.acreate(name="TestCategory")

        # Create File
        file = await File.objects.acreate(resource_type="image/jpeg")

        # Create Listing
        listing_dict = {
            "auctioneer_id": verified_user.id,
            "name": "New Listing",
            "desc": "New description",
            "category_id": category.id,
            "price": 1000.00,
            "closing_date": timezone.now() + timedelta(days=1),
            "image_id": file.id,
        }
        listing = await Listing.objects.acreate(**listing_dict)
        return {"user": verified_user, "listing": listing, "category": category}
