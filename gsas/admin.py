from django.contrib import admin
from django.contrib.auth.models import User, Group

class GsasAdminSite(admin.AdminSite):
    site_header = 'GSAS Administration'
    site_title = 'GSAS site admin'
    index_title = 'Site administration'


admin_site = GsasAdminSite(name='gsas-admin')
admin_site.register(User)
admin_site.register(Group)