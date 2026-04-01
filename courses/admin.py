from gsas.admin import admin_site
from . import models


admin_site.register(models.Course)
admin_site.register(models.Prerequisite)
admin_site.register(models.EquivalenceMap)
admin_site.register(models.EquivalenceMapCourses)
