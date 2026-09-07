from django.urls import path
from . import views

app_name = 'todos'

urlpatterns = [
    path('', views.TodoDashboardView.as_view(), name='dashboard'),
    path('api/todos/', views.TodoAPIView.as_view(), name='api_todos'),
    path('api/todos/<int:pk>/', views.TodoAPIView.as_view(), name='api_todo_detail'),
    path('api/lists/', views.TodoListAPIView.as_view(), name='api_lists'),
    path('api/lists/<int:pk>/', views.TodoListAPIView.as_view(), name='api_list_detail'),
]
