from django.urls import path
from . import views

app_name = 'applications'
urlpatterns = [
    path('', views.applications_search, name='search'),
    path('add/', views.application_add, name='add'),
    path('<int:application_id>/', views.application_view, name='view'),
    path('<int:application_id>/edit/', views.application_edit, name='edit'),
    path('<int:application_id>/delete/', views.application_delete, name='delete'),
    path('batch-imports/', views.batch_import_history, name='batch_import_history'),
    path('batch-imports/upload/', views.batch_import_upload, name='batch_import_upload'),
    path('batch-imports/confirm/', views.batch_import_confirm, name='batch_import_confirm'),
    path('batch-imports/<int:import_id>/', views.batch_import_detail, name='batch_import_detail'),
]