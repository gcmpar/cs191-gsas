from django.db import models
from common.fields import YearField
from applicants.models import Applicant
from courses.models import Course


class BatchImport(models.Model):
    import_id       = models.AutoField('Import Id', primary_key=True)
    date_imported   = models.DateTimeField('Date Imported', auto_now_add=True)

    class Meta:
        db_table = 'batch_import'


class Application(models.Model):
    class Degree(models.TextChoices):
        PHD_CS      = 'PhD CS', 'PhD CS'
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
        PROCESSING  = 'Processing', 'Processing'
        ACCEPTED    = 'Accepted', 'Accepted'
        REJECTED    = 'Rejected', 'Rejected'
        
        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)
    
    application_id      = models.AutoField('Application Id', primary_key=True)
    applicant           = models.ForeignKey(Applicant, on_delete=models.CASCADE)  
    batch_import        = models.ForeignKey(BatchImport, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    application_number  = models.CharField('Application Number', max_length=20)
    application_status  = models.CharField('Applicant Status', max_length=Status.max_length(), choices=Status)
    date_applied        = models.DateField('Date Applied')
    program             = models.CharField('Degree Program', max_length=Degree.max_length(), choices=Degree)
    folder_link         = models.CharField('Folder Link', max_length=255, blank=True, null=True)
    study_load          = models.CharField('Study Load', max_length=StudyLoad.max_length(), choices=StudyLoad)
    notes               = models.TextField('Notes', blank=True, null=True)

    class Meta:
        db_table = 'application'

            
# class Enrolled(models.Model):
#     enrolled_id     = models.CharField('Enrolled ID', primary_key=True, max_length=20)
#     applicant       = models.ForeignKey(Applicant, on_delete=models.CASCADE)
#     course          = models.ForeignKey(Course, on_delete=models.CASCADE)
    
#     class Meta:
#         db_table = 'enrolled'


class ApplicationTranscript(models.Model):
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
    
    transcript_id   = models.AutoField('Application Transcript Id', primary_key=True)
    application     = models.ForeignKey(Application, on_delete=models.CASCADE)
    course          = models.ForeignKey(Course, on_delete=models.CASCADE)
    academic_year   = YearField('Academic Year')
    semester        = models.CharField('Semester', max_length=Semester.max_length(), choices=Semester)
    grade           = models.CharField('Grade', max_length=Grade.max_length(), choices=Grade)

    class Meta:
        db_table = 'application_transcript'
        constraints = [
            models.UniqueConstraint(fields=['application', 'course'], name='CPK_application_transcript')
        ]


class PrereqMapping(models.Model):
    """
    A reusable saved mapping template: a group of source courses maps to one
    target prerequisite course. Example: [ICT18, ICT22] → CS135.
    Shared across applications — saving the same logical mapping twice is blocked.
    """
    target_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='prereq_mapping_targets',
    )

    class Meta:
        db_table = 'prereq_mapping'

    def source_course_ids_sorted(self):
        """Return a frozenset of source course PKs — used for duplicate detection."""
        return frozenset(self.source_courses.values_list('course_id', flat=True))

    def __str__(self):
        codes = ', '.join(
            self.source_courses.select_related('course')
                               .values_list('course__course_code', flat=True)
                               .order_by('course__course_code')
        )
        return f'[{codes}] → {self.target_course.course_code}'


class PrereqMappingCourse(models.Model):
    """Source courses belonging to a PrereqMapping."""
    mapping = models.ForeignKey(PrereqMapping, on_delete=models.CASCADE,
                                related_name='source_courses')
    course  = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'prereq_mapping_course'
        constraints = [
            models.UniqueConstraint(fields=['mapping', 'course'],
                                    name='CPK_prereq_mapping_course')
        ]


class ApplicationPrereqMapping(models.Model):
    """
    Links a reusable PrereqMapping to a specific Application.
    Removing this row only removes the link — the reusable template is preserved.
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE,
                                    related_name='prereq_mappings')
    mapping     = models.ForeignKey(PrereqMapping, on_delete=models.CASCADE,
                                    related_name='application_usages')

    class Meta:
        db_table = 'application_prereq_mapping'
        constraints = [
            models.UniqueConstraint(fields=['application', 'mapping'],
                                    name='CPK_application_prereq_mapping')
        ]