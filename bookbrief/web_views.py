"""
Web UI views (Django templates). API views remain in views.py unchanged.
"""
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden

from .models import Book, Summary, Category, Review, Comment, UserProfile, UserBookStatus
from .forms import BookForm, SummaryForm, RegisterForm, ProfileForm, CommentForm, ReviewForm


# ---------- Home ----------
class HomeView(TemplateView):
    template_name = "bookbrief/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recent_books"] = (
            Book.objects.filter(status=Book.STATUS_PUBLISHED)
            .annotate(summary_count=Count("summaries", filter=Q(summaries__is_public=True)))
            .order_by("-created_at")[:8]
        )
        ctx["recent_summaries"] = (
            Summary.objects.filter(is_public=True)
            .select_related("book", "user")
            .order_by("-created_at")[:8]
        )
        return ctx


# ---------- Books (web) ----------
class WebBookListView(ListView):
    model = Book
    template_name = "bookbrief/book_list.html"
    context_object_name = "books"
    paginate_by = 24

    def get_queryset(self):
        qs = (
            Book.objects.filter(status=Book.STATUS_PUBLISHED)
            .select_related("category")
            .annotate(summary_count=Count("summaries", filter=Q(summaries__is_public=True)))
            .order_by("-created_at")
        )
        search = self.request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(author__icontains=search))
        cat = self.request.GET.get("category", "").strip()
        if cat:
            qs = qs.filter(category__slug=cat)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all().order_by("name")
        ctx["search_query"] = self.request.GET.get("search", "")
        ctx["selected_category"] = self.request.GET.get("category", "")
        return ctx


class WebBookDetailView(DetailView):
    model = Book
    template_name = "bookbrief/book_detail.html"
    context_object_name = "book"
    slug_url_kwarg = "slug"
    slug_field = "slug"

    def get_queryset(self):
        qs = Book.objects.select_related("category", "added_by")
        if self.request.user.is_authenticated:
            qs = qs.filter(
                Q(status=Book.STATUS_PUBLISHED) | Q(added_by=self.request.user)
            )
        else:
            qs = qs.filter(status=Book.STATUS_PUBLISHED)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        book = self.object
        ctx["summaries"] = book.summaries.filter(is_public=True).select_related("user")
        ctx["reviews"] = book.reviews.select_related("user").order_by("-created_at")
        ctx["user_review"] = None
        if self.request.user.is_authenticated:
            ctx["user_review"] = book.reviews.filter(user=self.request.user).first()
        ctx["review_form"] = ReviewForm() if self.request.user.is_authenticated else None
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect(reverse("login") + "?next=" + request.get_full_path())
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.update_or_create(
                book=self.object,
                user=request.user,
                defaults={"rating": form.cleaned_data["rating"], "body": form.cleaned_data.get("body") or ""},
            )
            return redirect("book_detail", slug=self.object.slug)
        ctx = self.get_context_data()
        ctx["review_form"] = form
        return render(request, self.template_name, ctx)


class WebBookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "bookbrief/book_form.html"
    success_url = reverse_lazy("book_list")

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        form.instance.status = Book.STATUS_PUBLISHED
        return super().form_valid(form)


class WebBookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "bookbrief/book_form.html"
    context_object_name = "object"
    slug_url_kwarg = "slug"
    slug_field = "slug"

    def test_func(self):
        book = self.get_object()
        return book.added_by_id == self.request.user.id or self.request.user.is_staff

    def get_success_url(self):
        return reverse("book_detail", kwargs={"slug": self.object.slug})


class WebBookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = "bookbrief/book_confirm_delete.html"
    slug_url_kwarg = "slug"
    slug_field = "slug"
    success_url = reverse_lazy("book_list")

    def test_func(self):
        book = self.get_object()
        return book.added_by_id == self.request.user.id or self.request.user.is_staff


# ---------- Summaries (web) ----------
class WebSummaryListView(ListView):
    model = Summary
    template_name = "bookbrief/summary_list.html"
    context_object_name = "summary_list"
    paginate_by = 24

    def get_queryset(self):
        qs = (
            Summary.objects.filter(is_public=True)
            .select_related("book", "user")
            .order_by("-created_at")
        )
        search = self.request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(content__icontains=search)
                | Q(quick_preview__icontains=search)
                | Q(book__title__icontains=search)
                | Q(book__author__icontains=search)
            )
        st = self.request.GET.get("type", "").strip()
        if st:
            qs = qs.filter(summary_type=st)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search_query"] = self.request.GET.get("search", "")
        ctx["filter_type"] = self.request.GET.get("type", "")
        return ctx


class WebSummaryDetailView(DetailView):
    model = Summary
    template_name = "bookbrief/summary_detail.html"
    context_object_name = "summary"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return Summary.objects.select_related("book", "user").prefetch_related("chapters")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        summary = self.object
        ctx["comments"] = summary.comments.filter(parent__isnull=True).select_related("user").prefetch_related("children")
        ctx["comment_form"] = CommentForm() if self.request.user.is_authenticated else None
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect(reverse("login") + "?next=" + request.get_full_path())
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                summary=self.object,
                user=request.user,
                body=form.cleaned_data["body"],
            )
            return redirect("summary_detail", pk=self.object.pk)
        ctx = self.get_context_data()
        ctx["comment_form"] = form
        return render(request, self.template_name, ctx)


class WebSummaryCreateView(LoginRequiredMixin, CreateView):
    model = Summary
    form_class = SummaryForm
    template_name = "bookbrief/summary_form.html"
    success_url = reverse_lazy("summary_list")

    def get_initial(self):
        initial = super().get_initial()
        book_id = self.request.GET.get("book")
        if book_id:
            initial["book"] = get_object_or_404(Book, pk=book_id)
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        book_id = self.request.GET.get("book")
        if book_id:
            ctx["book"] = get_object_or_404(Book, pk=book_id)
        return ctx

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class WebSummaryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Summary
    form_class = SummaryForm
    template_name = "bookbrief/summary_form.html"
    context_object_name = "object"
    pk_url_kwarg = "pk"

    def test_func(self):
        return self.get_object().user_id == self.request.user.id or self.request.user.is_staff

    def get_success_url(self):
        return reverse("summary_detail", kwargs={"pk": self.object.pk})


class WebSummaryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Summary
    template_name = "bookbrief/summary_confirm_delete.html"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("summary_list")

    def test_func(self):
        return self.get_object().user_id == self.request.user.id or self.request.user.is_staff


# ---------- Dashboard ----------
class WebDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "bookbrief/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["my_books"] = (
            Book.objects.filter(added_by=user)
            .annotate(summary_count=Count("summaries", filter=Q(summaries__is_public=True)))
            .order_by("-created_at")[:12]
        )
        ctx["my_summaries"] = (
            Summary.objects.filter(user=user).select_related("book").order_by("-created_at")[:12]
        )
        ctx["reading_statuses"] = (
            UserBookStatus.objects.filter(user=user).select_related("book").order_by("-updated_at")[:10]
        )
        return ctx


# ---------- Profile ----------
class WebProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = "bookbrief/profile.html"
    context_object_name = "profile"
    success_url = reverse_lazy("profile_edit")

    def get_object(self, queryset=None):
        obj, _ = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"display_name": self.request.user.name or self.request.user.phone},
        )
        return obj


# ---------- Register (web form; API register stays at /api/auth/register/) ----------
class WebRegisterView(FormView):
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        UserProfile.objects.get_or_create(
            user=user,
            defaults={"display_name": form.cleaned_data.get("display_name") or user.name},
        )
        login(self.request, user)
        return super().form_valid(form)


# ---------- Category (web) ----------
class WebCategoryDetailView(ListView):
    model = Book
    template_name = "bookbrief/category_detail.html"
    context_object_name = "books"
    paginate_by = 24

    def get_queryset(self):
        return (
            Book.objects.filter(category__slug=self.kwargs["slug"], status=Book.STATUS_PUBLISHED)
            .select_related("category")
            .annotate(summary_count=Count("summaries", filter=Q(summaries__is_public=True)))
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from .models import Category
        ctx["category"] = get_object_or_404(Category, slug=self.kwargs["slug"])
        return ctx
