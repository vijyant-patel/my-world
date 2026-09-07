from django.urls import path, include

from .views.dashboard import dashboard
from .views.questions import QuestionListView, QuestionCreateView, QuestionDetailView, QuestionUpdateView
from .views.experiences import InterviewListView
from .views.notes import NoteListView
from .views.revisions import RevisionQueueView

app_name = "interviews"

urlpatterns = [
    path("api/", include("apps.interviews.api.urls")),
    path("", dashboard, name="dashboard"),
    path("questions/", QuestionListView.as_view(), name="questions"),
    path("questions/add/", QuestionCreateView.as_view(), name="question_add"),
    path("questions/<int:pk>/", QuestionDetailView.as_view(), name="question_detail"),
    path("questions/<int:pk>/edit/", QuestionUpdateView.as_view(), name="question_edit"),
    path("experiences/", InterviewListView.as_view(), name="experiences"),
    path("notes/", NoteListView.as_view(), name="notes"),
    path("revisions/", RevisionQueueView.as_view(), name="revisions"),
]
