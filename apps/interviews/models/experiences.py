from django.db import models
from django.conf import settings
from .core import TimeStampedModel

class Company(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Interview(TimeStampedModel):
    class ModeChoices(models.TextChoices):
        ONLINE = "online", "Online"
        OFFLINE = "offline", "Offline"

    class ResultChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        SELECTED = "selected", "Selected"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interviews")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="interviews")
    role = models.CharField(max_length=150)
    job_description = models.TextField(blank=True)
    interview_date = models.DateField()
    mode = models.CharField(max_length=20, choices=ModeChoices.choices, default=ModeChoices.ONLINE)
    result = models.CharField(max_length=20, choices=ResultChoices.choices, default=ResultChoices.PENDING)
    ctc_offered = models.CharField(max_length=100, blank=True, help_text="e.g., 30 LPA")
    notes = models.TextField(blank=True)
    overall_experience = models.TextField(blank=True)
    difficulty_level = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    
    class Meta:
        ordering = ["-interview_date"]

    def __str__(self):
        return f"{self.role} at {self.company.name} ({self.interview_date})"

class InterviewRound(TimeStampedModel):
    class RoundTypeChoices(models.TextChoices):
        DSA = "dsa", "DSA"
        SYSTEM_DESIGN = "system_design", "System Design"
        HR = "hr", "HR"
        DEVOPS = "devops", "DevOps"
        BACKEND = "backend", "Backend"
        FRONTEND = "frontend", "Frontend"
        MACHINE_CODING = "machine_coding", "Machine Coding"
        MANAGERIAL = "managerial", "Managerial"
        BEHAVIORAL = "behavioral", "Behavioral"
        OTHER = "other", "Other"

    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="rounds")
    name = models.CharField(max_length=100, help_text="e.g., Technical Round 1")
    round_type = models.CharField(max_length=30, choices=RoundTypeChoices.choices, default=RoundTypeChoices.DSA)
    feedback = models.TextField(blank=True)
    my_performance = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    duration_minutes = models.PositiveIntegerField(default=60)
    
    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name} - {self.interview.company.name}"
