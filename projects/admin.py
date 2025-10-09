from django.contrib import admin
from .models import Project, Stage
class StageInline(admin.TabularInline):
    model = Stage
    extra = 1
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name","address")
    search_fields = ("name","address")
    inlines = [StageInline]
@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("name","project","start_date","end_date")
    list_filter = ("project",)
