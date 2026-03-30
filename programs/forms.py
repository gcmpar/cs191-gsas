from django.forms import ModelForm, widgets
from schools.models import School
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