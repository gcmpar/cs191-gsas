from django_select2.forms import ModelSelect2Widget
from django.forms import ModelForm, Form, CharField
from .models import School

class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['school_name']

class SchoolsQueryForm(Form):
    search = CharField(required=False)

class RelatedProgramsQueryForm(Form):
    search = CharField(required=False)

class RelatedAppsQueryForm(Form):
    search = CharField(required=False)

class SchoolsWidget(ModelSelect2Widget):
    model = School
    search_fields = ['school_name__icontains']

    def label_from_instance(self, school):
        return f"{school.school_name}"