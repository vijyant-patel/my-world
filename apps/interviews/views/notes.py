from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.interviews.models.notes import Note

class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = "interviews/note_list.html"
    context_object_name = "notes"
    paginate_by = 20

    def get_queryset(self):
        qs = Note.objects.filter(user=self.request.user)
        return qs.order_by('-updated_at')
