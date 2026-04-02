from django.forms import ModelForm, widgets
from django_select2.forms import ModelSelect2Widget
from django.urls import reverse_lazy
from programs.models import Program
from .models import Course


COURSE_SEARCH_FIELDS = ['course_id', 'course_name', 'course_code']

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['program', 'course_code', 'course_name', 'units', 'description']
        widgets = {
            'program':     widgets.Select(attrs={'class': 'form-select'}),
            'course_code': widgets.TextInput(attrs={'class': 'form-control'}),
            'course_name': widgets.TextInput(attrs={'class': 'form-control'}),
            'units':       widgets.NumberInput(attrs={'class': 'form-control'}),
            'description': widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program'].queryset = Program.objects.select_related('school').all()
        self.fields['program'].label_from_instance = lambda obj: f"{obj.school.school_name} — {obj.program_name}"

class CoursesWidget(ModelSelect2Widget):
    model = Course
    search_fields = [f'{field}__icontains' for field in COURSE_SEARCH_FIELDS]
    data_url = reverse_lazy('courses:select2_courses_grouped')

    def get_queryset(self):
        return Course.objects.select_related('program__school').all()

    def label_from_instance(self, course):
        return f"{course.course_code} - {course.course_name}"