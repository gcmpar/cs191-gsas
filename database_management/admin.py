from gsas.admin import admin_site
import database_management.models as M


admin_site.register(M.School)
admin_site.register(M.Program)
admin_site.register(M.Course)
admin_site.register(M.Prerequisite)
admin_site.register(M.Applicant)
admin_site.register(M.Application)
admin_site.register(M.EquivalenceGroup)
admin_site.register(M.EquivalenceGroupMap)
admin_site.register(M.Enrolled)
admin_site.register(M.Transcript)
