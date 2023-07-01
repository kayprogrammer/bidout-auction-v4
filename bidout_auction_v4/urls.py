from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from drf_spectacular.utils import extend_schema
from adrf.views import APIView
import debug_toolbar

from apps.common.responses import CustomResponse


class HealthCheckView(APIView):
    @extend_schema(
        "/",
        summary="API Health Check",
        description="This endpoint checks the health of the API",
    )
    async def get(self, request):
        return CustomResponse.success(message="pong")


urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("admin/", admin.site.urls),
    path("api/v4/auth/", include("apps.accounts.urls")),
    path("api/v4/general/", include("apps.general.urls")),
    path("api/v4/listings/", include("apps.listings.urls")),
    path("api/v4/auctioneer/", include("apps.auctioneer.urls")),
    path("api/v4/healthcheck/", HealthCheckView.as_view()),
    path("__debug__/", include(debug_toolbar.urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
