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

# NOTE: previously this only ran `if settings.DEBUG`, which meant uploaded
# media (product photos, chat attachments) 404'd in production — Django
# never served /media/ at all with DEBUG=False. Serving media through
# Django isn't ideal at real scale, but for this app's traffic it's the
# simplest fix and matches how STATIC is already served via Whitenoise.
# Remember: Render's free-tier filesystem is ephemeral, so uploaded files
# can still be wiped on the next deploy/restart — a persistent disk or
# S3-backed storage (django-storages) is the real long-term fix.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
