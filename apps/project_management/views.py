from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from .models import Project, Sprint, Task, Issue, ChecklistItem, WorkLink, Comment, PMAuditLog
from .forms import ProjectForm, SprintForm, TaskForm, IssueForm, WorkLinkForm, CommentForm

def log_audit(user, instance, action):
    PMAuditLog.objects.create(
        user=user,
        action=action,
        content_type=ContentType.objects.get_for_model(instance.__class__),
        object_id=instance.pk
    )

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'project_management/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(members__user=user)
        ).distinct().order_by('-created_at')

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_management/project_form.html'
    success_url = reverse_lazy('project_management:project_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        log_audit(self.request.user, self.object, "Project created")
        return response

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'project_management/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context['sprints'] = project.sprints.all().order_by('-start_date')
        context['tasks'] = project.tasks.all().order_by('-created_at')
        context['issues'] = project.issues.all().order_by('-created_at')
        context['members'] = project.members.select_related('user', 'role').all()
        return context

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_management/project_form.html'
    
    def form_valid(self, form):
        if form.has_changed() and 'status' in form.changed_data:
            old = dict(form.fields['status'].choices).get(form.initial.get('status'), form.initial.get('status'))
            new = dict(form.fields['status'].choices).get(form.cleaned_data.get('status'), form.cleaned_data.get('status'))
            log_audit(self.request.user, self.object, f"Status changed from '{old}' to '{new}'")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project_management:project_detail', kwargs={'pk': self.object.pk})

class SprintCreateView(LoginRequiredMixin, CreateView):
    model = Sprint
    form_class = SprintForm
    template_name = 'project_management/sprint_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        form.instance.project = project
        response = super().form_valid(form)
        log_audit(self.request.user, self.object, f"Sprint created with status '{self.object.get_status_display()}'")
        return response

    def get_success_url(self):
        return reverse_lazy('project_management:sprint_detail', kwargs={'pk': self.object.pk})

class SprintDetailView(LoginRequiredMixin, DetailView):
    model = Sprint
    template_name = 'project_management/sprint_detail.html'
    context_object_name = 'sprint'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['audit_logs'] = PMAuditLog.objects.filter(
            content_type=ContentType.objects.get_for_model(Sprint),
            object_id=self.object.pk
        ).select_related('user').order_by('-timestamp')
        return context

class SprintUpdateView(LoginRequiredMixin, UpdateView):
    model = Sprint
    form_class = SprintForm
    template_name = 'project_management/sprint_form.html'

    def form_valid(self, form):
        if form.has_changed() and 'status' in form.changed_data:
            old = dict(form.fields['status'].choices).get(form.initial.get('status'), form.initial.get('status'))
            new = dict(form.fields['status'].choices).get(form.cleaned_data.get('status'), form.cleaned_data.get('status'))
            log_audit(self.request.user, self.object, f"Status changed from '{old}' to '{new}'")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project_management:sprint_detail', kwargs={'pk': self.object.pk})

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'project_management/task_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        form.instance.project = project
        form.instance.reporter = self.request.user
        response = super().form_valid(form)
        log_audit(self.request.user, self.object, f"Task created with status '{self.object.get_status_display()}'")
        return response

    def get_success_url(self):
        return reverse_lazy('project_management:task_detail', kwargs={'pk': self.object.pk})

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'project_management/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context['checklists'] = task.checklists.all().order_by('created_at')
        context['work_links'] = WorkLink.objects.filter(
            content_type=ContentType.objects.get_for_model(Task), 
            object_id=task.pk
        ).order_by('-created_at')
        context['work_link_form'] = WorkLinkForm()
        
        context['comments'] = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(Task),
            object_id=task.pk
        ).order_by('created_at')
        context['comment_form'] = CommentForm()

        # Audit Logs
        context['audit_logs'] = PMAuditLog.objects.filter(
            content_type=ContentType.objects.get_for_model(Task),
            object_id=task.pk
        ).select_related('user').order_by('-timestamp')
        
        # Time Tracking
        from .models import WorkLog
        from django.utils import timezone
        
        context['work_logs'] = WorkLog.objects.filter(task=task, end_time__isnull=False).order_by('-end_time')
        context['active_work_log'] = WorkLog.objects.filter(task=task, user=self.request.user, end_time__isnull=True).first()

        return context

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'project_management/task_form.html'

    def form_valid(self, form):
        if form.has_changed() and 'status' in form.changed_data:
            old = dict(form.fields['status'].choices).get(form.initial.get('status'), form.initial.get('status'))
            new = dict(form.fields['status'].choices).get(form.cleaned_data.get('status'), form.cleaned_data.get('status'))
            log_audit(self.request.user, self.object, f"Status changed from '{old}' to '{new}'")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project_management:task_detail', kwargs={'pk': self.object.pk})

class IssueCreateView(LoginRequiredMixin, CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'project_management/issue_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        form.instance.project = project
        form.instance.reporter = self.request.user
        response = super().form_valid(form)
        log_audit(self.request.user, self.object, f"Issue created with status '{self.object.get_status_display()}'")
        return response

    def get_success_url(self):
        return reverse_lazy('project_management:issue_detail', kwargs={'pk': self.object.pk})

class IssueDetailView(LoginRequiredMixin, DetailView):
    model = Issue
    template_name = 'project_management/issue_detail.html'
    context_object_name = 'issue'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['audit_logs'] = PMAuditLog.objects.filter(
            content_type=ContentType.objects.get_for_model(Issue),
            object_id=self.object.pk
        ).select_related('user').order_by('-timestamp')
        return context

class IssueUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = 'project_management/issue_form.html'

    def form_valid(self, form):
        if form.has_changed() and 'status' in form.changed_data:
            old = dict(form.fields['status'].choices).get(form.initial.get('status'), form.initial.get('status'))
            new = dict(form.fields['status'].choices).get(form.cleaned_data.get('status'), form.cleaned_data.get('status'))
            log_audit(self.request.user, self.object, f"Status changed from '{old}' to '{new}'")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project_management:issue_detail', kwargs={'pk': self.object.pk})

class TaskChecklistCreateView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        content = request.POST.get('content')
        if content:
            ChecklistItem.objects.create(task=task, content=content)
        return redirect('project_management:task_detail', pk=task_id)

class TaskChecklistToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(ChecklistItem, pk=pk)
        item.is_done = not item.is_done
        item.save()
        return redirect('project_management:task_detail', pk=item.task.pk)

class WorkLinkCreateView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        form = WorkLinkForm(request.POST)
        if form.is_valid():
            work_link = form.save(commit=False)
            work_link.content_type = ContentType.objects.get_for_model(Task)
            work_link.object_id = task.pk
            work_link.added_by = request.user
            work_link.save()
        return redirect('project_management:task_detail', pk=task_id)

        return reverse_lazy('project_management:project_detail', kwargs={'pk': self.object.project.pk})

class IssueUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = 'project_management/issue_form.html'

    def get_success_url(self):
        return reverse_lazy('project_management:project_detail', kwargs={'pk': self.object.project.pk})

class TaskCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.content_type = ContentType.objects.get_for_model(Task)
            comment.object_id = task.pk
            comment.author = request.user
            comment.save()
        return redirect('project_management:task_detail', pk=task_id)

class TaskWorkLogStartView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        from .models import WorkLog
        task = get_object_or_404(Task, pk=task_id)
        # Prevent multiple active logs for same user and task
        if not WorkLog.objects.filter(task=task, user=request.user, end_time__isnull=True).exists():
            WorkLog.objects.create(task=task, user=request.user)
        return redirect('project_management:task_detail', pk=task_id)

class TaskWorkLogStopView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        from .models import WorkLog
        from django.utils import timezone
        task = get_object_or_404(Task, pk=task_id)
        active_log = WorkLog.objects.filter(task=task, user=request.user, end_time__isnull=True).first()
        
        if active_log:
            active_log.end_time = timezone.now()
            active_log.comment = request.POST.get('comment', '')
            active_log.save()
        return redirect('project_management:task_detail', pk=task_id)
