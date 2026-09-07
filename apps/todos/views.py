import json
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from .models import Todo, TodoList

class TodoDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'todos/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pre-load initial data for fast rendering
        context['todo_lists'] = TodoList.objects.filter(user=self.request.user).order_by('created_at')
        return context

class TodoAPIView(LoginRequiredMixin, View):
    def get(self, request):
        todos = Todo.objects.filter(user=request.user).order_by('-created_at')
        data = [{
            'id': t.id,
            'title': t.title,
            'notes': t.notes,
            'is_completed': t.is_completed,
            'priority': t.priority,
            'due_date': str(t.due_date) if t.due_date else None,
            'todo_list_id': t.todo_list_id,
            'created_at': t.created_at.isoformat()
        } for t in todos]
        return JsonResponse({'todos': data})

    def post(self, request):
        try:
            data = json.loads(request.body)
            todo = Todo.objects.create(
                user=request.user,
                title=data.get('title', '').strip(),
                todo_list_id=data.get('todo_list_id'),
                priority=data.get('priority', 'NONE'),
                due_date=data.get('due_date')
            )
            return JsonResponse({'status': 'success', 'todo': {
                'id': todo.id,
                'title': todo.title,
                'is_completed': todo.is_completed,
                'priority': todo.priority,
                'todo_list_id': todo.todo_list_id
            }})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def put(self, request, pk):
        try:
            data = json.loads(request.body)
            todo = Todo.objects.get(pk=pk, user=request.user)
            
            if 'is_completed' in data:
                todo.is_completed = data['is_completed']
                todo.completed_at = timezone.now() if todo.is_completed else None
            if 'title' in data:
                todo.title = data['title']
            if 'priority' in data:
                todo.priority = data['priority']
            if 'due_date' in data:
                todo.due_date = data['due_date']
            if 'notes' in data:
                todo.notes = data['notes']
            if 'todo_list_id' in data:
                todo.todo_list_id = data['todo_list_id']
                
            todo.save()
            return JsonResponse({'status': 'success'})
        except Todo.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Todo not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, pk):
        try:
            todo = Todo.objects.get(pk=pk, user=request.user)
            todo.delete()
            return JsonResponse({'status': 'success'})
        except Todo.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Todo not found'}, status=404)

class TodoListAPIView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            todo_list = TodoList.objects.create(
                user=request.user,
                name=data.get('name', 'New List').strip(),
                color=data.get('color', '#2563eb'),
                icon=data.get('icon', 'list')
            )
            return JsonResponse({'status': 'success', 'list': {
                'id': todo_list.id,
                'name': todo_list.name,
                'color': todo_list.color,
                'icon': todo_list.icon
            }})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, pk):
        try:
            todo_list = TodoList.objects.get(pk=pk, user=request.user)
            todo_list.delete()
            return JsonResponse({'status': 'success'})
        except TodoList.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'List not found'}, status=404)
