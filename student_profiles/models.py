# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Courses(models.Model):
    course_code = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'courses'
        

class Prereqs(models.Model):
    program = models.CharField(max_length=14)
    core_course_code = models.CharField(max_length=50)
    prereq_course_code = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)

    class Meta:
        db_table = 'prereqs'


class Student(models.Model):
    idstudent = models.AutoField(db_column='idStudent', primary_key=True)  # Field name made lowercase.
    student_name = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=50, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_num = models.CharField(max_length=12, blank=True, null=True)
    sex = models.CharField(max_length=6, blank=True, null=True)
    birthdate = models.CharField(max_length=10, blank=True, null=True)
    university = models.CharField(max_length=255, blank=True, null=True)
    years_attended = models.CharField(max_length=20, blank=True, null=True)
    degree_title = models.CharField(max_length=255, blank=True, null=True)
    extracted_text = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'student'


class Transcripts(models.Model):
    student = models.ForeignKey(Student, models.DO_NOTHING)
    semester = models.CharField(max_length=50, blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    course = models.ForeignKey(Courses, models.DO_NOTHING, blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True, null=True)
    units = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'transcripts'
