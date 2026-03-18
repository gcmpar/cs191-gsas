from django.db import models
from django.core.validators import MinValueValidator


class School(models.Model):
    school_id   = models.AutoField('School Id', primary_key=True)
    school_name = models.CharField('School Name', max_length=100)

    class Meta:
        db_table = 'school'

class Program(models.Model):
    program_id      = models.AutoField('Program Id', primary_key=True)
    school          = models.ForeignKey(School, on_delete=models.CASCADE)
    program_name    = models.CharField('Program Name', max_length=50)
    description     = models.TextField('Description', max_length=200)

    class Meta:
        db_table = 'program'


class Course(models.Model):

    course_id       = models.AutoField('Course Id', primary_key=True)
    program         = models.ForeignKey(Program, on_delete=models.CASCADE)
    course_code     = models.CharField('Course Code', max_length=20)
    course_name     = models.CharField('Course Name', max_length=50)
    units           = models.PositiveSmallIntegerField('Units', validators=[MinValueValidator(1)])
    description     = models.CharField('Description', max_length=200)

    class Meta:
        db_table = 'course'


class Prerequisite(models.Model):
    prereq_entry_id     = models.AutoField('Prereq Entry Id', primary_key=True)
    course              = models.ForeignKey(Course, on_delete=models.CASCADE)
    prereq              = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prereq_id', verbose_name="Prereq ID")

    class Meta:
        db_table = 'prerequisite'


class EquivalenceGroup(models.Model):
    group_id    = models.AutoField('EquivalenceGroup Id', primary_key=True)
    course      = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'equivalence_groups'

class EquivalenceGroupMap(models.Model):
    map_id      = models.AutoField('EquivalenceGroupMap Id', primary_key=True)
    group       = models.ForeignKey(EquivalenceGroup, on_delete=models.CASCADE)
    course      = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'equivalence_group_map'


