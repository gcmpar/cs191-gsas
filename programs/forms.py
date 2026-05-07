from django.forms import ModelForm, Form, CharField, ModelChoiceField, widgets
from schools.models import School
from schools.forms import SchoolsWidget
from .models import Program

class ProgramForm(ModelForm):
    class Meta:
        model = Program
        fields = ['school', 'program_name', 'description']
        widgets = {
            'school':       widgets.Select(attrs={'class': 'form-select'}),
            'program_name': widgets.TextInput(attrs={'class': 'form-control'}),
            'description':  widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show school names in the dropdown instead of the default "School object (1)"
        self.fields['school'].queryset = School.objects.all()
        self.fields['school'].label_from_instance = lambda obj: obj.school_name

class ProgramsFilterForm(Form):
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

class RelatedCoursesFilterForm(Form):
    search = CharField(required=False)

class RelatedAppsFilterForm(Form):
    search = CharField(required=False)