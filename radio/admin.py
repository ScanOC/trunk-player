from os import scandir
from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.conf import settings

from .models import *

class TalkGroupAdmin(admin.ModelAdmin):
    search_fields = ['alpha_tag', 'description', 'dec_id']
    list_display = ('alpha_tag', 'description', 'dec_id', 'system')
    save_on_top = True


class UnitAdmin(admin.ModelAdmin): 
    search_fields = ['description', 'dec_id' ]
    list_display = ('description', 'dec_id', 'system' )
    save_on_top = True


class TranmissionUnitInline(admin.TabularInline):
    model = TranmissionUnit
    extra = 0 # how many rows to show

class TransmissionAdmin(admin.ModelAdmin):
    #inlines = (TranmissionUnitInline,)
    raw_id_fields = ('talkgroup_info', 'units', 'source', 'system')
    save_on_top = True


class SourceInline(admin.TabularInline):
    model = Source
    readonly_fields=('id',)


class SourceAdmin(admin.ModelAdmin):
    list_display = ('id','description')
    list_display_links = ('id','description')
    #fields = ('id','description')
    save_on_top = True

    def get_readonly_fields(self, request, obj=None):
            if obj: # editing an existing object
                return self.readonly_fields + ('id',)
            return self.readonly_fields


class ScanListAdminForm(forms.ModelForm):
    talkgroups = forms.ModelMultipleChoiceField(
        queryset=TalkGroupWithSystem.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name = 'talkgroups',
            is_stacked=False
        )
    )

    class Meta:
        model = ScanList
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ScanListAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['talkgroups'].initial = self.instance.talkgroups.all()
    def save(self, commit=True):
        scanlist = super(ScanListAdminForm, self).save(commit=False)

        if commit:
            scanlist.save()

        if scanlist.pk:
            scanlist.talkgroups.set(self.cleaned_data['talkgroups'])
            self.save_m2m()

        return scanlist


class ScanListAdmin(admin.ModelAdmin):
    form = ScanListAdminForm
    save_as = True
    save_on_top = True

class ScanListRawAdmin(admin.ModelAdmin):
    autocomplete_fields= ('talkgroups',)    


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )


class TalkGroupAccessAdminForm(forms.ModelForm):
    talkgroups = forms.ModelMultipleChoiceField(
        queryset=TalkGroupWithSystem.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name = 'talkgroups',
            is_stacked=False
        )
    )

    class Meta:
        model = TalkGroupAccess
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(TalkGroupAccessAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['talkgroups'].initial = self.instance.talkgroups.all()
    def save(self, commit=True):
        tglist = super(TalkGroupAccessAdminForm, self).save(commit=False)

        if commit:
            tglist.save()

        if tglist.pk:
            tglist.talkgroups.set(self.cleaned_data['talkgroups'])
            self.save_m2m()

        return tglist

class TalkGroupAccessAdmin(admin.ModelAdmin):
    form = TalkGroupAccessAdminForm
    list_display = ('name', 'default_group', 'default_new_talkgroups')
    save_on_top = True

class TalkGroupAccessRawAdmin(admin.ModelAdmin):
    autocomplete_fields= ('talkgroups',)   

class TranmissionUnitAdmin(admin.ModelAdmin):
    raw_id_fields = ("transmission", "unit")
    save_on_top = True


class IncidentAdmin(admin.ModelAdmin):
    raw_id_fields = ("transmissions",)
    save_on_top = True

class CityForms(forms.ModelForm):
    google_maps_url = forms.CharField(max_length=1000)

    class Meta:
        model = City
        fields = '__all__'


    def clean_google_maps_url(self):
        data = self.cleaned_data.get('google_maps_url', '')
        parts = data.split('"')
        new_url = None
        try:
          new_url = parts[1]
        except IndexError:
          return self
        return new_url

class CityAdmin(admin.ModelAdmin):
    form = CityForms

class MessagePopUpAdmin(admin.ModelAdmin):
    list_display = ('mesg_type', 'mesg_html', 'active')


admin.site.register(Transmission, TransmissionAdmin)
admin.site.register(Unit,UnitAdmin)
#admin.site.register(TranmissionUnit, TranmissionUnitAdmin)
admin.site.register(TalkGroup, TalkGroupAdmin)

if not settings.USE_RAW_ID_FIELDS:
    admin.site.register(ScanList, ScanListAdmin)
    admin.site.register(TalkGroupAccess, TalkGroupAccessAdmin)
else:
    admin.site.register(ScanList, ScanListRawAdmin)
    admin.site.register(TalkGroupAccess, TalkGroupAccessRawAdmin)
admin.site.register(MenuScanList)
admin.site.register(MenuTalkGroupList)
admin.site.register(Source, SourceAdmin)
admin.site.register(Agency)
admin.site.register(Plan)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(System)
admin.site.register(WebHtml)
admin.site.register(RepeaterSite)
admin.site.register(Service)
admin.site.register(SiteOption)
admin.site.register(Incident, IncidentAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(MessagePopUp, MessagePopUpAdmin)


# New Fine-Grained Authorization Admin

class SystemRoleInline(admin.TabularInline):
    model = SystemRole
    extra = 0
    fields = ('user', 'role', 'created_at', 'created_by')
    readonly_fields = ('created_at', 'created_by')


class SystemPermissionInline(admin.TabularInline):
    model = SystemPermission
    extra = 0
    fields = ('permission', 'granted_at', 'granted_by')
    readonly_fields = ('granted_at', 'granted_by')


class UserTalkgroupAccessInline(admin.TabularInline):
    model = UserTalkgroupAccess
    extra = 0
    fields = ('talkgroup', 'granted_at', 'granted_by')
    readonly_fields = ('granted_at', 'granted_by')
    raw_id_fields = ('talkgroup',)


@admin.register(SystemRole)
class SystemRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'system', 'role', 'created_at', 'created_by')
    list_filter = ('role', 'system', 'created_at')
    search_fields = ('user__username', 'user__email', 'system__name')
    raw_id_fields = ('user', 'created_by')
    inlines = [SystemPermissionInline, UserTalkgroupAccessInline]
    save_on_top = True

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SystemPermission)
class SystemPermissionAdmin(admin.ModelAdmin):
    list_display = ('system_role', 'permission', 'granted_at', 'granted_by')
    list_filter = ('permission', 'granted_at', 'system_role__system')
    search_fields = ('system_role__user__username', 'system_role__system__name')
    raw_id_fields = ('system_role', 'granted_by')
    save_on_top = True

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(UserTalkgroupAccess)
class UserTalkgroupAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'talkgroup', 'system_name', 'granted_at', 'granted_by')
    list_filter = ('granted_at', 'talkgroup__system')
    search_fields = ('user__username', 'talkgroup__alpha_tag', 'talkgroup__system__name')
    raw_id_fields = ('user', 'granted_by', 'talkgroup')
    save_on_top = True

    def system_name(self, obj):
        return obj.talkgroup.system.name
    system_name.short_description = 'System'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.granted_by = request.user
            # Ensure user has a SystemRole for this system
            system_role, created = SystemRole.objects.get_or_create(
                user=obj.user,
                system=obj.talkgroup.system,
                defaults={'role': SystemRole.USER, 'created_by': request.user}
            )
            obj.system_role = system_role
        super().save_model(request, obj, form, change)


class TalkgroupAccessAdminForm(forms.ModelForm):
    """Form for bulk managing talkgroup access for system admins"""
    talkgroups = forms.ModelMultipleChoiceField(
        queryset=TalkGroupWithSystem.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Talkgroups',
            is_stacked=False
        ),
        help_text='Select talkgroups to grant access to this user for this system'
    )

    class Meta:
        model = SystemRole
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Show currently accessible talkgroups
            self.fields['talkgroups'].initial = TalkGroupWithSystem.objects.filter(
                user_permissions__user=self.instance.user,
                system=self.instance.system
            )
            # Limit talkgroup choices to this system
            self.fields['talkgroups'].queryset = TalkGroupWithSystem.objects.filter(
                system=self.instance.system
            )

    def save(self, commit=True):
        system_role = super().save(commit=False)
        if commit:
            system_role.save()

        if system_role.pk:
            # Update talkgroup access
            selected_talkgroups = self.cleaned_data.get('talkgroups', [])

            # Remove existing access for this system
            UserTalkgroupAccess.objects.filter(
                user=system_role.user,
                talkgroup__system=system_role.system
            ).delete()

            # Add new access (unless user is admin - they get access to all)
            if not system_role.is_admin:
                for talkgroup in selected_talkgroups:
                    UserTalkgroupAccess.objects.create(
                        user=system_role.user,
                        talkgroup=talkgroup,
                        system_role=system_role,
                        granted_by=getattr(self, '_current_user', None)
                    )

        return system_role


@admin.register(UserTalkgroupMenu)
class UserTalkgroupMenuAdmin(admin.ModelAdmin):
    list_display = ('user', 'talkgroup', 'show_in_menu', 'order', 'created_at')
    list_filter = ('show_in_menu', 'created_at', 'talkgroup__system')
    search_fields = ('user__username', 'talkgroup__alpha_tag')
    raw_id_fields = ('user', 'talkgroup')
    ordering = ('user__username', 'order', 'talkgroup__alpha_tag')


@admin.register(UserScanList)
class UserScanListAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_active', 'is_default', 'talkgroup_count', 'created_at')
    list_filter = ('is_active', 'is_default', 'created_at')
    search_fields = ('user__username', 'name', 'description')
    raw_id_fields = ('user',)
    filter_horizontal = ('talkgroups',)
    save_on_top = True

    def talkgroup_count(self, obj):
        return obj.talkgroups.count()
    talkgroup_count.short_description = 'Talkgroups'


# Update existing System admin to show user roles
class SystemAdminNew(admin.ModelAdmin):
    list_display = ('name', 'system_id', 'user_count')
    search_fields = ('name', 'system_id')
    inlines = [SystemRoleInline]

    def user_count(self, obj):
        return obj.user_roles.count()
    user_count.short_description = 'Users'

admin.site.unregister(System)
admin.site.register(System, SystemAdminNew)
