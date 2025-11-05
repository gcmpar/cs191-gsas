from django.db import models


class Student(models.Model):
    student_no = models.CharField(primary_key=True, max_length=20)
    full_name = models.CharField(max_length=100)
    ay_entry = models.CharField(max_length=15, blank=True, null=True)
    ay_latest = models.CharField(max_length=15, blank=True, null=True)
    degree = models.CharField(max_length=10, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    study_load = models.CharField(max_length=9, blank=True, null=True)
    scholarship = models.CharField(max_length=50, blank=True, null=True)
    progress_status = models.CharField(max_length=21, blank=True, null=True)
    year_graduation = models.TextField(blank=True, null=True)  # This field type is a guess.
    progress_link = models.CharField(max_length=255, blank=True, null=True)
    adviser_lab = models.CharField(max_length=100, blank=True, null=True)
    folder_link = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'student'
