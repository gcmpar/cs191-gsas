from django.forms import ModelForm, widgets
from programs.models import Program
from .models import Course

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['program', 'course_code', 'course_name', 'units', 'description']
        widgets = {
            'program':     widgets.Select(attrs={'class': 'form-select'}),
            'course_code': widgets.TextInput(attrs={'class': 'form-control'}),
            'course_name': widgets.TextInput(attrs={'class': 'form-control'}),
            'units':       widgets.NumberInput(attrs={'class': 'form-control'}),
            'description': widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program'].queryset = Program.objects.select_related('school').all()
        self.fields['program'].label_from_instance = lambda obj: f"{obj.school.school_name} — {obj.program_name}"