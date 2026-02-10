from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime

# TODO View for AY Entry and AY Latest must have a second side textbox
# that is automatically filled with startYear + 1 (see how CRS does it
# for AY of the Transactions)

class YearField(models.PositiveSmallIntegerField):
    def __init__(self, *args, min_year=1900, max_year=datetime.now().year+10, **kwargs):
        self.min_year           = min_year
        self.max_year           = max_year
        kwargs['choices']       = [(r, str(r)) for r in range(min_year, max_year)]
        kwargs['validators']    = [MinValueValidator(min_year), MaxValueValidator(max_year)]
        
        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        name, path, args, kwargs    = super().deconstruct()
        kwargs['min_year']          = self.min_year
        kwargs['max_year']          = self.max_year

        del kwargs['choices']
        del kwargs['validators']
        
        return name, path, args, kwargs


class School(models.Model):
    school_id   = models.CharField('School ID', primary_key=True, max_length=20)
    school_name = models.CharField('School Name', max_length=100)

    class Meta:
        db_table = 'school'


class Applicant(models.Model):
    class Status(models.TextChoices):
        APPLYING        = 'applying', 'applying'
        REJECTED        = 'rejected', 'rejected'
        IS_ENROLLED     = 'enrolled', 'enrolled'
        DEFERRED        = 'deferred', 'deferred'

        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)

    applicant_number    = models.CharField('Applicant Number', primary_key=True, max_length=20)
    first_name          = models.CharField('First Name', max_length=50)
    middle_name         = models.CharField('Middle Name', max_length=50)
    last_name           = models.CharField('Last Name', max_length=50)
    applicant_status    = models.CharField('Applicant Status', max_length=Status.max_length(), choices=Status)
    email               = models.CharField('Email', max_length=100)
    contact_number      = models.CharField('Contact Number', max_length=20)
    notes               = models.TextField('Notes', blank=True, null=True)

    # def clean(self):
    #     super().clean()
    #     if not (self.ay_entry <= self.ay_latest):
    #         raise ValidationError("CONSTRAINT (ay_entry <= ay_latest)")

    class Meta:
        db_table = 'applicant'

class Application(models.Model):
    class Degree(models.TextChoices):
        PHD_CS      = 'PhD CS', 'PhD CS' # one  is dropdown text, hte other is actual val
        MS_CS       = 'MS CS', 'MS CS'
        MS_BIOINFO  = 'MS Bioinfo', 'MS Bioinfo'

        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)
        
    class StudyLoad(models.TextChoices):
        FULL_TIME = 'Full-Time', 'Full-Time'
        PART_TIME = 'Part-Time', 'Part-Time'

        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)
        
    class Status(models.TextChoices):
        PROCESSING  = 'processing', 'processing'
        ACCEPTED    = 'accepted', 'accepted'
        REJECTED    = 'rejected', 'rejected'
        
        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)
    
    application_no      = models.CharField('Application Number', primary_key=True, max_length=20)
    applicant_number    = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    applicant_status    = models.CharField('Applicant Status', max_length=Status.max_length(), choices=Status)
    date_applied        = models.DateField('Date Applied')
    degree              = models.CharField('Degree Program', max_length=Degree.max_length(), choices=Degree)
    folder_link         = models.CharField('Folder Link', max_length=255)
    study_load          = models.CharField('Study Load', max_length=StudyLoad.max_length(), choices=StudyLoad)

    class Meta:
        db_table = 'application'

class Program(models.Model):
    program_id      = models.CharField('Program ID', primary_key=True, max_length=20)
    school          = models.ForeignKey(School, on_delete=models.CASCADE)
    program_name    = models.CharField('Program Name', max_length=50)
    description     = models.TextField('Description', max_length=200)

    class Meta:
        db_table = 'program'


class Course(models.Model):

    course_id       = models.CharField('Course ID', primary_key=True, max_length=20)
    program         = models.ForeignKey(Program, on_delete=models.CASCADE)
    course_code     = models.CharField('Course Code', max_length=20)
    course_name     = models.CharField('Course Name', max_length=50)
    units           = models.PositiveSmallIntegerField('Units', validators=[MinValueValidator(20)])
    description     = models.CharField('Description', max_length=200)

    class Meta:
        db_table = 'course'


class Prerequisite(models.Model):
    prereq_entry_id     = models.CharField('prereq_entry_id', primary_key=True, max_length=20)
    course              = models.ForeignKey(Course, on_delete=models.CASCADE)
    prereq              = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prereq_id', verbose_name="Prereq ID")

    class Meta:
        db_table = 'prerequisite'

            
class Enrolled(models.Model):
    enrolled_id     = models.CharField('Enrolled ID', primary_key=True, max_length=20)
    applicant       = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    course          = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'enrolled'


class Transcript(models.Model):
    class Semester(models.TextChoices):
        Sem_1 = '1st', '1st'
        Sem_2 = '2nd', '2nd'
        Sem_3 = '3rd', '3rd'

        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)

    class Grade(models.TextChoices):
        Grade_100 = '1.00', '1.00'  
        Grade_125 = '1.25', '1.25'
        Grade_150 = '1.50', '1.50'
        Grade_175 = '1.75', '1.75'
        Grade_200 = '2.00', '2.00'
        Grade_225 = '2.25', '2.25'
        Grade_250 = '2.50', '2.50'
        Grade_275 = '2.75', '2.75'
        Grade_300 = '3.00', '3.00'
        Grade_400 = '4.00', '4.00'
        Grade_500 = '5.00', '5.00'
        Grade_INC = 'INC', 'INC'
        Grade_DRP = 'DRP', 'DRP'

        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)
    
    transcript_id   = models.CharField('Transcript ID', primary_key=True, max_length=20)
    application_no  = models.ForeignKey(Application, on_delete=models.CASCADE)
    course          = models.ForeignKey(Course, on_delete=models.CASCADE)
    academic_year   = YearField('Academic Year')
    semester        = models.CharField('Semester', max_length=Semester.max_length(), choices=Semester)
    grade           = models.CharField('Grade', max_length=Grade.max_length(), choices=Grade)

    class Meta:
        db_table = 'transcript'

class EquivalenceGroup(models.Model):
    group_id    = models.CharField('Group ID', primary_key=True, max_length=20)
    course_id   = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'equivalence group'

class EquivalenceGroupMap(models.Model):
    map_id      = models.CharField('Map ID', primary_key=True, max_length=20)
    group_id    = models.ForeignKey(EquivalenceGroup, on_delete=models.CASCADE)
    course_id   = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'equivalence group map'