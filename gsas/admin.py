from django.contrib import admin


class GsasAdmin(admin.AdminSite):
    site_header = 'GSAS Administration'
    site_title = 'GSAS site admin'
    index_title = 'Site administration'


admin_site = GsasAdmin(name='gsas-admin')
