from django.contrib import admin
from .models import *

class TalkGroupAdmin(admin.ModelAdmin):
    search_fields = ['alpha_tag', 'description', 'dec_id']
    list_display = ('alpha_tag', 'description', 'dec_id')

class UnitAdmin(admin.ModelAdmin): 
    search_fields = ['description', 'dec_id' ]
    list_display = ('description', 'dec_id' )

class TranmissionUnitInline(admin.TabularInline):
    model = TranmissionUnit
    extra = 0 # how many rows to show

class TransmissionAdmin(admin.ModelAdmin):
    inlines = (TranmissionUnitInline,)

admin.site.register(Transmission, TransmissionAdmin)
admin.site.register(Unit,UnitAdmin)
admin.site.register(TranmissionUnit)
admin.site.register(TalkGroup, TalkGroupAdmin)
admin.site.register(ScanList)
admin.site.register(MenuScanList)
admin.site.register(MenuTalkGroupList)
