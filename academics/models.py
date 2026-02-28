from django.db import models
from django.core.validators import MinValueValidator


class School(models.Model):
    school_id   = models.CharField('School ID', primary_key=True, max_length=20)
    school_name = models.CharField('School Name', max_length=100)

    class Meta:
        db_table = 'school'

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


class EquivalenceGroup(models.Model):
    group_id    = models.CharField('Group ID', primary_key=True, max_length=20)
    course      = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'equivalence_groups'

class EquivalenceGroupMap(models.Model):
    map_id      = models.CharField('Map ID', primary_key=True, max_length=20)
    group       = models.ForeignKey(EquivalenceGroup, on_delete=models.CASCADE)
    course      = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'equivalence_group_map'


