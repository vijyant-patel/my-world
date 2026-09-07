from django.db import models
from django.conf import settings

class TodoList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='todo_lists')
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, default='list')
    color = models.CharField(max_length=20, blank=True, default='#2563eb')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user})"

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('NONE', 'None'),
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='todos')
    todo_list = models.ForeignKey(TodoList, on_delete=models.SET_NULL, null=True, blank=True, related_name='todos')
    
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NONE')
    
    due_date = models.DateField(null=True, blank=True)
    due_time = models.TimeField(null=True, blank=True)
    
    # Simple strings for now to store standard values (e.g. "AT_TIME", "10_MIN_BEFORE", "DAILY", "WEEKLY")
    reminder = models.CharField(max_length=50, blank=True)
    recurrence = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
