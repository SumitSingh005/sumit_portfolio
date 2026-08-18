from django.contrib import admin
from .models import ContactMessage, Project, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'github_link', 'demo_link')
    search_fields = ('title', 'description')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)


admin.site.site_header = 'AI Portfolio Admin'
admin.site.site_title = 'AI Portfolio'
admin.site.index_title = 'Dashboard'
