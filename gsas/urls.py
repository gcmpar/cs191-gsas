from gsas.admin import admin_site
from django.urls import path, include
from accounts.views import home

urlpatterns = [
    path('admin/', admin_site.urls),
    path('accounts/', include('accounts.urls')),
    path('', home, name='home'),
    path('applicants/', include('applicants.urls')),
    path('applications/', include('applications.urls')),
    path('schools/', include('schools.urls')),  
    path('programs/', include('programs.urls')),
    path('courses/', include('courses.urls')),
]