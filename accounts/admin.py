from django.contrib import admin
import accounts

# Register your models here.
admin.site.register(accounts.models.User)
admin.site.register(accounts.models.UserProfile)