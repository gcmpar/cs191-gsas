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

    unit                            = models.CharField('Unit', max_length=100, blank=True, null=True)
    research_field_1                = models.CharField('Research Field 1', max_length=100, blank=True, null=True)
    research_field_2                = models.CharField('Research Field 2', max_length=100, blank=True, null=True)
    research_field_3                = models.CharField('Research Field 3', max_length=100, blank=True, null=True)
    special_project_topic_interest  = models.CharField('Special Project Topic Interest', max_length=100, blank=True, null=True)
    undergraduate_gwa               = models.CharField('Undergraduate GWA', max_length=10, blank=True, null=True)
    undergraduate_failed_subjects   = models.CharField('Undergraduate Number of Failed Subjects', max_length=10, blank=True, null=True)
    graduate_gwa                    = models.CharField('Graduate GWA', max_length=10, blank=True, null=True)
    graduate_failed_subjects        = models.CharField('Graduate Number of Failed Subjects', max_length=10, blank=True, null=True)
    ngse_requirements_complete      = models.BooleanField('NGSE Requirements Complete', blank=True, null=True, default=None)
    ngse_remarks                    = models.TextField('NGSE Remarks', blank=True, null=True)

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


    transcript_id   = models.AutoField('Application Transcript Id', primary_key=True)
    application     = models.ForeignKey(Application, on_delete=models.CASCADE)
    course          = models.ForeignKey(Course, on_delete=models.CASCADE)
    academic_year   = YearField('Academic Year')
    semester        = models.CharField('Semester', max_length=Semester.max_length(), choices=Semester)
    grade           = models.CharField('Grade', max_length=15)

    class Meta:
        db_table = 'application_transcript'
        constraints = [
            models.UniqueConstraint(fields=['application', 'course'], name='CPK_application_transcript')
        ]


class PrerequisiteMap(models.Model):
    map_id = models.AutoField('Prerequisite Map Id', primary_key=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    target_course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'prerequisite_map'


class PrerequisiteMapCourses(models.Model):
    map_entry_id = models.AutoField('Prerequisite Map Courses Id', primary_key=True)
    map = models.ForeignKey(PrerequisiteMap, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'prerequisite_map_courses'
        constraints = [
            models.UniqueConstraint(fields=['map', 'course'], name='CPK_prerequisite_map_courses')
        ]