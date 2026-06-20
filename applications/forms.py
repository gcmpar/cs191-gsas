from django.forms import ModelForm, Form, ModelChoiceField, MultipleChoiceField, DateInput, CharField, TypedChoiceField, TextInput, BooleanField, HiddenInput, ChoiceField
from django_select2.forms import Select2Widget, Select2MultipleWidget
from .models import Application, ApplicationTranscript
from applicants.forms import ApplicantsWidget
from applicants.models import Applicant
from courses.forms import CoursesWidget, ApplicantCoursesWidget
from courses.models import Course
from django.forms import formset_factory


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = [
            'applicant', 'application_number', 'application_status', 'date_applied', 'folder_link', 'program', 'study_load',
            'unit', 'research_field_1', 'research_field_2', 'research_field_3', 'special_project_topic_interest',
            'undergraduate_gwa', 'undergraduate_failed_subjects', 'graduate_gwa', 'graduate_failed_subjects',
            'ngse_requirements_complete', 'ngse_remarks',
            'notes',
        ]
        widgets = {
            'date_applied': DateInput(attrs={'type': 'date'}),
            'applicant': ApplicantsWidget(
                attrs={
                    'data-placeholder': 'Applicant',
                    'data-minimum-input-length': 1,
                },
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
    ngse_requirements_complete = TypedChoiceField(
        choices=[
            ('null', 'Unknown'),
            ('true', 'Yes'),
            ('false', 'No'),
        ],
        coerce=lambda v: {
            'null': None,
            'true': True,
            'false': False,
        }[v],
        required=False,
        widget=Select2Widget(
            attrs={
                'data-placeholder': 'Complete?',
            }
        ),
    )

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
                    'data-minimum-input-length': 1,
                },
            ),
            'academic_year': Select2Widget(
                attrs={
                    'data-placeholder': 'Year',
                }
            ),
            'semester': Select2Widget(
                attrs={
                    'data-placeholder': 'Semester',
                }
            ),
            'grade': TextInput(
                attrs={
                    'placeholder': 'Grade',
                }
            ),
        }

class PrereqMapForm(Form):
    target_course = ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=CoursesWidget(
            attrs={
                'data-placeholder': 'Select Target Course',
                'data-minimum-input-length': 1,
            }
        ),
    )

class PrereqCourseForm(Form):
    course = ModelChoiceField(
        queryset=Course.objects.none(),
        required=False,
    )
    def __init__(self, *args, application, **kwargs):
        super().__init__(*args, **kwargs)

        applicant = application.applicant

        self.fields['course'].widget = ApplicantCoursesWidget(
            applicant=applicant,
            attrs={
                'data-placeholder': 'Select Prerequisite Course',
                'data-minimum-input-length': 0,
            },
        )

        if application.applicant is None:
            self.fields['course'].queryset = Course.objects.filter(
                applicationtranscript__application=application
            ).prefetch_related('programs__school').distinct()
        else:
            self.fields['course'].queryset = Course.objects.filter(
                applicationtranscript__application__applicant=applicant
            ).prefetch_related('programs__school').distinct()

class BatchImportRowForm(ModelForm):
    scanned_last_name = CharField(required=False, max_length=Applicant._meta.get_field('last_name').max_length, widget=TextInput(attrs={'readonly': True}))
    scanned_first_name = CharField(required=False, max_length=Applicant._meta.get_field('first_name').max_length, widget=TextInput(attrs={'readonly': True}))
    scanned_middle_name = CharField(required=False,max_length=Applicant._meta.get_field('middle_name').max_length, widget=TextInput(attrs={'readonly': True}))
    scanned_email = CharField(required=False, max_length=Applicant._meta.get_field('email').max_length, widget=TextInput(attrs={'readonly': True}))
    scanned_contact_number = CharField(required=False, max_length=Applicant._meta.get_field('contact_number').max_length, widget=TextInput(attrs={'readonly': True}))

    class Meta:
        model = Application
        fields = [
            'application_number', 'applicant', 'application_status', 'folder_link', 'program', 'study_load',
            'unit', 'research_field_1', 'research_field_2', 'research_field_3', 'special_project_topic_interest',
            'undergraduate_gwa', 'undergraduate_failed_subjects', 'graduate_gwa', 'graduate_failed_subjects',
            'ngse_requirements_complete', 'ngse_remarks',
            'notes',
        ]
        widgets = {
            'applicant': ApplicantsWidget(
                attrs={
                    'data-placeholder': 'Select Applicant...',
                    'data-minimum-input-length': 1,
                },
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
    ngse_requirements_complete = TypedChoiceField(
        choices=[
            ('null', 'Unknown'),
            ('true', 'Yes'),
            ('false', 'No'),
        ],
        coerce=lambda v: {
            'null': None,
            'true': True,
            'false': False,
        }[v],
        required=False,
        widget=Select2Widget(
            attrs={
                'data-placeholder': 'Complete?',
            }
        ),
    )

BatchImportFormSet = formset_factory(BatchImportRowForm, extra=0)

class OCRRowForm(Form):
    include = BooleanField(required=False, initial=True)
    scanned_code = CharField(required=False, max_length=Course._meta.get_field('course_code').max_length, widget=HiddenInput())
    scanned_name = CharField(required=False, max_length=Course._meta.get_field('course_name').max_length, widget=HiddenInput())
    scanned_units = CharField(required=False, max_length=10, widget=HiddenInput())
    
    course = ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=CoursesWidget(
            attrs={
                'data-placeholder': 'Select course...',
                'data-minimum-input-length': 1,
            },
        )
    )
    grade = CharField(
        required=False,
        max_length=ApplicationTranscript._meta.get_field('grade').max_length,
        widget=TextInput(attrs={'placeholder': 'Grade'})
    )

    def clean(self):
        cleaned_data = super().clean()

        include = cleaned_data.get('include')
        course = cleaned_data.get('course')
        grade = cleaned_data.get('grade')

        if include:
            if not course:
                self.add_error('course', 'This field is required.')
            if not grade:
                self.add_error('grade', 'This field is required.')
        
        return cleaned_data


OCRFormSet = formset_factory(OCRRowForm, extra=0)

class ExportOptionsForm(Form):
    EXPORT_CHOICES = [
        ('csv', 'CSV'),
        ('xlsx', 'Excel (XLSX)'),
    ]
    export_format = ChoiceField(
        choices=EXPORT_CHOICES,
        widget=Select2Widget(
            attrs={
                'data-placeholder': 'Export Type',
            }
        ),
        required=True
    )