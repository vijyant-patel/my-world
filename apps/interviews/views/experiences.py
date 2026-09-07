from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.interviews.models.experiences import Interview

class InterviewListView(LoginRequiredMixin, ListView):
    model = Interview
    template_name = "interviews/experience_list.html"
    context_object_name = "interviews"
    paginate_by = 20

    def get_queryset(self):
        qs = Interview.objects.filter(user=self.request.user).select_related('company')
        return qs.order_by('-interview_date')
