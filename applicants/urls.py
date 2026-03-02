from django.urls import path

from . import views


app_name = 'applicants'
urlpatterns = [
    path('', views.applicants_search, name='search'),
    path('<int:applicant_id>/', views.applicant_view, name='view'),
    path('<int:applicant_id>/edit/', views.applicant_edit, name='edit'),
]
