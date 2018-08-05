from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include(('political_profile.core.urls', 'core'), namespace='core')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.insert(0, url(r'^__debug__/', include(debug_toolbar.urls)))
