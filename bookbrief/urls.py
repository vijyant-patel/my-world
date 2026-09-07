"""
Bookbrief app URL configuration.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = "bookbrief"

urlpatterns = [
    # Auth
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Books
    path("books/", views.BookListCreateView.as_view(), name="book-list-create"),
    path("books/<slug:slug>/", views.BookDetailView.as_view(), name="book-detail"),
    path("books/my/", views.MyBooksView.as_view(), name="my-books"),
    # Summaries
    path("summaries/", views.SummaryListCreateView.as_view(), name="summary-list-create"),
    path("summaries/<int:pk>/", views.SummaryDetailView.as_view(), name="summary-detail"),
    path("summaries/my/", views.MySummariesView.as_view(), name="my-summaries"),
    # Profile
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
