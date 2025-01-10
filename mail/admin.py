from django.contrib import admin

from .models import Company, Recipient, Pipeline, EmailFollowup, Followup


class CompanyAdmin(admin.ModelAdmin):
	list_display = ('name', 'url', 'user')

class RecipientAdmin(admin.ModelAdmin):
	list_display = ('first_name', 'last_name', 'company', 'email', 'user')

class PipelineAdmin(admin.ModelAdmin):
	list_display = ('recipient', 'company', 'language', 'status', 'user')

class EmailFollowupAdmin(admin.ModelAdmin):
	list_display = ('recipient', 'company', 'user', 'status', 'date_to_send', 'subject')

class FollowupAdmin(admin.ModelAdmin):
	list_display = ('email', 'user', 'status', 'date_to_send', 'number')


admin.site.register(Company, CompanyAdmin)
admin.site.register(Recipient, RecipientAdmin)
admin.site.register(Pipeline, PipelineAdmin)
admin.site.register(EmailFollowup, EmailFollowupAdmin)
admin.site.register(Followup, FollowupAdmin)
