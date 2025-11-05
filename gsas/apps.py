from django.contrib.admin.apps import AdminConfig


class GsasAdminConfig(AdminConfig):
    default_site = 'gsas.admin.GsasAdminSite'