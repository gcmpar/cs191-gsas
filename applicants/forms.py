from django_select2.forms import Select2Widget
from django.forms import ModelForm, Form, CharField, ChoiceField
from django_select2.forms import ModelSelect2Widget
from .models import Applicant


APPLICANT_SEARCH_FIELDS = ['applicant_id', 'first_name', 'middle_name', 'last_name']
class ApplicantForm(ModelForm):
    class Meta:
        model = Applicant
        fields = ['first_name', 'middle_name', 'last_name', 'applicant_status', 'email', 'contact_number', 'notes']
        widgets = {
            'applicant_status': Select2Widget(
                attrs={
                    'data-placeholder': 'Applicant Status',
                }
            ),
        }

class ApplicantsFilterForm(Form):
    search = CharField(required=False)
    status = ChoiceField(
        choices=Applicant.Status.choices,
        required=False,
        widget=Select2Widget(attrs={'data-placeholder': 'Filter by Status'})
    )

class ApplicantsWidget(ModelSelect2Widget):
    model = Applicant
    search_fields = [f'{field}__icontains' for field in APPLICANT_SEARCH_FIELDS]

    def label_from_instance(self, applicant):
        return f'(#{applicant.applicant_id}) {applicant.first_name} {applicant.middle_name} {applicant.last_name}'