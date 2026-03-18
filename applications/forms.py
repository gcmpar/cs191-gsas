from django.forms import ModelForm, widgets
from applicants.models import Application, Applicant

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['applicant', 'application_number', 'application_status', 'date_applied', 'program', 'folder_link', 'study_load', 'notes']
        widgets = {
            'applicant':          widgets.Select(attrs={'class': 'form-select'}),
            'application_number': widgets.TextInput(attrs={'class': 'form-control'}),
            'application_status': widgets.Select(attrs={'class': 'form-select'}),
            'date_applied':       widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'program':            widgets.Select(attrs={'class': 'form-select'}),
            'folder_link':        widgets.TextInput(attrs={'class': 'form-control'}),
            'study_load':         widgets.Select(attrs={'class': 'form-select'}),
            'notes':              widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['applicant'].queryset = Applicant.objects.all()
        self.fields['applicant'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"