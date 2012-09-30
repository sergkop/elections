from django.contrib import admin

from elections.models import Election, ElectionLocation

class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'vrn')

class ElectionLocationAdmin(admin.ModelAdmin):
    list_display = ('election', 'location')
    raw_id_fields = ('election', 'location')

admin.site.register(Election, ElectionAdmin)
admin.site.register(ElectionLocation, ElectionLocationAdmin)
