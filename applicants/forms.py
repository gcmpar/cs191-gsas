from django.forms import ModelForm
from django_select2.forms import ModelSelect2Widget
from .models import Applicant


APPLICANT_SEARCH_FIELDS = ['applicant_id', 'first_name', 'middle_name', 'last_name']

class ApplicantForm(ModelForm):
    class Meta:
        model = Applicant
        fields = ['first_name', 'middle_name', 'last_name', 'applicant_status', 'email', 'contact_number', 'notes']

class ApplicantsWidget(ModelSelect2Widget):
    model = Applicant
    search_fields = [f'{field}__icontains' for field in APPLICANT_SEARCH_FIELDS]

    def label_from_instance(self, applicant):
        return f'(#{applicant.applicant_id}) {applicant.first_name} {applicant.middle_name} {applicant.last_name}'