from django.urls import path
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.courses_search, name='search'),
    path('add/', views.course_add, name='add'),
    path('<int:course_id>/', views.course_view, name='view'),
    path('<int:course_id>/edit/', views.course_edit, name='edit'),
    path('<int:course_id>/delete/', views.course_delete, name='delete'),
]