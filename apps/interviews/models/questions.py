from django.db import models
from django.conf import settings
from django.utils.text import slugify
from .core import TimeStampedModel, Category, Tag
from .experiences import Company, InterviewRound

class Question(TimeStampedModel):
    class DifficultyChoices(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    class StatusChoices(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        LEARNING = "learning", "Learning"
        REVISED = "revised", "Revised"
        MASTERED = "mastered", "Mastered"

    class QuestionTypeChoices(models.TextChoices):
        THEORY = "theory", "Theory"
        HR = "hr", "HR"
        CODING = "coding", "Coding"
        SYSTEM_DESIGN = "system_design", "System Design"
        SCENARIO = "scenario", "Scenario"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    question_type = models.CharField(max_length=20, choices=QuestionTypeChoices.choices, default=QuestionTypeChoices.THEORY)
    
    difficulty = models.CharField(max_length=10, choices=DifficultyChoices.choices, default=DifficultyChoices.MEDIUM)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NOT_STARTED)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions")
    tags = models.ManyToManyField(Tag, blank=True, related_name="questions")
    companies = models.ManyToManyField(Company, blank=True, related_name="questions", help_text="Companies that ask this")
    interview_rounds = models.ManyToManyField(InterviewRound, blank=True, related_name="asked_questions")
    
    is_favorite = models.BooleanField(default=False)
    source = models.URLField(blank=True, help_text="Link to LeetCode, Article, etc.")
    interview_frequency = models.PositiveIntegerField(default=0, help_text="How often asked")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            import uuid
            self.slug = slugify(self.title) + "-" + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

class QuestionContent(TimeStampedModel):
    class ContentTypeChoices(models.TextChoices):
        PROBLEM_STATEMENT = "problem_statement", "Problem Statement"
        QUICK_ANSWER = "quick_answer", "Quick Answer"
        DEEP_DIVE = "deep_dive", "Deep Dive"
        PERSONAL_NOTE = "personal_note", "Personal Note"
        BEGINNER_CODE = "beginner_code", "Beginner Code"
        OPTIMIZED_CODE = "optimized_code", "Optimized Code"
        PRODUCTION_CODE = "production_code", "Production Code"
        DIAGRAM = "diagram", "Diagram"
        ARCHITECTURE = "architecture", "Architecture Note"
        INTERVIEW_TIP = "interview_tip", "Interview Tip"
        FOLLOW_UP = "follow_up", "Follow-up Question"
        DEBUGGING = "debugging", "Debugging Tip"
        OPTIMIZATION = "optimization", "Optimization Note"
        USE_CASE = "use_case", "Use Case"
        ANTI_PATTERN = "anti_pattern", "Anti-Pattern"
        REVISION_NOTE = "revision_note", "Revision Note"
        FLASHCARD = "flashcard", "Flashcard"
        CHEAT_SHEET = "cheat_sheet", "Cheat Sheet"

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="contents")
    content_type = models.CharField(max_length=30, choices=ContentTypeChoices.choices)
    title = models.CharField(max_length=255, blank=True, help_text="Optional section title")
    content = models.TextField(help_text="Markdown content")
    content_roman = models.TextField(blank=True, help_text="Markdown content in Roman English / Hinglish")
    language = models.CharField(max_length=50, blank=True, help_text="e.g. python, javascript (for code)")
    diagram_type = models.CharField(max_length=50, blank=True, help_text="e.g. mermaid (for diagrams)")
    display_order = models.PositiveIntegerField(default=0)
    is_ai_generated = models.BooleanField(default=False)
    metadata_json = models.TextField(blank=True, help_text="JSON serialized metadata")

    class Meta:
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return f"{self.get_content_type_display()} for {self.question.title}"

    def save(self, *args, **kwargs):
        if self.content and not self.content_roman:
            import asyncio
            import sys
            from googletrans import Translator

            async def run_translation():
                try:
                    translator = Translator()
                    res = await translator.translate(self.content, dest='hi')
                    translations = res.extra_data.get('translation', [])
                    for item in translations:
                        if isinstance(item, list) and len(item) >= 3 and isinstance(item[2], str):
                            return item[2].replace('।', '.')
                except Exception:
                    pass
                return None

            try:
                if sys.platform == 'win32':
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                roman_text = loop.run_until_complete(run_translation())
                loop.close()
                if roman_text:
                    self.content_roman = roman_text
            except Exception:
                pass

        super().save(*args, **kwargs)

class CodingProblem(TimeStampedModel):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="coding_details")
    constraints = models.TextField(blank=True)
    examples = models.TextField(blank=True)
    time_complexity = models.CharField(max_length=100, blank=True)
    space_complexity = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=50, default="python")
    
    def __str__(self):
        return f"Coding details for: {self.question.title}"

class RevisionTracker(TimeStampedModel):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="revision_tracker")
    next_revision_date = models.DateField(null=True, blank=True)
    last_revised_date = models.DateField(null=True, blank=True)
    revision_streak = models.PositiveIntegerField(default=0)
    ease_factor = models.FloatField(default=2.5, help_text="SuperMemo-2 style ease factor")
    interval_days = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Revision for: {self.question.title}"
