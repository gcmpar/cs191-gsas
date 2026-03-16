from django.forms import ModelForm, widgets
from applicants.models import Application

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['application_number', 'application_status', 'date_applied', 'program', 'folder_link', 'study_load', 'notes']
        widgets = {
            'application_number': widgets.TextInput(attrs={'class': 'form-control'}),
            'application_status': widgets.Select(attrs={'class': 'form-select'}),
            'date_applied':       widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'program':            widgets.Select(attrs={'class': 'form-select'}),
            'folder_link':        widgets.TextInput(attrs={'class': 'form-control'}),
            'study_load':         widgets.Select(attrs={'class': 'form-select'}),
            'notes':              widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }