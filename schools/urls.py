from django.urls import path
from . import views

app_name = 'schools'
urlpatterns = [
    path('', views.schools_search, name='search'),
    path('add/', views.school_add, name='add'),
    path('<int:school_id>/', views.school_view, name='view'),
    path('<int:school_id>/edit/', views.school_edit, name='edit'),
    path('<int:school_id>/delete/', views.school_delete, name='delete'),
]