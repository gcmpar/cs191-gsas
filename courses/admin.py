from gsas.admin import admin_site
from . import models


admin_site.register(models.Course)
admin_site.register(models.Prerequisite)
admin_site.register(models.EquivalenceGroup)
admin_site.register(models.EquivalenceGroupMap)
