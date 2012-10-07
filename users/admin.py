from django.contrib import admin
from django.contrib.auth.models import User

from users.models import Message, Profile, Role

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'title', 'show_email', 'time')
    ordering = ('-time',)
    search_fields = ('sender', 'receiver')
    raw_id_fields = ('sender', 'receiver')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'about', 'rating')
    ordering = ('-add_time',)
    search_fields = ('user__email', 'first_name', 'last_name')
    raw_id_fields = ('user',)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('profile', 'location', 'type')
    search_fields = ('profile__user__email',)
    raw_id_fields = ('location', 'profile')

admin.site.register(Message, MessageAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Role, RoleAdmin)

# A hack to show is_active field in User model admin instead of is_stuff
admin.site._registry[User].list_display = ('email', 'is_active', 'date_joined', 'last_login')
