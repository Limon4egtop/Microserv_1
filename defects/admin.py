from django.contrib import admin
from .models import Defect, Comment, Attachment, History


class AttachmentInline(admin.TabularInline):
    model = Attachment;
    extra = 0


class CommentInline(admin.TabularInline):
    model = Comment;
    extra = 0


@admin.register(Defect)
class DefectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "project", "stage", "priority", "status", "assignee", "due_date", "created_at")
    list_filter = ("project", "status", "priority", "assignee")
    search_fields = ("title", "description")
    inlines = [AttachmentInline, CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("defect", "author", "created_at")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("defect", "file", "uploaded_by", "uploaded_at")


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("defect", "field", "old_value", "new_value", "changed_by", "changed_at")
    list_filter = ("field",)
