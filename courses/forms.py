from django.forms import (
    ModelForm, Form, CharField, ModelChoiceField,
)
from django_select2.forms import ModelSelect2Widget
from django.urls import reverse_lazy, reverse
from .models import Course
from schools.models import School
from schools.forms import SchoolsWidget
from programs.models import Program
from programs.forms import ProgramsWidget


COURSE_SEARCH_FIELDS = ['course_id', 'course_name', 'course_code']

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'units', 'description', 'notes']

class CoursesQueryForm(Form):
    search = CharField(required=False)
    program = ModelChoiceField(
        queryset=Program.objects.all(),
        required=False,
        widget=ProgramsWidget(
            attrs={
                'data-placeholder': 'Filter by Program',
                'data-minimum-input-length': 0
            },
            dependent_fields={'school': 'school'}
        )
    )
    school = ModelChoiceField(
        queryset=School.objects.all(),
        required=False,
        widget=SchoolsWidget(
            attrs={
                'data-placeholder': 'Filter by School',
                'data-minimum-input-length': 0
            }
        )
    )

class CoursesWidget(ModelSelect2Widget):
    model = Course
    search_fields = [f'{field}__icontains' for field in COURSE_SEARCH_FIELDS]
    data_url = reverse_lazy('courses:select2_courses_grouped')

    def label_from_instance(self, course):
        return f"{course.course_code} - {course.course_name}"
    
class ApplicantCoursesWidget(ModelSelect2Widget):
    model = Course
    search_fields = [f'{field}__icontains' for field in COURSE_SEARCH_FIELDS]
    data_url = reverse_lazy('courses:select2_courses_grouped')

    def __init__(self, *args, applicant=None, **kwargs):
        self.applicant = applicant
        super().__init__(*args, **kwargs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)

        base_url = reverse('courses:select2_courses_grouped')
        attrs['data-ajax--url'] = f"{base_url}?applicant={self.applicant.applicant_id if self.applicant else 'none'}"
        
        return attrs

    def label_from_instance(self, course):
        return f"{course.course_code} - {course.course_name}"


class ProgramRowForm(Form):
    program = ModelChoiceField(
        queryset=Program.objects.all(),
        required=False,
        widget=ProgramsWidget(
            attrs={
                'data-placeholder': 'Select associated Program',
                'data-minimum-input-length': 0,
            }
        ),
    )

class EquivRowForm(Form):
    course = ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=CoursesWidget(
            attrs={
                'data-placeholder': 'Select Course',
                'data-minimum-input-length': 0,
            }
        ),
    )