from django.urls import path
from . import views

app_name = 'applications'
urlpatterns = [
    path('', views.applications_search, name='search'),
    path('add/', views.application_add, name='add'),
    path('<int:application_id>/', views.application_view, name='view'),
    path('<int:application_id>/edit/', views.application_edit, name='edit'),
    path('<int:application_id>/delete/', views.application_delete, name='delete'),
    path('<int:application_id>/scan-tor/', views.application_scan_tor, name='scan_tor'),
    path('<int:application_id>/ocr-preview/', views.application_ocr_preview, name='ocr_preview'),
    path('<int:application_id>/save-mapping/', views.application_save_mapping, name='save_mapping'),
    path('<int:application_id>/load-mapping/', views.application_load_mapping, name='load_mapping'),
    path('<int:application_id>/remove-mapping/', views.application_remove_mapping, name='remove_mapping'),
    path('batch-imports/', views.batch_import_history, name='batch_import_history'),
    path('batch-imports/upload/', views.batch_import_upload, name='batch_import_upload'),
    path('batch-imports/confirm/', views.batch_import_confirm, name='batch_import_confirm'),
    path('batch-imports/<int:import_id>/', views.batch_import_detail, name='batch_import_detail'),
]