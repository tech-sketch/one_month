from django.contrib import admin
from question.models import Question, Reply

# Register your models here.
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'text','date')
    list_display_links = ('id', 'title', 'text','date')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'date', 'question')
    list_display_links = ('id', 'text', 'date', 'question')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Reply, ReplyAdmin)