from django.db import models


class Program(models.Model):
    program_id      = models.AutoField('Program Id', primary_key=True)
    school          = models.ForeignKey(School, on_delete=models.CASCADE)
    program_name    = models.CharField('Program Name', max_length=50)
    description     = models.TextField('Description', max_length=200)

    class Meta:
        db_table = 'program'
