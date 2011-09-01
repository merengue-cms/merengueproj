# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import BaseAdmin
from merengue.review.models import ReviewTask
from merengue.perms import utils as perms_api


class ReviewAdmin(BaseAdmin):

    list_display = ('title', 'owner', 'get_assigned_to', 'is_done', 'url_link', 'task_object', )
    list_filter = ('is_done', )
    search_fields = ('title', 'url', 'assigned_to__username', 'owner__username', )
    list_per_page = 50
    actions = ['mark_as_done', 'mark_as_not_done']

    def url_link(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % (obj.url, obj.url)
    url_link.short_description = _('URL')
    url_link.allow_tags = True

    def get_assigned_to(self, obj):
        return ', '.join([i.username for i in obj.assigned_to.order_by('username')])
    get_assigned_to.short_description = _('assigned to')

    def get_form(self, request, obj=None):
        if not self.has_add_permission(request):
            self.readonly_fields = ('owner', 'assigned_to', 'title', 'url_link', 'task_object', )
        else:
            self.readonly_fields = ('owner', 'title', 'url_link', 'task_object', )

        self.fieldsets = None
        form = super(ReviewAdmin, self).get_form(request, obj)
        self.fieldsets = (
            (_('Task information'), {
                'fields': ('owner', 'assigned_to', 'title', 'url_link', 'task_object', ), }),
            (_('Task status'), {
                'fields': ('is_done', ), }),
        )
        form.url_link = self.url_link  # URL to the object
        return form

    def add_view(self, request, form_url="", extra_context=None):
        data = request.GET.copy()
        data['owner'] = request.user.id
        request.GET = data
        return super(ReviewAdmin, self).add_view(request, form_url="", extra_context=extra_context)

    def queryset(self, request):
        if not self.has_add_permission(request):
            return ReviewTask.objects.filter(assigned_to=request.user)
        return ReviewTask.objects.all()

    def has_add_permission(self, request):
        """
            Overrides Django admin behaviour to add ownership based access control
        """
        return perms_api.has_global_permission(request.user, 'manage_review')

    def has_change_permission(self, request, obj=None):
        #regular users can still edit the task status, other fields are read only
        return True

    def has_delete_permission(self, request, obj=None):
        return self.has_add_permission(request)

    def get_actions(self, request):
        actions = super(ReviewAdmin, self).get_actions(request)
        if not self.has_add_permission(request):
            del actions['delete_selected']
        return actions

    def mark_as_done(self, request, queryset):
        queryset.update(is_done=True)
    mark_as_done.short_description = _("Mark selected tasks as done")

    def mark_as_not_done(self, request, queryset):
        queryset.update(is_done=False)
    mark_as_not_done.short_description = _("Mark selected tasks as not done")


def register(site):
    """ Merengue admin registration callback """
    site.register(ReviewTask, ReviewAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(ReviewAdmin)
