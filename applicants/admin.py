from gsas.admin import admin_site
from . import models


admin_site.register(models.Applicant)
admin_site.register(models.Application)
# admin_site.register(models.Enrolled)
admin_site.register(models.ApplicationTranscript)
