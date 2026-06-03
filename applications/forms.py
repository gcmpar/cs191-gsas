from django.forms import ModelForm, Form, ModelChoiceField, MultipleChoiceField, DateInput, CharField, inlineformset_factory, TextInput, BooleanField, HiddenInput, CheckboxInput
from django_select2.forms import Select2Widget, Select2MultipleWidget
from .models import Application, ApplicationTranscript
from applicants.forms import ApplicantsWidget
from courses.forms import CoursesWidget, FlatCoursesWidget
from courses.models import Course
from django.forms import formset_factory


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

class ApplicationsQueryForm(Form):
    search = CharField(required=False)
    status = MultipleChoiceField(
        choices=Application.Status.choices,
        required=False,
        widget=Select2MultipleWidget(
            attrs={
                'data-placeholder': 'Status',
                'data-minimum-input-length': 0,
            },
        )
    )


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
            'grade': TextInput(
                attrs={
                    'placeholder': 'Grade',
                    'style': 'width: 10em;',
                }
            ),
        }

class PrereqMapForm(Form):
    target_course = ModelChoiceField(
        queryset=Course.objects.all(),
        required=True,
        widget=CoursesWidget(
            attrs={
                'data-placeholder': 'Select Target Course',
                'data-minimum-input-length': 0,
            }
        ),
    )

class PrereqCourseForm(Form):
    course = ModelChoiceField(
        queryset=Course.objects.none(),
        required=False,
        widget=FlatCoursesWidget(
            attrs={
                'data-placeholder': 'Select Prerequisite Course',
                'data-minimum-input-length': 0,
            }
        ),
    )
    def __init__(self, *args, application=None, **kwargs):
        super().__init__(*args, **kwargs)

        if application:
            applicant = application.applicant
            self.fields['course'].queryset = Course.objects.filter(
                applicationtranscript__application__applicant=applicant
            ).prefetch_related('programs__school').distinct()

class BatchImportRowForm(ModelForm):
    scanned_name = CharField(disabled=True, required=False)
    scanned_email = CharField(disabled=True, required=False)
    scanned_contact_number = CharField(disabled=True, required=False)

    class Meta:
        model = Application
        fields = ['application_number', 'applicant', 'program', 'study_load', 'application_status', 'notes']
        widgets = {
            'applicant': ApplicantsWidget(
                attrs={
                    'data-placeholder': 'Select Applicant...',
                    'data-minimum-input-length': 0,
                },
                select2_options={'width': '100%'},
            ),
            'program': Select2Widget(
                attrs={
                    'data-placeholder': 'Program',
                }
            ),
            'study_load': Select2Widget(
                attrs={
                    'data-placeholder': 'Study Load',
                }
            ),
            'application_status': Select2Widget(
                attrs={
                    'data-placeholder': 'Status',
                }
            ),
        }

BatchImportFormSet = formset_factory(BatchImportRowForm, extra=0)

class OCRRowForm(Form):
    include = BooleanField(required=False, initial=True)
    scanned_code = CharField(required=False, widget=HiddenInput())
    scanned_description = CharField(required=False, widget=HiddenInput())
    scanned_units = CharField(required=False, widget=HiddenInput())
    
    course = ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=CoursesWidget(
            attrs={
                'data-placeholder': 'Select course...',
                'data-minimum-input-length': 0,
            },
            select2_options={'width': '100%'}
        )
    )
    grade = CharField(
        required=False,
        widget=TextInput(attrs={'placeholder': 'Grade'})
    )

OCRFormSet = formset_factory(OCRRowForm, extra=0)