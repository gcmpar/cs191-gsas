from django.forms import (
    ModelForm, widgets, Form, ModelChoiceField,
    formset_factory, inlineformset_factory
)
from django_select2.forms import ModelSelect2Widget
from django.urls import reverse_lazy
from programs.models import Program
from .models import Course, EquivalenceMap, EquivalenceMapCourses


COURSE_SEARCH_FIELDS = ['course_id', 'course_name', 'course_code']

# ---------------------------------------------------------------------------
# Course general-info form 
# ---------------------------------------------------------------------------

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'units', 'description']
        widgets = {
            'course_code': widgets.TextInput(attrs={'class': 'form-control'}),
            'course_name': widgets.TextInput(attrs={'class': 'form-control'}),
            'units':       widgets.NumberInput(attrs={'class': 'form-control'}),
            'description': widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# ---------------------------------------------------------------------------
# Programs ACT-style formset
# ---------------------------------------------------------------------------

class ProgramsWidget(ModelSelect2Widget):
    model = Program
    search_fields = ['program_name__icontains', 'school__school_name__icontains']

    def get_queryset(self):
        return Program.objects.select_related('school').all()

    def label_from_instance(self, program):
        return f"{program.school.school_name} — {program.program_name}"

class CourseProgramRowForm(Form):
    program = ModelChoiceField(
        queryset=Program.objects.select_related('school').all(),
        widget=ProgramsWidget(attrs={
            'data-placeholder': 'Program',
            'data-minimum-input-length': 0,
        }),
        required=False,
    )

CourseProgramFormSet = formset_factory(CourseProgramRowForm, extra=1, can_delete=True)

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