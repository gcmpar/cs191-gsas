from django.urls import path
from . import views

app_name = 'applicants'
urlpatterns = [
    path('', views.applicants_search, name='search'),
    path('add/', views.applicant_add, name='add'),
    path('<int:applicant_id>/', views.applicant_view, name='view'),
    path('<int:applicant_id>/edit/', views.applicant_edit, name='edit'),
    path('<int:applicant_id>/delete/', views.applicant_delete, name='delete'),
]