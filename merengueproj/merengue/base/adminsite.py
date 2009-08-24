from django.contrib.admin.sites import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    pass


# This global object represents the default admin site, for the common case.
# You can instantiate AdminSite in your own code to create a custom admin site.
site = AdminSite()
