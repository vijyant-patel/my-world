"""
REST API views for Book Summary Platform.
Web UI views are in web_views.py (templates); API remains here.
"""
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from .models import Book, Summary, UserProfile
from .serializers import (
    BookListSerializer,
    BookDetailSerializer,
    BookCreateSerializer,
    SummaryListSerializer,
    SummaryDetailSerializer,
    SummaryCreateUpdateSerializer,
    UserProfileSerializer,
)
from .permissions import IsBookSummaryOwner, IsAuthenticatedOrReadOnlyForPublic
from .filters import BookFilter, BookSummaryFilter

User = get_user_model()


# ---------- Auth (API) ----------
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")
        if not username or not password:
            return Response(
                {"error": "username and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.create_user(username=username, password=password, email=email)
        UserProfile.objects.get_or_create(user=user, defaults={"display_name": username})
        return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)


# ---------- Books ----------
class BookListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnlyForPublic]

    def get_queryset(self):
        qs = Book.objects.all().select_related("category", "added_by").order_by("-created_at")
        if not self.request.user.is_authenticated:
            qs = qs.filter(status=Book.STATUS_PUBLISHED)
        else:
            from django.db.models import Q
            qs = qs.filter(Q(status=Book.STATUS_PUBLISHED) | Q(added_by=self.request.user))
        return qs
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ["title", "author", "isbn"]
    ordering_fields = ["created_at", "title", "author"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BookCreateSerializer
        return BookListSerializer

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all().select_related("category", "added_by")
    serializer_class = BookDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


# ---------- Summaries ----------
class SummaryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnlyForPublic]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookSummaryFilter
    search_fields = ["content", "quick_preview", "key_takeaways", "book__title", "book__author"]
    ordering_fields = ["created_at", "updated_at", "view_count"]

    def get_queryset(self):
        return Summary.objects.filter(is_public=True).select_related("book", "user")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SummaryCreateUpdateSerializer
        return SummaryListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SummaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsBookSummaryOwner]
    queryset = Summary.objects.all().select_related("book", "user")

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return SummaryCreateUpdateSerializer
        return SummaryDetailSerializer


class MySummariesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummaryListSerializer

    def get_queryset(self):
        return Summary.objects.filter(user=self.request.user).select_related("book").order_by("-created_at")


class MyBooksView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookListSerializer

    def get_queryset(self):
        return Book.objects.filter(added_by=self.request.user).order_by("-created_at")


# ---------- User Profile ----------
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"display_name": self.request.user.username},
        )
        return profile
