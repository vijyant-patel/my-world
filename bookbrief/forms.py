"""
Forms for Book Summary Platform - books, summaries, reviews.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Book, Summary, Chapter, Review, Comment, UserProfile, SUMMARY_TYPE_CHOICES

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    display_name = forms.CharField(max_length=100, required=False, label="Display name")

    class Meta:
        model = User
        fields = ("phone", "name", "email")


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("title", "author", "isbn", "cover_image", "category", "status")


class SummaryForm(forms.ModelForm):
    summary_type = forms.ChoiceField(choices=SUMMARY_TYPE_CHOICES, widget=forms.Select)

    class Meta:
        model = Summary
        fields = ("book", "summary_type", "title", "content", "quick_preview", "key_takeaways", "estimated_reading_minutes", "is_public")
        widgets = {
            "content": forms.Textarea(attrs={"rows": 12, "placeholder": "Use headings and paragraphs."}),
            "quick_preview": forms.Textarea(attrs={"rows": 2, "placeholder": "Short preview (2–5 lines) for cards."}),
            "key_takeaways": forms.Textarea(attrs={"rows": 4, "placeholder": "Point-wise key takeaways (optional)."}),
        }


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ("title", "content", "order")
        widgets = {
            "content": forms.Textarea(attrs={"rows": 6}),
        }


ChapterFormSet = forms.inlineformset_factory(
    Summary,
    Chapter,
    form=ChapterForm,
    extra=1,
    can_delete=True,
    max_num=50,
)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "body")
        widgets = {
            "rating": forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Your review (optional)."}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a comment..."})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("display_name", "bio", "avatar")
