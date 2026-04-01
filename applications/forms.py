from django.forms import ModelForm, DateInput
from .models import Application
from applicants.models import Applicant


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['applicant', 'application_number', 'application_status', 'date_applied', 'program', 'folder_link', 'study_load', 'notes']
        widgets = {
            'date_applied': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['applicant'].queryset = Applicant.objects.all()
        self.fields['applicant'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"