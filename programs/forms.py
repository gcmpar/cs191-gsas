from django_select2.forms import ModelSelect2Widget
from django.forms import ModelForm, Form, CharField, ModelChoiceField
from django.urls import reverse_lazy
from schools.models import School
from schools.forms import SchoolsWidget
from .models import Program

class ProgramForm(ModelForm):
    class Meta:
        model = Program
        fields = ['school', 'program_name', 'description']
        widgets = {
            'school': SchoolsWidget(
                attrs={
                    'data-placeholder': 'School',
                    'data-minimum-input-length': 0
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
                'data-minimum-input-length': 0
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

    def get_queryset(self):
        return Program.objects.select_related('school').all()

    def label_from_instance(self, program):
        return f"{program.program_name}"