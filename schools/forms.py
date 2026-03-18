from django.forms import ModelForm, widgets
from academics.models import School

class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['school_name']
        widgets = {
            'school_name': widgets.TextInput(attrs={'class': 'form-control'}),
        }