from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
import debug_toolbar

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("admin/", admin.site.urls),
    # path("api/v4/accounts/", include("apps.accounts.urls")),
    path("api/v4/general/", include("apps.general.urls")),
    # path("api/v4/listings/", include("apps.listings.urls")),
    # path("api/v4/auctioneer/", include("apps.auctioneer.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
