from adrf.views import APIView
from apps.accounts.emails import Util

from apps.accounts.models import Otp, User
from .serializers import RegisterSerializer, ResendOtpSerializer, VerifyOtpSerializer
from drf_spectacular.utils import extend_schema
from apps.common.responses import CustomResponse

from apps.common.exceptions import RequestError


class RegisterView(APIView):
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="Register a new user",
        description="This endpoint registers new users into our application",
    )
    async def post(self, request):
        # Check for existing user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        existing_user = await User.objects.get_or_none(email=data["email"])
        if existing_user:
            raise RequestError(
                err_msg="Invalid Entry",
                status_code=422,
                data={"email": "Email already registered!"},
            )

        # Create user
        user = await User.objects.create_user(**data)

        # Send verification email
        await Util.send_activation_otp(user)

        return CustomResponse.success(
            message="Registration successful",
            data={"email": data["email"]},
            status_code=201,
        )


class VerifyEmailView(APIView):
    serializer_class = VerifyOtpSerializer

    @extend_schema(
        summary="Verify a user's email",
        description="This endpoint verifies a user's email",
    )
    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp_code = serializer.validated_data["otp"]

        user = await User.objects.get_or_none(email=email)

        if not user:
            raise RequestError(err_msg="Incorrect Email", status_code=404)

        if user.is_email_verified:
            return CustomResponse.success(message="Email already verified")

        otp = await Otp.objects.get_or_none(user=user)
        if not otp or otp.code != otp_code:
            raise RequestError(err_msg="Incorrect Otp", status_code=404)
        if otp.check_expiration():
            raise RequestError(err_msg="Expired Otp")

        user.is_email_verified = True
        await user.asave()
        await otp.adelete()

        # Send welcome email
        Util.welcome_email(user)
        return CustomResponse.success(
            message="Account verification successful", status_code=200
        )


class ResendVerificationEmailView(APIView):
    serializer_class = ResendOtpSerializer

    @extend_schema(
        summary="Resend Verification Email",
        description="This endpoint resends new otp to the user's email",
    )
    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = await User.objects.get_or_none(email=email)
        if not user:
            raise RequestError(err_msg="Incorrect Email", status_code=404)
        if user.is_email_verified:
            return CustomResponse.success(message="Email already verified")

        # Send verification email
        await Util.send_activation_otp(user)
        return CustomResponse.success(
            message="Verification email sent", status_code=200
        )


# class SendPasswordResetOtpView(Controller):
#     path = "/send-password-reset-otp"

#     @post(
#         summary="Send Password Reset Otp",
#         description="This endpoint sends new password reset otp to the user's email",
#         status_code=200,
#     )
#     async def send_password_reset_otp(
#         self, data: RequestOtpSchema, db: AsyncSession
#     ) -> ResponseSchema:
#         user_by_email = await user_manager.get_by_email(db, data.email)
#         if not user_by_email:
#             raise RequestError(err_msg="Incorrect Email", status_code=404)

#         # Send password reset email
#         await send_email(db, user_by_email, "reset")

#         return ResponseSchema(message="Password otp sent")


# class SetNewPasswordView(Controller):
#     path = "/set-new-password"

#     @post(
#         summary="Set New Password",
#         description="This endpoint verifies the password reset otp",
#         status_code=200,
#     )
#     async def set_new_password(
#         self, data: SetNewPasswordSchema, db: AsyncSession
#     ) -> ResponseSchema:
#         email = data.email
#         otp_code = data.otp
#         password = data.password

#         user_by_email = await user_manager.get_by_email(db, email)
#         if not user_by_email:
#             raise RequestError(err_msg="Incorrect Email", status_code=404)

#         otp = await otp_manager.get_by_user_id(db, user_by_email.id)
#         if not otp or otp.code != otp_code:
#             raise RequestError(err_msg="Incorrect Otp", status_code=404)

#         if otp.check_expiration():
#             raise RequestError(err_msg="Expired Otp")

#         await user_manager.update(db, user_by_email, {"password": password})

#         # Send password reset success email
#         await send_email(db, user_by_email, "reset-success")

#         return ResponseSchema(message="Password reset successful")


# class LoginView(Controller):
#     path = "/login"

#     @post(
#         summary="Login a user",
#         description="This endpoint generates new access and refresh tokens for authentication",
#     )
#     async def login(
#         self,
#         data: LoginUserSchema,
#         client: Optional[Union["User", "GuestUser"]],
#         db: AsyncSession,
#     ) -> TokensResponseSchema:
#         email = data.email
#         plain_password = data.password
#         user = await user_manager.get_by_email(db, email)
#         if not user or verify_password(plain_password, user.password) == False:
#             raise RequestError(err_msg="Invalid credentials", status_code=401)

#         if not user.is_email_verified:
#             raise RequestError(err_msg="Verify your email first", status_code=401)
#         await jwt_manager.delete_by_user_id(db, user.id)

#         # Create tokens and store in jwt model
#         access = await Authentication.create_access_token({"user_id": str(user.id)})
#         refresh = await Authentication.create_refresh_token()
#         await jwt_manager.create(
#             db, {"user_id": user.id, "access": access, "refresh": refresh}
#         )

#         # Move all guest user watchlists to the authenticated user watchlists
#         guest_user_watchlists = await watchlist_manager.get_by_session_key(
#             db, client.id if client else None, user.id
#         )
#         if len(guest_user_watchlists) > 0:
#             data_to_create = [
#                 {"user_id": user.id, "listing_id": listing_id}.copy()
#                 for listing_id in guest_user_watchlists
#             ]
#             await watchlist_manager.bulk_create(db, data_to_create)

#         if isinstance(client, GuestUser):
#             # Delete client (Almost like clearing sessions)
#             await guestuser_manager.delete(db, client)

#         return TokensResponseSchema(
#             message="Login successful", data={"access": access, "refresh": refresh}
#         )


# class RefreshTokensView(Controller):
#     path = "/refresh"

#     @post(
#         summary="Refresh tokens",
#         description="This endpoint refresh tokens by generating new access and refresh tokens for a user",
#     )
#     async def refresh(
#         self, data: RefreshTokensSchema, db: AsyncSession
#     ) -> TokensResponseSchema:
#         token = data.refresh
#         jwt = await jwt_manager.get_by_refresh(db, token)
#         if not jwt:
#             raise RequestError(err_msg="Refresh token does not exist", status_code=404)
#         if not await Authentication.decode_jwt(token):
#             raise RequestError(
#                 err_msg="Refresh token is invalid or expired", status_code=401
#             )

#         access = await Authentication.create_access_token({"user_id": str(jwt.user_id)})
#         refresh = await Authentication.create_refresh_token()

#         await jwt_manager.update(db, jwt, {"access": access, "refresh": refresh})

#         return TokensResponseSchema(
#             message="Tokens refresh successful",
#             data={"access": access, "refresh": refresh},
#         )


# class LogoutView(Controller):
#     path = "/logout"

#     @get(
#         summary="Logout a user",
#         description="This endpoint logs a user out from our application",
#     )
#     async def logout(self, user: User, db: AsyncSession) -> ResponseSchema:
#         await jwt_manager.delete_by_user_id(db, user.id)
#         return ResponseSchema(message="Logout successful")


# auth_handlers = [
#     RegisterView,
#     VerifyEmailView,
#     ResendVerificationEmailView,
#     SendPasswordResetOtpView,
#     SetNewPasswordView,
#     LoginView,
#     RefreshTokensView,
#     LogoutView,
# ]
