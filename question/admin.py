from django.contrib import admin
from question.models import Question, Reply, ReplyList, Tag, UserTag, QuestionTag

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

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)

class UserTagAdmin(admin.ModelAdmin):
    list_display = ('user', 'tag')
    list_display_links = ('user', 'tag')

class QuestionTagAdmin(admin.ModelAdmin):
    list_display = ('question', 'tag')
    list_display_links = ('question', 'tag')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(ReplyList, ReplyListAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(UserTag, UserTagAdmin)
admin.site.register(QuestionTag, QuestionTagAdmin)