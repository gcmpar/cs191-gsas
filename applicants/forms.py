from django.forms import ModelForm, widgets
from . import models

class ApplicantForm(ModelForm):
    class Meta:
        model = models.Applicant
        fields = ['first_name', 'middle_name', 'last_name', 'applicant_status', 'email', 'contact_number', 'notes']
        widgets = {
            'first_name':       widgets.TextInput(attrs={'class': 'form-control'}),
            'middle_name':      widgets.TextInput(attrs={'class': 'form-control'}),
            'last_name':        widgets.TextInput(attrs={'class': 'form-control'}),
            'applicant_status': widgets.Select(attrs={'class': 'form-select'}),
            'email':            widgets.TextInput(attrs={'class': 'form-control'}),
            'contact_number':   widgets.TextInput(attrs={'class': 'form-control'}),
            'notes':            widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ApplicationForm(ModelForm):
    class Meta:
        model = models.Application
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