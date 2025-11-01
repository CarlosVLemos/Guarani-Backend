from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic.base import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# URLs da API - Agrupadas para melhor organização
api_urlpatterns = [
    # Redireciona a raiz da API para a documentação do Swagger
    path("", RedirectView.as_view(url="/api/schema/swagger-ui/", permanent=False), name="api-root-redirect"),

    # apps
    path("projects/", include("projects.urls")),
    path("users/", include("users.urls")),
    path("marketplace/", include("marketplace.urls")),

    # Rotas da documentação (Swagger/ReDoc)
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

urlpatterns = [
    # Redireciona a raiz do projeto para a documentação do Swagger
    path("", RedirectView.as_view(url="/api/schema/swagger-ui/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)