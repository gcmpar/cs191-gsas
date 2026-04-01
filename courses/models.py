from django.db import models
from django.core.validators import MinValueValidator
from programs.models import Program


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
        constraints = [
            models.UniqueConstraint(fields=['course', 'prereq'], name='CPK_prerequisite')
        ]


class EquivalenceMap(models.Model):
    map_id        = models.AutoField('EquivalenceMap Id', primary_key=True)
    target_course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'equivalence_map'

class EquivalenceMapCourses(models.Model):
    map_entry_id = models.AutoField('EequivalenceMapCourses Id', primary_key=True)
    map          = models.ForeignKey(EquivalenceMap, on_delete=models.CASCADE)
    course       = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'equivalence_map_courses'
        constraints = [
            models.UniqueConstraint(fields=['map', 'course'], name='CPK_equivalence_map_courses')
        ]