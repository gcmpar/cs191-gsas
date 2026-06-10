from django_select2.forms import ModelSelect2Widget
from django.forms import ModelForm, Form, CharField, ModelChoiceField
from django.urls import reverse_lazy, reverse
from schools.models import School
from schools.forms import SchoolsWidget
from .models import Program

class ProgramForm(ModelForm):
    class Meta:
        model = Program
        fields = ['school', 'program_name', 'description', 'notes']
        widgets = {
            'school': SchoolsWidget(
                attrs={
                    'data-placeholder': 'School',
                    'data-minimum-input-length': 1
                }
            ),
        }

class ProgramsQueryForm(Form):
    search = CharField(required=False)
    school = ModelChoiceField(
        queryset=School.objects.all(),
        required=False,
        widget=SchoolsWidget(
            attrs={
                'data-placeholder': 'Filter by School',
                'data-minimum-input-length': 1
            }
        )
    )

class RelatedCoursesQueryForm(Form):
    search = CharField(required=False)

class RelatedAppsQueryForm(Form):
    search = CharField(required=False)

class ProgramsWidget(ModelSelect2Widget):
    model = Program
    search_fields = ['program_name__icontains', 'school__school_name__icontains']
    data_url = reverse_lazy('programs:select2_programs_grouped')

    def __init__(self, *args, school=None, **kwargs):
        self.school = school
        super().__init__(*args, **kwargs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        
        if self.school is not None:
            base_url = reverse('programs:select2_programs_grouped')
            attrs['data-ajax--url'] = f"{base_url}?school={self.school.school_id}"
        
        return attrs

    def label_from_instance(self, program):
        return f"{program.program_name}"