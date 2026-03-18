from django.urls import path
from . import views

app_name = 'programs'
urlpatterns = [
    path('', views.programs_search, name='search'),
    path('add/', views.program_add, name='add'),
    path('<int:program_id>/', views.program_view, name='view'),
    path('<int:program_id>/edit/', views.program_edit, name='edit'),
    path('<int:program_id>/delete/', views.program_delete, name='delete'),
]