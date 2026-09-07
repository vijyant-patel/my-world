# Book Summary Platform – Frontend Design (Django/Jinja Templates)

## 1. Template Folder Structure

```
templates/
├── base.html
├── 404.html
├── 403.html
├── 500.html
├── registration/
│   ├── login.html
│   ├── register.html
│   └── logged_out.html
└── bookbrief/
    ├── home.html
    ├── book_list.html
    ├── book_detail.html
    ├── book_form.html
    ├── summary_list.html
    ├── summary_detail.html
    ├── summary_form.html
    ├── category_detail.html
    ├── dashboard.html
    ├── profile.html
    └── components/
        ├── _book_card.html
        ├── _summary_card.html
        ├── _pagination.html
        ├── _comment.html
        ├── _review_form.html
        └── _search_filter.html
```

---

## 2. Base Template & Block Hierarchy

**base.html** defines:

| Block | Purpose |
|-------|---------|
| `title` | Page title (default: "BookBrief – Book Summary Platform") |
| `meta_description` | Optional meta description for SEO |
| `extra_css` | Page-specific styles (optional) |
| `content` | Main page content (required) |
| `extra_js` | Page-specific scripts (optional) |

**Extension chain:** Every page extends `base.html` and overrides `title` and `content`; optionally `meta_description`, `extra_css`, `extra_js`.

---

## 3. View → Template → Context Mapping

| View (required) | Template | Main context variables |
|-----------------|----------|------------------------|
| HomeView | bookbrief/home.html | `recent_books`, `recent_summaries` |
| BookListView | bookbrief/book_list.html | `page_obj` (paginated), `books`, `categories`, `search_query`, `selected_category` |
| BookDetailView | bookbrief/book_detail.html | `book`, `summaries` (public), `reviews`, `user_review`, `user_status` |
| BookCreateView / BookUpdateView | bookbrief/book_form.html | `form`, `object` (edit only) |
| SummaryListView | bookbrief/summary_list.html | `page_obj`, `summary_list`, `search_query`, `filter_type` |
| SummaryDetailView | bookbrief/summary_detail.html | `summary`, `book`, `comments`, `user_vote`, `likes_count`, `dislikes_count` |
| SummaryCreateView / SummaryUpdateView | bookbrief/summary_form.html | `form`, `book` (add), `object` (edit) |
| CategoryDetailView | bookbrief/category_detail.html | `category`, `page_obj`, `books` |
| DashboardView | bookbrief/dashboard.html | `my_books`, `my_summaries`, `reading_statuses` |
| LoginView | registration/login.html | `form`, `next` |
| RegisterView (GET/POST) | registration/register.html | `form` |
| LogoutView | registration/logged_out.html | (none) |
| ProfileView | bookbrief/profile.html | `form`, `profile` |
| 404/403/500 | 404.html, 403.html, 500.html | (request context) |

---

## 4. URL → Template (Navigation)

| URL name | Path (current) | Template |
|----------|----------------|----------|
| home | / | home.html |
| bookbrief:book-list-create | /api/books/ | book_list.html (when HTML view added) |
| bookbrief:book-detail | /api/books/<slug>/ | book_detail.html (when HTML view added) |
| bookbrief:summary-list-create | /api/summaries/ | summary_list.html (when HTML view added) |
| bookbrief:summary-detail | /api/summaries/<pk>/ | summary_detail.html (when HTML view added) |
| bookbrief:my-books | /api/books/my/ | (API; dashboard uses this data) |
| bookbrief:my-summaries | /api/summaries/my/ | (API; dashboard uses this data) |
| bookbrief:profile | /api/profile/ | profile.html (when HTML view added) |
| bookbrief:register | /api/auth/register/ | register.html (when GET form view added) |
| login | /accounts/login/ | registration/login.html |
| logout | /accounts/logout/ | registration/logged_out.html |

**Note:** The app currently exposes JSON at `/api/`. To serve the HTML templates above, add template-rendering views (e.g. `ListView`, `DetailView`, `FormView`) and either mount them at separate paths (e.g. `/books/`, `/summaries/`) or add content negotiation to existing API views.

---

## 5. Reusable Components (Include Usage)

| Component | Include | Passed context |
|-----------|---------|----------------|
| _book_card.html | `{% include "bookbrief/components/_book_card.html" with book=book %}` | `book` |
| _summary_card.html | `{% include "bookbrief/components/_summary_card.html" with summary=s %}` | `summary` |
| _pagination.html | `{% include "bookbrief/components/_pagination.html" with page_obj=page_obj %}` | `page_obj` |
| _comment.html | `{% include "bookbrief/components/_comment.html" with comment=c %}` (recursive for replies) | `comment` |
| _search_filter.html | `{% include "bookbrief/components/_search_filter.html" %}` | (uses request.GET) |

---

## 6. Conditionals (Logged-in vs Anonymous)

- **Nav:** Show "Login / Register" when `user.is_authenticated` is False; show "Dashboard", "My Books", "My Summaries", "Profile", "Logout" when True.
- **Book detail:** Show "Edit" / "Add summary" only if `user.is_authenticated` and (`book.added_by == user` or staff).
- **Summary detail:** Show "Edit" only if `user == summary.user`; show "Like/Dislike" and "Comment" only if authenticated.
- **Forms (add book, add summary):** Require login; redirect to login with `?next=`.

---

## 7. Loops & Backend Data

- **Books:** `{% for book in books %}` or `{% for book in page_obj %}` — each `book` has: `title`, `author`, `slug`, `cover_image`, `category`, `category.name`, `summary_count` (or annotate), `average_rating`, `reviews_count`.
- **Summaries:** `{% for summary in summary_list %}` — each `summary` has: `id`, `book`, `book.title`, `book.author`, `user`, `user.username`, `summary_type`, `get_summary_type_display`, `quick_preview`, `content`, `key_takeaways`, `estimated_reading_minutes`, `view_count`, `created_at`.
- **Comments:** `{% for comment in summary.comments.all %}` filtered by `parent__isnull=True` for top-level; recurse with `comment.children.all` in `_comment.html`.
- **Reviews:** `{% for review in book.reviews.all %}` — `review.user`, `review.rating`, `review.body`, `review.created_at`.

---

## 8. Forms Usage

- **Login:** `{{ form.as_p }}` or manual fields: `form.username`, `form.password`, `form.errors`. POST to `{% url 'login' %}` with `next={{ request.GET.next }}`.
- **Register:** `form.username`, `form.email`, `form.password1`, `form.password2`, `form.errors`. POST to `{% url 'bookbrief:register' %}`.
- **Book form (add/edit):** `form.title`, `form.author`, `form.isbn`, `form.cover_image`, `form.category`, `form.status`. POST to add or update URL; `{% csrf_token %}`.
- **Summary form:** `form.book`, `form.summary_type`, `form.title`, `form.content`, `form.quick_preview`, `form.key_takeaways`, `form.is_public`. CSRF required.
- **Review form:** `form.rating`, `form.body`. POST to book detail or dedicated review URL.
- **Comment form:** `form.body`. POST to summary detail or comment-create URL.

---

## 9. Key Jinja Snippets (Examples)

### 9.1 Base layout (header nav)

```django
<nav class="nav">
  <a href="{% url 'home' %}">Home</a>
  <a href="{% url 'bookbrief:book-list' %}">Books</a>
  <a href="{% url 'bookbrief:summary-list' %}">Summaries</a>
  {% if user.is_authenticated %}
    <a href="{% url 'bookbrief:dashboard' %}">Dashboard</a>
    <a href="{% url 'bookbrief:profile' %}">Profile</a>
    <a href="{% url 'logout' %}">Logout</a>
  {% else %}
    <a href="{% url 'login' %}?next={{ request.path }}">Login</a>
    <a href="{% url 'bookbrief:register' %}">Register</a>
  {% endif %}
</nav>
```

### 9.2 Book list (loop + empty + pagination)

```django
{% if page_obj %}
  {% for book in page_obj %}
    {% include "bookbrief/components/_book_card.html" with book=book %}
  {% endfor %}
  {% include "bookbrief/components/_pagination.html" with page_obj=page_obj %}
{% else %}
  <p class="empty-state">No books found.</p>
{% endif %}
```

### 9.3 Book detail (summaries + reviews)

```django
<h1>{{ book.title }}</h1>
<p>by {{ book.author }}{% if book.category %} · {{ book.category.name }}{% endif %}</p>
{% if book.cover_image %}<img src="{{ book.cover_image.url }}" alt="{{ book.title }}">{% endif %}

<h2>Summaries</h2>
{% for summary in summaries %}
  {% include "bookbrief/components/_summary_card.html" with summary=summary %}
{% empty %}
  <p>No summaries yet.</p>
{% endfor %}

<h2>Reviews</h2>
{% for review in reviews %}
  <p>{{ review.user.username }}: {{ review.rating }}/5 — {{ review.body|truncatewords:20 }}</p>
{% empty %}
  <p>No reviews yet.</p>
{% endfor %}
```

### 9.4 Summary detail (comments threaded)

```django
<article>
  <h1>{{ summary.get_summary_type_display }}: {{ summary.book.title }}</h1>
  <p>{{ summary.content|linebreaks }}</p>
  {% if summary.key_takeaways %}<section><h3>Key takeaways</h3><p>{{ summary.key_takeaways|linebreaks }}</p></section>{% endif %}
</article>

<section class="comments">
  {% for comment in comments %}
    {% if not comment.parent %}
      {% include "bookbrief/components/_comment.html" with comment=comment %}
    {% endif %}
  {% endfor %}
</section>
{% if user.is_authenticated %}
  <form method="post" action="...">{% csrf_token %}{{ comment_form.as_p }}<button type="submit">Post</button></form>
{% endif %}
```

### 9.5 Search & filter UI

```django
<form method="get" action="{% url 'bookbrief:book-list' %}" class="search-form">
  <input type="search" name="search" value="{{ request.GET.search }}" placeholder="Search books...">
  <select name="category">{{ categories }}</select>
  <button type="submit">Search</button>
</form>
```

### 9.6 Error pages

- **404:** `{% block content %}<h1>Page not found</h1><p><a href="{% url 'home' %}">Home</a></p>{% endblock %}`
- **403:** Same pattern, "Permission denied".
- **500:** Same pattern, "Server error".

---

## 10. Validation Checklist

- [x] Every template extends `base.html` (except base, 404/403/500 can extend base).
- [x] Context variables match view-provided names (page_obj, book, summary, form, etc.).
- [x] Loops use correct relation names (book.summaries, summary.comments, book.reviews).
- [x] Navigation URLs use `{% url 'name' %}` or `{% url 'bookbrief:name' arg %}`.
- [x] Forms include `{% csrf_token %}` and correct action URL.
- [x] Logged-in vs anonymous branches use `{% if user.is_authenticated %}`.
- [x] Empty states use `{% empty %}` or `{% if list %}...{% else %}...{% endif %}`.
