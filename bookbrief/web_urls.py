"""
URL configuration for the web UI (Django templates).
API URLs remain in urls.py under /api/.
"""
from django.urls import path
from . import web_views

urlpatterns = [
    path("", web_views.HomeView.as_view(), name="home"),
    # Books
    path("books/", web_views.WebBookListView.as_view(), name="book_list"),
    path("books/add/", web_views.WebBookCreateView.as_view(), name="book_add"),
    path("books/<slug:slug>/", web_views.WebBookDetailView.as_view(), name="book_detail"),
    path("books/<slug:slug>/edit/", web_views.WebBookUpdateView.as_view(), name="book_edit"),
    path("books/<slug:slug>/delete/", web_views.WebBookDeleteView.as_view(), name="book_delete"),
    # Summaries
    path("summaries/", web_views.WebSummaryListView.as_view(), name="summary_list"),
    path("summaries/add/", web_views.WebSummaryCreateView.as_view(), name="summary_add"),
    path("summaries/<int:pk>/", web_views.WebSummaryDetailView.as_view(), name="summary_detail"),
    path("summaries/<int:pk>/edit/", web_views.WebSummaryUpdateView.as_view(), name="summary_edit"),
    path("summaries/<int:pk>/delete/", web_views.WebSummaryDeleteView.as_view(), name="summary_delete"),
    # Category
    path("category/<slug:slug>/", web_views.WebCategoryDetailView.as_view(), name="category_detail"),
    # Dashboard & profile
    path("dashboard/", web_views.WebDashboardView.as_view(), name="dashboard"),
    path("profile/", web_views.WebProfileView.as_view(), name="profile_edit"),
    # Register (web form; login/logout use django.contrib.auth.urls at /accounts/)
    path("register/", web_views.WebRegisterView.as_view(), name="register"),
]
