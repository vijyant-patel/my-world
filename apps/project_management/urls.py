from django.urls import path
from . import views

app_name = 'project_management'

urlpatterns = [
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    
    path('projects/<int:project_id>/sprints/create/', views.SprintCreateView.as_view(), name='sprint_create'),
    path('sprints/<int:pk>/', views.SprintDetailView.as_view(), name='sprint_detail'),
    path('sprints/<int:pk>/update/', views.SprintUpdateView.as_view(), name='sprint_update'),
    path('projects/<int:project_id>/tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('projects/<int:project_id>/issues/create/', views.IssueCreateView.as_view(), name='issue_create'),
    path('issues/<int:pk>/', views.IssueDetailView.as_view(), name='issue_detail'),
    path('issues/<int:pk>/update/', views.IssueUpdateView.as_view(), name='issue_update'),
    
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:task_id>/checklist/add/', views.TaskChecklistCreateView.as_view(), name='task_checklist_create'),
    path('checklists/<int:pk>/toggle/', views.TaskChecklistToggleView.as_view(), name='task_checklist_toggle'),
    path('tasks/<int:task_id>/links/add/', views.WorkLinkCreateView.as_view(), name='work_link_create'),
    path('tasks/<int:task_id>/comments/add/', views.TaskCommentCreateView.as_view(), name='task_comment_create'),
    path('tasks/<int:task_id>/start_timer/', views.TaskWorkLogStartView.as_view(), name='task_worklog_start'),
    path('tasks/<int:task_id>/stop_timer/', views.TaskWorkLogStopView.as_view(), name='task_worklog_stop'),
]
