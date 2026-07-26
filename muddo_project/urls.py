from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('', include('apps.products.urls')),
    path('', include('apps.distributors.urls')),
    path('', include('apps.agents.urls')),
    path('', include('apps.requests_app.urls')),
    path('', include('apps.messaging.urls')),
    path('admin-panel/', include('apps.analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
