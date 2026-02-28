from gsas.admin import admin_site
import academics.models as M


admin_site.register(M.School)
admin_site.register(M.Program)
admin_site.register(M.Course)
admin_site.register(M.Prerequisite)
admin_site.register(M.EquivalenceGroup)
admin_site.register(M.EquivalenceGroupMap)
