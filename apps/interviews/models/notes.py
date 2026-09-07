from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .core import TimeStampedModel, Tag

class Note(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interview_notes")
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Markdown supported content.")
    
    # Generic relation to attach note to Question, Interview, or Category
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    
    tags = models.ManyToManyField(Tag, blank=True, related_name="notes")
    is_bookmarked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title
