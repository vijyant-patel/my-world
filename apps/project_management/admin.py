from django.contrib import admin
from .models import (
    ProjectRole, Project, ProjectMember, Sprint, Task, TaskDependency,
    Issue, Comment, Attachment, WorkLink, Mention, PMAuditLog
)

@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'can_manage_project', 'can_manage_sprints', 'can_create_tasks')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'owner', 'start_date', 'end_date')
    list_filter = ('status', 'owner')
    search_fields = ('name',)

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role', 'joined_at')
    list_filter = ('project', 'role')

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'project')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'sprint', 'status', 'priority', 'task_type', 'reporter')
    list_filter = ('status', 'priority', 'task_type', 'project', 'sprint')
    search_fields = ('title',)

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'issue_type', 'severity', 'status', 'reporter', 'assignee')
    list_filter = ('status', 'severity', 'issue_type', 'project')
    search_fields = ('title',)

admin.site.register(TaskDependency)
admin.site.register(Comment)
admin.site.register(Attachment)
admin.site.register(WorkLink)
admin.site.register(Mention)
admin.site.register(PMAuditLog)
