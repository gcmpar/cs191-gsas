from django.forms import ModelForm, Form, CharField, ModelChoiceField
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