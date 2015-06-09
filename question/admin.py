from django.contrib import admin
from question.models import Question, Reply, ReplyList

# Register your models here.
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'text','date')
    list_display_links = ('id', 'title', 'text','date')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'date', 'question')
    list_display_links = ('id', 'text', 'date', 'question')

class ReplyListAdmin(admin.ModelAdmin):
    list_display = ('question', 'answerer', 'time_limit_date', 'has_replied')
    list_display_links = ('question', 'answerer', 'time_limit_date', 'has_replied')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(ReplyList, ReplyListAdmin)
