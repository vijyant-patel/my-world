"""
DRF serializers for Book Summary Platform API.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Book, Summary, UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "username", "display_name", "bio", "avatar", "created_at"]


class UserBriefSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "display_name"]

    def get_display_name(self, obj):
        try:
            return obj.profile.display_name or obj.username
        except UserProfile.DoesNotExist:
            return obj.username


class BookListSerializer(serializers.ModelSerializer):
    summary_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "slug", "isbn", "cover_image",
            "category", "status", "view_count", "added_by", "created_at", "summary_count",
        ]

    def get_summary_count(self, obj):
        return obj.summaries.filter(is_public=True).count()


class BookDetailSerializer(serializers.ModelSerializer):
    summaries = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "slug", "isbn", "cover_image",
            "category", "status", "view_count", "added_by", "created_at", "summaries",
        ]

    def get_summaries(self, obj):
        qs = obj.summaries.filter(is_public=True).select_related("user")
        return SummaryListSerializer(qs, many=True).data


class SummaryListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_author = serializers.CharField(source="book.author", read_only=True)
    author_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Summary
        fields = [
            "id", "book", "book_title", "book_author", "author_username",
            "summary_type", "title", "content", "quick_preview", "key_takeaways",
            "estimated_reading_minutes", "word_count", "is_public", "view_count",
            "created_at", "updated_at",
        ]


class SummaryDetailSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    author_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Summary
        fields = [
            "id", "book", "author_username", "summary_type", "title",
            "content", "quick_preview", "key_takeaways",
            "estimated_reading_minutes", "word_count", "is_public", "view_count",
            "created_at", "updated_at",
        ]


class SummaryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = [
            "book", "summary_type", "title", "content", "quick_preview", "key_takeaways",
            "estimated_reading_minutes", "is_public",
        ]

    def validate_content(self, value):
        if value and len(value) < 50:
            raise serializers.ValidationError("Content should be at least 50 characters.")
        return value


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["title", "author", "slug", "isbn", "cover_image", "category", "status"]
