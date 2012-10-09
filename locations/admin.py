from django.contrib import admin

from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region', 'tik', 'date')
    ordering = ('id',)
    search_fields = ('id', 'region_name', 'vrnkomis', 'vrnorg', 'name')
    raw_id_fields = ('country', 'region', 'tik')

admin.site.register(Location, LocationAdmin)
