from django.forms import ModelForm, DateInput, inlineformset_factory
from django_select2.forms import Select2Widget
from .models import Application, ApplicationTranscript
from applicants.forms import ApplicantsWidget
from courses.forms import CoursesWidget


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['applicant', 'application_number', 'application_status', 'date_applied', 'program', 'folder_link', 'study_load', 'notes']
        widgets = {
            'date_applied': DateInput(attrs={'type': 'date'}),
            'applicant': ApplicantsWidget(
                attrs={
                    'data-placeholder': 'Applicant',
                    'data-minimum-input-length': 0,
                },
                select2_options={'width': '100%'},
            ),
            'application_status': Select2Widget(
                attrs={
                    'data-placeholder': 'Application Status',
                }
            ),
            'program': Select2Widget(
                attrs={
                    'data-placeholder': 'Degree Program',
                }
            ),
            'study_load': Select2Widget(
                attrs={
                    'data-placeholder': 'Study Load',
                }
            ),
        }


class ApplicationTranscriptForm(ModelForm):
    class Meta:
        model = ApplicationTranscript
        fields = ['course', 'academic_year', 'semester', 'grade']
        widgets = {
            'course': CoursesWidget(
                attrs={
                    'data-placeholder': 'Course',
                    'data-minimum-input-length': 0,
                    'data-width': '10em',
                },
            ),
            'academic_year': Select2Widget(
                attrs={
                    'data-placeholder': 'Academic Year',
                    'data-width': '10em',
                }
            ),
            'semester': Select2Widget(
                attrs={
                    'data-placeholder': 'Semester',
                    'data-width': '10em',
                }
            ),
            'grade': Select2Widget(
                attrs={
                    'data-placeholder': 'Grade',
                    'data-width': '10em',
                }
            ),
        }

ApplicationTranscriptFormSet = inlineformset_factory(
    Application,
    ApplicationTranscript,
    form=ApplicationTranscriptForm,
    extra=1,
    can_delete=True
)