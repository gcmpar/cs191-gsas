from django.urls import path
from . import views

app_name = 'applications'
urlpatterns = [
    path('', views.applications_search, name='search'),
    path('export/', views.applications_export, name='export'),
    path('add/', views.application_add, name='add'),
    
    # Restructured application pages
    path('<int:application_id>/', views.application_general_view, name='general_view'),
    path('<int:application_id>/edit/', views.application_general_edit, name='general_edit'),
    
    path('<int:application_id>/transcripts/', views.application_transcripts_view, name='transcripts_view'),
    path('<int:application_id>/transcripts/edit/', views.application_transcripts_edit, name='transcripts_edit'),
    
    path('<int:application_id>/prereq/', views.application_prereq_view, name='prereq_view'),
    path('<int:application_id>/prereq/edit/', views.application_prereq_edit, name='prereq_edit'),
    
    path('<int:application_id>/delete/', views.application_delete, name='delete'),
    
    # Transcript OCR and TOR
    path('<int:application_id>/transcripts/scan-tor/', views.application_scan_tor, name='scan_tor'),
    path('<int:application_id>/transcripts/ocr-preview/', views.application_ocr_preview, name='ocr_preview'),
    
    # Partial HTMX endpoints
    path('partials/transcript_form/<int:application_id>/', views.application_transcript_form, name='partial_transcript_form'),
    path('partials/prereq_map/<int:application_id>/', views.application_prereq_map, name='partial_prereq_map'),
    path('partials/prereq_form/<int:map_id>/', views.application_prereq_form, name='partial_prereq_form'),
    path('partials/prereq_detect_equiv/<int:map_id>/', views.application_prereq_detect_equiv, name='partial_prereq_detect_equiv'),
    path('partials/prereq_detect_similar/<int:map_id>/', views.application_prereq_detect_similar, name='partial_prereq_detect_similar'),
    
    # Batch actions
    path('batch-imports/', views.batch_import_history, name='batch_import_history'),
    path('batch-imports/upload/', views.batch_import_upload, name='batch_import_upload'),
    path('batch-imports/confirm/', views.batch_import_confirm, name='batch_import_confirm'),
    path('batch-imports/<int:import_id>/', views.batch_import_detail, name='batch_import_detail'),
]