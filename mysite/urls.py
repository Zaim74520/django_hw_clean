from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from employees.views import index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("employees/", include("employees.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]

# Подключение медиафайлов только в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
