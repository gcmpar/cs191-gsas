from gsas.admin import admin_site
from django.urls import path, include

urlpatterns = [
    path('admin/', admin_site.urls),
    path('accounts/', include('accounts.urls')),
    path('applicants/', include('applicants.urls')),
    path('applications/', include('applications.urls')),
]