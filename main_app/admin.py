from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from django.utils.translation import gettext, gettext_lazy as _

from .models import *


# Register your models here.


class UserModel(admin.ModelAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        ('Secrets', {'fields': ('password', 'fcm_token')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
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
    'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'address', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


class OpModel(admin.ModelAdmin):
    list_display = ('re_user', 're_ip', 're_url', 're_content', 'rp_status_code')
    readonly_fields = ('re_user', 're_ip', 're_url', 're_content', 'rp_status_code', 'rp_content',
                       're_time', 're_method', 'access_time')
    search_fields = ('re_user__email', 're_user__first_name', 're_user__last_name', 're_ip', 're_url', 're_content',
                     'rp_status_code')

    def get_actions(self, request):
        actions = super(OpModel, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(OpLogs, OpModel)

admin.site.register(CustomUser, UserModel)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Session)
