from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from apps.interviews.models.questions import Question, QuestionContent

ContentFormSet = inlineformset_factory(
    Question, 
    QuestionContent, 
    fields=['content_type', 'title', 'content', 'content_roman', 'language', 'diagram_type', 'display_order'],
    extra=1,
    can_delete=True
)

class QuestionListView(LoginRequiredMixin, ListView):
    model = Question
    template_name = "interviews/question_list.html"
    context_object_name = "questions"
    paginate_by = 20

    def get_queryset(self):
        qs = Question.objects.filter(user=self.request.user)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(title__icontains=search)
        
        difficulty = self.request.GET.get('difficulty', '')
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
            
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
            
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['difficulty'] = self.request.GET.get('difficulty', '')
        context['status'] = self.request.GET.get('status', '')
        context['difficulties'] = Question.DifficultyChoices.choices
        context['statuses'] = Question.StatusChoices.choices
        return context

class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    template_name = "interviews/question_form.html"
    fields = ['title', 'question_type', 'difficulty', 'status']
    success_url = reverse_lazy('interviews:questions')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['content_formset'] = ContentFormSet(self.request.POST)
        else:
            data['content_formset'] = ContentFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        content_formset = context['content_formset']
        if content_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            content_formset.instance = self.object
            content_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class QuestionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Question
    template_name = "interviews/question_detail.html"
    context_object_name = "question"

    def test_func(self):
        return self.get_object().user == self.request.user

class QuestionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    template_name = "interviews/question_form.html"
    fields = ['title', 'question_type', 'difficulty', 'status']
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['content_formset'] = ContentFormSet(self.request.POST, instance=self.object)
        else:
            data['content_formset'] = ContentFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        content_formset = context['content_formset']
        if content_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            content_formset.instance = self.object
            content_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return reverse_lazy('interviews:question_detail', kwargs={'pk': self.object.pk})
