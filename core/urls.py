from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from common import urls as common_urls
from workspace import urls as workspace_urls
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin interface
    path("admin/", admin.site.urls),
    # Schema generation and Swagger UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    # Common app URLs
    path("api/common/", include(common_urls)),
    # Auth endpoints
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    # Workspace app URLs
    path("api/workspace/", include(workspace_urls)),
    # stripe
    path("api/stripe/", include(("djstripe.urls", "djstripe"), namespace="djstripe")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
