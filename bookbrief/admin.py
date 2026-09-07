"""
Admin panel customization for Book Summary Platform.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Book, Summary, Chapter, UserProfile, Review, SummaryVote, UserBookStatus, Comment, Report


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "display_name", "created_at"]
    search_fields = ["user__username", "display_name"]
    raw_id_fields = ["user"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "status", "view_count", "added_by", "created_at", "summary_count_display"]
    list_filter = ["status", "category", "created_at"]
    search_fields = ["title", "author", "isbn"]
    raw_id_fields = ["added_by", "category"]
    date_hierarchy = "created_at"

    def summary_count_display(self, obj):
        count = obj.summaries.count()
        return format_html("<b>{}</b>", count)
    summary_count_display.short_description = "Summaries"


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ["book", "user", "summary_type", "is_public", "view_count", "created_at"]
    list_filter = ["is_public", "summary_type", "created_at"]
    search_fields = ["content", "quick_preview", "key_takeaways", "book__title", "user__username"]
    raw_id_fields = ["book", "user"]
    date_hierarchy = "created_at"
    inlines = [ChapterInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["book", "user", "rating", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["body", "book__title", "user__username"]
    raw_id_fields = ["book", "user"]


@admin.register(SummaryVote)
class SummaryVoteAdmin(admin.ModelAdmin):
    list_display = ["summary", "user", "value", "created_at"]
    list_filter = ["value"]
    raw_id_fields = ["summary", "user"]


@admin.register(UserBookStatus)
class UserBookStatusAdmin(admin.ModelAdmin):
    list_display = ["user", "book", "status", "updated_at"]
    list_filter = ["status"]
    raw_id_fields = ["user", "book"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["summary", "user", "parent", "created_at"]
    search_fields = ["body"]
    raw_id_fields = ["summary", "user", "parent"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["reporter", "report_type", "summary", "review", "status", "created_at"]
    list_filter = ["report_type", "status", "created_at"]
    search_fields = ["reason"]
    raw_id_fields = ["reporter", "summary", "review"]
    date_hierarchy = "created_at"
