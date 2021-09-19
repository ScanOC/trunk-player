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
