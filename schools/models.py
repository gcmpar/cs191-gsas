from django.db import models


class School(models.Model):
    school_id   = models.AutoField('School Id', primary_key=True)
    school_name = models.CharField('School Name', max_length=100)
    notes       = models.TextField('Notes', blank=True, null=True)

    class Meta:
        db_table = 'school'