from django.urls import path
from . import views

app_name = 'applications'
urlpatterns = [
    path('', views.applications_search, name='search'),
    path('<int:application_id>/', views.application_view, name='view'),
    path('<int:application_id>/edit/', views.application_edit, name='edit'),
]