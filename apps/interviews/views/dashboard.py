from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.interviews.models import Question, Interview, RevisionTracker, Category

@login_required
def dashboard(request):
    user = request.user
    
    # Stats
    total_interviews = Interview.objects.filter(user=user).count()
    total_questions = Question.objects.filter(user=user).count()
    
    # Revisions Pending (simplified for MVP: next_revision_date <= today or null)
    from django.utils import timezone
    today = timezone.now().date()
    revisions_pending = RevisionTracker.objects.filter(
        question__user=user, 
        next_revision_date__lte=today
    ).count() + RevisionTracker.objects.filter(
        question__user=user, 
        next_revision_date__isnull=True
    ).count()

    # Mastered Questions
    mastered_questions = Question.objects.filter(user=user, status=Question.StatusChoices.MASTERED).count()

    # Recent Questions
    recent_questions = Question.objects.filter(user=user).order_by('-created_at')[:5]

    context = {
        "total_interviews": total_interviews,
        "total_questions": total_questions,
        "revisions_pending": revisions_pending,
        "mastered_questions": mastered_questions,
        "recent_questions": recent_questions,
    }
    
    return render(request, "interviews/dashboard.html", context)
