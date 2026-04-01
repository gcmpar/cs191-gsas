from django.db import models


class Applicant(models.Model):
    class Status(models.TextChoices):
        APPLYING        = 'Applying', 'Applying'
        REJECTED        = 'Rejected', 'Rejected'
        ENROLLED        = 'Enrolled', 'Enrolled'
        DEFERRED        = 'Deferred', 'Deferred'

        @classmethod
        def max_length(cls):
            return max(len(v) for v in cls.values)

    applicant_id        = models.AutoField('Applicant Id', primary_key=True)
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

