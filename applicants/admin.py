from gsas.admin import admin_site
import applicants.models as M


admin_site.register(M.Applicant)
admin_site.register(M.Application)
# admin_site.register(M.Enrolled)
admin_site.register(M.ApplicationTranscript)
