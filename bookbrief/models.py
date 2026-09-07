"""
Book Summary Platform - Database models.
Structured summaries (quick, detailed, chapter-wise, etc.) with engagement and moderation.
"""
from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Category(models.Model):
    """Genre/category for books; used for filtering and SEO."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        db_table = "bookbrief_category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended user profile; contributor badge for high-quality summary writers."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_contributor = models.BooleanField(default=False)  # Badge for quality contributors
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookbrief_user_profile"

    def __str__(self):
        return self.display_name or self.user.username


class Book(models.Model):
    """Book entity - metadata. Summaries and reviews are separate."""
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [(STATUS_DRAFT, "Draft"), (STATUS_PUBLISHED, "Published")]

    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    isbn = models.CharField(max_length=20, blank=True, db_index=True)
    cover_image = models.ImageField(upload_to="covers/", blank=True, null=True)
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PUBLISHED,
        db_index=True,
    )
    view_count = models.PositiveIntegerField(default=0)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="added_books",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookbrief_book"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.title}-{self.author}"
            self.slug = slugify(base)[:350]
            # Ensure uniqueness
            orig = self.slug
            n = 0
            while Book.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                n += 1
                self.slug = f"{orig}-{n}"[:350]
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(avg=Avg("rating"))
        return round(agg["avg"] or 0, 1)

    @property
    def reviews_count(self):
        return self.reviews.count()


# Summary type choices - user selects when adding
SUMMARY_TYPE_QUICK = "quick"
SUMMARY_TYPE_DETAILED = "detailed"
SUMMARY_TYPE_CHAPTER = "chapter_wise"
SUMMARY_TYPE_BULLET = "bullet_points"
SUMMARY_TYPE_LESSONS = "key_lessons"
SUMMARY_TYPE_INSIGHTS = "actionable_insights"

SUMMARY_TYPE_CHOICES = [
    (SUMMARY_TYPE_QUICK, "Quick Summary (2–5 min read)"),
    (SUMMARY_TYPE_DETAILED, "Detailed Summary"),
    (SUMMARY_TYPE_CHAPTER, "Chapter-wise Summary"),
    (SUMMARY_TYPE_BULLET, "Bullet Point Summary"),
    (SUMMARY_TYPE_LESSONS, "Key Lessons"),
    (SUMMARY_TYPE_INSIGHTS, "Actionable Insights"),
]


class Summary(models.Model):
    """One summary per book per type per user (or allow multiple). Rich content, reading time, word count."""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="summaries",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summaries",
    )
    summary_type = models.CharField(max_length=20, choices=SUMMARY_TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=200, blank=True)  # Optional subtitle
    # Rich content: structured headings, formatting (store as HTML or Markdown; use TextField for now)
    content = models.TextField(help_text="Main summary content with headings and formatting.")
    # Quick preview for cards (first 2–5 lines)
    quick_preview = models.CharField(max_length=500, blank=True)
    # Point-wise key takeaways (optional)
    key_takeaways = models.TextField(blank=True, help_text="Bullet or point-wise key takeaways.")
    view_count = models.PositiveIntegerField(default=0)
    estimated_reading_minutes = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(120)],
    )
    word_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)  # Admin can feature
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookbrief_summary"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["book"]),
            models.Index(fields=["user"]),
            models.Index(fields=["summary_type"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["view_count"]),
        ]
        verbose_name_plural = "Summaries"

    def __str__(self):
        return f"{self.get_summary_type_display()} of '{self.book.title}' by {self.user.username}"

    def save(self, *args, **kwargs):
        if self.word_count == 0 and self.content:
            self.word_count = len(self.content.split())
        if not self.quick_preview and self.content:
            self.quick_preview = self.content[:500].strip()
        super().save(*args, **kwargs)


class Chapter(models.Model):
    """Chapter entry for chapter-wise summaries."""
    summary = models.ForeignKey(
        Summary,
        on_delete=models.CASCADE,
        related_name="chapters",
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "bookbrief_chapter"
        ordering = ["summary", "order"]

    def __str__(self):
        return f"{self.summary.book.title} – {self.title}"


class Review(models.Model):
    """User review/rating for a book."""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="book_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookbrief_review"
        ordering = ["-created_at"]
        unique_together = [["book", "user"]]

    def __str__(self):
        return f"{self.user.username} on {self.book.title}: {self.rating}"


class Report(models.Model):
    """Report on summary or review for moderation."""
    REPORT_SUMMARY = "summary"
    REPORT_REVIEW = "review"
    REPORT_CHOICES = [(REPORT_SUMMARY, "Summary"), (REPORT_REVIEW, "Review")]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports_made",
    )
    summary = models.ForeignKey(
        Summary,
        on_delete=models.CASCADE,
        related_name="summary_reports",
        null=True,
        blank=True,
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="review_reports",
        null=True,
        blank=True,
    )
    report_type = models.CharField(max_length=10, choices=REPORT_CHOICES, default=REPORT_SUMMARY)
    reason = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("resolved", "Resolved"), ("dismissed", "Dismissed")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bookbrief_report"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report on {self.report_type} by {self.reporter.username}"


class SummaryVote(models.Model):
    """Like (1) or Dislike (-1) on a summary; one vote per user per summary; toggle = remove."""
    VALUE_LIKE = 1
    VALUE_DISLIKE = -1
    VALUE_CHOICES = [(VALUE_LIKE, "Like"), (VALUE_DISLIKE, "Dislike")]

    summary = models.ForeignKey(
        Summary,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summary_votes",
    )
    value = models.SmallIntegerField(choices=VALUE_CHOICES)  # 1 or -1
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bookbrief_summary_vote"
        unique_together = [["summary", "user"]]

    def __str__(self):
        return f"{self.user.username} voted {self.value} on summary {self.summary_id}"


class BookSave(models.Model):
    """User saved a book (bookmark)."""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="saves",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_books",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bookbrief_book_save"
        unique_together = [["book", "user"]]

    def __str__(self):
        return f"{self.user.username} saved {self.book.title}"


class UserBookStatus(models.Model):
    """Track Read / Reading / Want to Read per user per book."""
    STATUS_WANT_TO_READ = "want_to_read"
    STATUS_READING = "reading"
    STATUS_READ = "read"
    STATUS_CHOICES = [
        (STATUS_WANT_TO_READ, "Want to Read"),
        (STATUS_READING, "Reading"),
        (STATUS_READ, "Read"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="book_statuses",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="user_statuses",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookbrief_user_book_status"
        unique_together = [["user", "book"]]
        verbose_name_plural = "User book statuses"

    def __str__(self):
        return f"{self.user.username} – {self.book.title}: {self.get_status_display()}"


class Comment(models.Model):
    """Threaded comment on a summary."""
    summary = models.ForeignKey(
        Summary,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summary_comments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookbrief_comment"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} on summary {self.summary_id}"
