from django.forms import ModelForm, widgets
from . import models

class ApplicantForm(ModelForm):
    class Meta:
        model = models.Applicant
        fields = ['first_name', 'middle_name', 'last_name', 'applicant_status', 'email', 'contact_number', 'notes']