from django.urls import path
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.courses_search, name='search'),
    path('add/', views.course_add, name='add'),
    
    # Restructured course pages
    path('<int:course_id>/', views.course_general_view, name='view'),
    path('<int:course_id>/edit/', views.course_general_edit, name='edit'),
    
    path('<int:course_id>/equiv/', views.course_equiv_view, name='equiv_view'),
    path('<int:course_id>/equiv/edit/', views.course_equiv_edit, name='equiv_edit'),
    path('<int:course_id>/equiv/delete/<int:map_id>/', views.delete_equivalence_map, name='delete_equivalence'),
    
    path('<int:course_id>/delete/', views.course_delete, name='delete'),

    path('select2_courses_grouped/', views.CoursesGroupedAutoResponseView.as_view(), name='select2_courses_grouped'),
]