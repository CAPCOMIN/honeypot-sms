from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import messages
from django.utils.translation import ngettext

from .models import *


# Register your models here.


class UserModel(admin.ModelAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        ('Secrets', {'fields': ('password', 'fcm_token')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('password1', 'password2'),
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = (
        'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_superuser', 'is_active', 'address',
        'last_login')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'groups',)
    search_fields = ('first_name', 'last_name', 'email', 'user_type')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


class OpModel(admin.ModelAdmin):
    list_display = ('re_user', 're_ip', 'get_path', 're_time', 'colored_rp_status_code', 'update_rp_content',
                    'update_re_content', 'access_time')
    readonly_fields = ('re_user', 're_ip', 're_url', 're_content', 'colored_rp_status_code', 'rp_content',
                       're_time', 're_method', 'access_time', 're_ua', 'rp_status_code', )
    search_fields = ('re_user__email', 're_user__first_name', 're_user__last_name', 're_ip', 're_url', 're_content',
                     'rp_status_code')
    list_filter = ('re_time', 'rp_status_code', 're_ip', 're_user')

    def get_path(self, instance):
        if len(str(instance.re_url)) > 35:
            p = '{}...'.format(str(instance.re_url)[0:35])
            #todo path url
            return format_html('<a href="?re_url={full_path}">{path}</a>', path=p, full_path=instance.re_url)
        else:
            return format_html('<a href="?re_url={path}">{path}</a>', path=instance.re_url)

    get_path.short_description = _('URL')

    def get_actions(self, request):
        actions = super(OpModel, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class AccessTimeOutLogsModel(admin.ModelAdmin):
    list_display = ('re_user', 're_ip', 'get_path', 're_time', 'colored_rp_status_code', 'update_re_content',
                    'update_rp_content', 'colored_access_time')
    readonly_fields = ('re_user', 're_ip', 're_url', 're_content', 'colored_rp_status_code', 'rp_content',
                       're_time', 're_method', 'colored_access_time', 're_ua')
    search_fields = ('re_user__email', 're_user__first_name', 're_user__last_name', 're_ip', 're_url', 're_content',
                     'rp_status_code')
    list_filter = ('re_time', 'rp_status_code', 're_ip', 're_user')

    def get_path(self, instance):
        if len(str(instance.re_url)) > 35:
            p = '{}...'.format(str(instance.re_url)[0:35])
            return format_html('<a href="?re_url={full_path}">{path}</a>', path=p, full_path=instance.re_url)
        else:
            return format_html('<a href="?re_url={path}">{path}</a>', path=instance.re_url)

    get_path.short_description = _('URL')

    def get_actions(self, request):
        actions = super(AccessTimeOutLogsModel, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class VulnSwitchModel(admin.ModelAdmin):
    list_display = ('module', 'colored_mode', 'description', 'search_page_url', 'search_action_url', 'auth', )
    actions = ['make_vulnerable', 'make_optimized', 'make_denied']

    def make_vulnerable(self, request, queryset):
        updated = queryset.update(mode=1)
        self.message_user(request, ngettext(
            '%d decoy vulnerability module has been successfully set to the vulnerable mode.',
            '%d decoy vulnerability modules have been successfully set to vulnerable mode.',
            updated,
        ) % updated, messages.SUCCESS)

    make_vulnerable.short_description = "Mark selected module as vulnerable"

    def make_optimized(self, request, queryset):
        updated = queryset.update(mode=2)
        self.message_user(request, ngettext(
            '%d decoy vulnerability module has been successfully set to the optimized mode.',
            '%d decoy vulnerability modules have been successfully set to optimized mode.',
            updated,
        ) % updated, messages.SUCCESS)

    make_optimized.short_description = "Mark selected module as optimized"

    def make_denied(self, request, queryset):
        updated = queryset.update(mode=3)
        self.message_user(request, ngettext(
            '%d decoy vulnerability module has been successfully set to the denied mode.',
            '%d decoy vulnerability modules have been successfully set to denied mode.',
            updated,
        ) % updated, messages.SUCCESS)

    make_denied.short_description = "Mark selected module as denied"


admin.site.register(OpLogs, OpModel)
admin.site.register(AccessTimeOutLogs, AccessTimeOutLogsModel)
admin.site.register(VulnSwitch, VulnSwitchModel)

admin.site.register(CustomUser, UserModel)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Session)
