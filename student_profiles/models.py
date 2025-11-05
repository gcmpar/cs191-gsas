from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime

# TODO View for AY Entry and AY Latest must have a second side textbox
# that is automatically filled with startYear + 1 (see how CRS does it
# for AY of the Transactions)

class YearField(models.PositiveSmallIntegerField):
    def __init__(self, *args, min_year=1900, max_year=datetime.now().year+10, **kwargs):
        self.min_year = min_year
        self.max_year = max_year
        kwargs['choices'] = [(r, str(r)) for r in range(min_year, max_year)]
        kwargs['validators'] = [MinValueValidator(min_year), MaxValueValidator(max_year)]
        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['min_year'] = self.min_year
        kwargs['max_year'] = self.max_year
        del kwargs['choices']
        del kwargs['validators']
        return name, path, args, kwargs


class Student(models.Model):
    class Degree(models.TextChoices):
        PHD_CS = 'PhD CS', 'PhD CS'
        MS_CS = 'MS CS', 'MS CS'
        MS_BIOINFO = 'MS Bioinfo', 'MS Bioinfo'

        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)

    class StudyLoad(models.TextChoices):
        FULL_TIME = 'Full-Time', 'Full-Time'
        PART_TIME = 'Part-Time', 'Part-Time'

        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)

    class ProgressStatus(models.TextChoices):
        PROBATIONARY = 'Probationary', 'Probationary'
        PRE_PROPOSAL = 'Pre-Proposal', 'Pre-Proposal'
        THESIS_PROPOSAL = 'Thesis Proposal', 'Thesis Proposal'
        THESIS_DEFENSE = 'Thesis Defense', 'Thesis Defense'
        CANDIDACY = 'Candidacy', 'Candidacy'
        QUALIFYING_EXAM = 'Qualifying Exam', 'Qualifying Exam'
        DISSERTATION_PROPOSAL = 'Dissertation Proposal', 'Dissertation Proposal'
        DISSERTATION_DEFENSE = 'Dissertation Defense', 'Dissertation Defense'
        GRADUATE = 'Graduate', 'Graduate'
        DISCONTINUED_PROGRAM = 'Discontinued Program', 'Discontinued Program'

        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)

    student_number = models.CharField('Student Number', primary_key=True, max_length=20)
    first_name = models.CharField('First Name', max_length=50)
    middle_name = models.CharField('Middle Name', max_length=50)
    last_name = models.CharField('Last Name', max_length=50)
    ay_entry = YearField('AY Entry')
    ay_latest = YearField('AY Latest')
    degree = models.CharField('Degree Program', max_length=Degree.max_length(), choices=Degree)
    email = models.CharField('Email', max_length=100)
    contact_number = models.CharField('Contact Number', max_length=20)
    study_load = models.CharField('Study Load', max_length=StudyLoad.max_length(), choices=StudyLoad)
    scholarship = models.CharField('Scholarship', max_length=50)
    progress_status = models.CharField('Progress Status', max_length=ProgressStatus.max_length(), choices=ProgressStatus)
    year_graduation = YearField('Year of Graduation')
    progress_link = models.CharField('Progress Link', max_length=255)
    adviser_lab = models.CharField('Adviser / Lab', max_length=100)
    folder_link = models.CharField('Folder Link', max_length=255)
    notes = models.TextField('Notes', blank=True, null=True)

    def clean(self):
        super().clean()
        if not (self.ay_entry <= self.ay_latest):
            raise ValidationError("CONSTRAINT (ay_entry <= ay_latest)")

    class Meta:
        db_table = 'student'
