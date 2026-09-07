from django import forms
from django.contrib.auth import get_user_model
from .models import Sprint, Project, Task, Issue, WorkLink, Comment

User = get_user_model()

class DateInput(forms.DateInput):
    input_type = 'date'

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name if getattr(obj, 'name', None) else str(obj)

class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name if getattr(obj, 'name', None) else str(obj)

class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['name', 'goal', 'start_date', 'end_date', 'status']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'start_date', 'end_date']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }

class TaskForm(forms.ModelForm):
    assignees = UserModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Task
        fields = ['sprint', 'title', 'description', 'task_type', 'priority', 'status', 'story_points', 'due_date', 'assignees']
        widgets = {
            'due_date': DateInput(),
        }

class IssueForm(forms.ModelForm):
    assignee = UserModelChoiceField(
        queryset=User.objects.all(),
        required=False
    )
    class Meta:
        model = Issue
        fields = ['sprint', 'linked_task', 'title', 'description', 'reproduction_steps', 'issue_type', 'severity', 'status', 'assignee']

class WorkLinkForm(forms.ModelForm):
    class Meta:
        model = WorkLink
        fields = ['url', 'title', 'link_type']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a comment... (You can drop git links here)'})
        }
