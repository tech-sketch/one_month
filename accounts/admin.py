from django.contrib import admin
import accounts

# Register your models here.

admin.site.register(accounts.models.WorkPlace)
admin.site.register(accounts.models.Division)
admin.site.register(accounts.models.WorkStatus)
admin.site.register(accounts.models.UserProfile)