from django_select2.forms import Select2Widget
from django.forms import ModelForm, Form, CharField, ChoiceField, widgets
from .models import School

class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['school_name']
        widgets = {
            'school_name': widgets.TextInput(attrs={'class': 'form-control'}),
        }

class SchoolsFilterForm(Form):
    search = CharField(required=False)