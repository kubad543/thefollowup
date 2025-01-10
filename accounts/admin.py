from django.contrib import admin

from .models import CustomUser, UserSmtp


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    There is a class to define the values displayed
    for the custom user admin model.
    """
    list_display = ['user', 'name', 'surname', 'phone', 'date_joined', 'date_change']
    list_filter = ['name', 'surname']


admin.site.register(UserSmtp)

