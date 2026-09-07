from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.interviews.models.questions import RevisionTracker
import datetime

class RevisionQueueView(LoginRequiredMixin, ListView):
    model = RevisionTracker
    template_name = "interviews/revision_queue.html"
    context_object_name = "revisions"
    paginate_by = 20

    def get_queryset(self):
        today = datetime.date.today()
        # Fetch due revisions
        qs = RevisionTracker.objects.filter(
            question__user=self.request.user,
            next_revision_date__lte=today
        ).select_related('question')
        return qs.order_by('next_revision_date')
