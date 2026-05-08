from django.forms import (
    ModelForm, Form, CharField, ModelChoiceField,
    formset_factory, inlineformset_factory
)
from django_select2.forms import ModelSelect2Widget
from django.urls import reverse_lazy
from .models import Course, EquivalenceMap, EquivalenceMapCourses
from schools.models import School
from schools.forms import SchoolsWidget
from programs.models import Program
from programs.forms import ProgramsWidget


COURSE_SEARCH_FIELDS = ['course_id', 'course_name', 'course_code']

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'units', 'description']

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

class ProgramRowForm(Form):
    program = ModelChoiceField(
        queryset=Program.objects.all(),
        required=False,
        widget=ProgramsWidget(
            attrs={
                'data-placeholder': 'Select associated Program',
                'data-minimum-input-length': 0,
                'name': 'programs[]'
            }
        ),
    )

# ---------------------------------------------------------------------------
# Courses Select2 widget 
# ---------------------------------------------------------------------------

class CoursesWidget(ModelSelect2Widget):
    model = Course
    search_fields = [f'{field}__icontains' for field in COURSE_SEARCH_FIELDS]
    data_url = reverse_lazy('courses:select2_courses_grouped')

    def get_queryset(self):
        return Course.objects.prefetch_related('programs__school').all()

    def label_from_instance(self, course):
        return f"{course.course_code} - {course.course_name}"

# ---------------------------------------------------------------------------
# Equivalence Mapping formsets
# ---------------------------------------------------------------------------

class EquivalenceMapCoursesForm(ModelForm):
    class Meta:
        model = EquivalenceMapCourses
        fields = ['course']
        widgets = {
            'course': CoursesWidget(attrs={
                'data-placeholder': 'Source Course',
                'data-minimum-input-length': 0,
            }),
        }

# One inline formset per existing EquivalenceMap
EquivMapInlineFormSet = inlineformset_factory(
    EquivalenceMap,
    EquivalenceMapCourses,
    form=EquivalenceMapCoursesForm,
    extra=1,
    can_delete=True,
)

class NewEquivSourceRowForm(Form):
    course = ModelChoiceField(
        queryset=Course.objects.prefetch_related('programs__school').all(),
        widget=CoursesWidget(attrs={
            'data-placeholder': 'Source Course',
            'data-minimum-input-length': 0,
        }),
        required=False,
    )

NewEquivMappingFormSet = formset_factory(NewEquivSourceRowForm, extra=1, can_delete=True)