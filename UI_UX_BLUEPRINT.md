# Book Summary Platform – UI/UX Blueprint

## 1. UI Suggestion List (Options with Pros/Cons)

| # | Suggestion | Pros | Cons |
|---|------------|------|------|
| **A** | **Magazine-style layout** – Hero with featured book, grid of cards with large cover images, clear typography hierarchy (H1 → H2 → body). | High visual impact; strong discoverability; feels premium. | Needs more imagery; empty states require placeholders. |
| **B** | **Reader-first layout** – Focus on reading experience: max-width content column (~65ch), generous line-height, sticky TOC for long summaries, visible reading time. | Best readability; supports long-form; accessible. | Less “dashboard” feel on home; list pages stay compact. |
| **C** | **Card + sidebar layout** – Main content area + sticky sidebar (categories, “Continue reading”, quick add). | Clear separation; quick navigation; good for power users. | Sidebar can feel cramped on mobile; needs collapse on small screens. |
| **D** | **Minimal / doc-style** – Clean whitespace, few decorations, strong focus on text and structure (headings, lists). | Fast to implement; works without many assets; accessible. | Risk of feeling “plain”; relies on typography and spacing. |
| **E** | **Hybrid (recommended)** – Magazine hero + reader-first summary view + card grids for lists + compact dashboard with status pills and progress. | Balances discovery, reading, and management; one design system. | Slightly more CSS and components to maintain. |

**Recommendation:** Option **E (Hybrid)** – Use card grids and hero on home/list/dashboard, reader-optimized layout on book/summary detail, and a rich text editor (e.g. Quill.js) for the summary form.

---

## 2. Template Folder Structure

```
templates/
├── base.html
├── base_nav_only.html          (optional: minimal base for auth pages)
├── 404.html, 403.html, 500.html
├── registration/
│   ├── login.html
│   ├── register.html
│   └── logged_out.html
└── bookbrief/
    ├── home.html
    ├── book_list.html
    ├── book_detail.html
    ├── book_form.html
    ├── book_confirm_delete.html
    ├── summary_list.html
    ├── summary_detail.html
    ├── summary_form.html       (rich editor here)
    ├── summary_confirm_delete.html
    ├── category_detail.html
    ├── dashboard.html
    ├── profile.html
    └── components/
        ├── _book_card.html
        ├── _summary_card.html
        ├── _summary_card_compact.html   (dashboard / lists)
        ├── _pagination.html
        ├── _comment.html
        ├── _search_filter.html
        ├── _review_form.html
        ├── _rich_editor.html            (Quill wrapper)
        ├── _reading_progress.html       (optional)
        └── _status_pill.html            (Want to read / Reading / Read)
```

---

## 3. Base Template Snippets

### 3.1 Base layout (semantic, mobile-first)

```django
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}BookBrief{% endblock %}</title>
    {% block meta_description %}{% endblock %}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Literata:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body class="{% block body_class %}layout-default{% endblock %}">
    <a href="#main" class="skip-link">Skip to main content</a>
    <header class="site-header" role="banner">
        <div class="container header-inner">
            <a href="{% url 'home' %}" class="logo" aria-label="BookBrief home">BookBrief</a>
            <button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false" type="button"></button>
            <nav class="nav" aria-label="Main" id="main-nav">
                <a href="{% url 'home' %}">Home</a>
                <a href="{% url 'book_list' %}">Books</a>
                <a href="{% url 'summary_list' %}">Summaries</a>
                {% if user.is_authenticated %}
                    <a href="{% url 'dashboard' %}">Dashboard</a>
                    <a href="{% url 'profile_edit' %}">Profile</a>
                    <a href="{% url 'logout' %}">Logout</a>
                {% else %}
                    <a href="{% url 'login' %}?next={{ request.get_full_path|urlencode }}">Login</a>
                    <a href="{% url 'register' %}">Register</a>
                {% endif %}
            </nav>
        </div>
    </header>
    <main id="main" class="main" role="main">
        <div class="container {% block container_class %}{% endblock %}">
            {% if messages %}
                <ul class="messages" role="alert">
                    {% for message in messages %}
                        <li class="message message-{{ message.tags }}">{{ message }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
            {% block content %}{% endblock %}
        </div>
    </main>
    <footer class="site-footer" role="contentinfo">
        <div class="container">
            <p>BookBrief – Read less, remember more.</p>
            <nav class="footer-nav" aria-label="Footer">
                <a href="{% url 'home' %}">Home</a>
                <a href="{% url 'book_list' %}">Books</a>
                <a href="{% url 'summary_list' %}">Summaries</a>
            </nav>
        </div>
    </footer>
    <script>/* nav toggle */</script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 3.2 Reader layout (for book/summary detail)

```django
{% extends "base.html" %}
{% block body_class %}layout-reader{% endblock %}
{% block container_class %}container--narrow{% endblock %}
```

---

## 4. Page Snippets

### 4.1 Home – Hero + sections

```django
{% extends "base.html" %}
{% block title %}Home – BookBrief{% endblock %}
{% block content %}
<section class="hero hero--home" aria-labelledby="hero-heading">
    <h1 id="hero-heading" class="hero__title">Read less, remember more</h1>
    <p class="hero__tagline">Discover book summaries. Quick, detailed, and chapter-wise.</p>
    <form class="hero__search" method="get" action="{% url 'book_list' %}" role="search">
        <label for="hero-search" class="visually-hidden">Search books</label>
        <input id="hero-search" type="search" name="search" placeholder="Search books or authors…" aria-label="Search books">
        <button type="submit">Search</button>
    </form>
</section>
<section class="section section--books" aria-labelledby="recent-books-heading">
    <h2 id="recent-books-heading" class="section__title">Recent books</h2>
    {% if recent_books %}
    <ul class="card-grid card-grid--books">
        {% for book in recent_books %}
        <li>{% include "bookbrief/components/_book_card.html" with book=book %}</li>
        {% endfor %}
    </ul>
    <p class="section__cta"><a href="{% url 'book_list' %}">View all books</a></p>
    {% else %}
    <p class="empty-state">No books yet. <a href="{% url 'book_list' %}">Browse</a> or add one.</p>
    {% endif %}
</section>
<section class="section section--summaries" aria-labelledby="recent-summaries-heading">
    <h2 id="recent-summaries-heading" class="section__title">Recent summaries</h2>
    {% if recent_summaries %}
    <ul class="card-grid card-grid--summaries">
        {% for s in recent_summaries %}
        <li>{% include "bookbrief/components/_summary_card.html" with summary=s %}</li>
        {% endfor %}
    </ul>
    <p class="section__cta"><a href="{% url 'summary_list' %}">View all summaries</a></p>
    {% else %}
    <p class="empty-state">No public summaries yet.</p>
    {% endif %}
</section>
{% endblock %}
```

### 4.2 Dashboard – Status pills + previews

```django
{% extends "base.html" %}
{% block title %}Dashboard – BookBrief{% endblock %}
{% block content %}
<header class="page-header">
    <h1 class="page-title">Dashboard</h1>
    <p class="page-subtitle">Welcome, {{ user.username }}</p>
</header>
<section class="dashboard-section" aria-labelledby="my-books-heading">
    <h2 id="my-books-heading">My books</h2>
    {% if my_books %}
    <ul class="card-grid">
        {% for book in my_books %}
        <li>{% include "bookbrief/components/_book_card.html" with book=book %}</li>
        {% endfor %}
    </ul>
    <p class="section__actions">
        <a href="{% url 'book_list' %}">View all</a>
        <a href="{% url 'book_add' %}" class="btn btn--primary">Add book</a>
    </p>
    {% else %}
    <div class="empty-state">
        <p>You haven't added any books yet.</p>
        <a href="{% url 'book_add' %}" class="btn btn--primary">Add your first book</a>
    </div>
    {% endif %}
</section>
<section class="dashboard-section" aria-labelledby="my-summaries-heading">
    <h2 id="my-summaries-heading">My summaries</h2>
    {% if my_summaries %}
    <ul class="card-grid">
        {% for summary in my_summaries %}
        <li>{% include "bookbrief/components/_summary_card_compact.html" with summary=summary %}</li>
        {% endfor %}
    </ul>
    <p class="section__actions">
        <a href="{% url 'summary_list' %}">View all</a>
        <a href="{% url 'summary_add' %}" class="btn btn--primary">Add summary</a>
    </p>
    {% else %}
    <div class="empty-state">
        <p>You haven't written any summaries yet.</p>
        <a href="{% url 'summary_add' %}" class="btn btn--primary">Write a summary</a>
    </div>
    {% endif %}
</section>
{% if reading_statuses %}
<section class="dashboard-section" aria-labelledby="reading-status-heading">
    <h2 id="reading-status-heading">Reading status</h2>
    <ul class="status-list">
        {% for status in reading_statuses %}
        <li class="status-list__item">
            <span class="status-pill status-pill--{{ status.status }}">{{ status.get_status_display }}</span>
            <a href="{% url 'book_detail' status.book.slug %}">{{ status.book.title }}</a>
        </li>
        {% endfor %}
    </ul>
</section>
{% endif %}
{% endblock %}
```

### 4.3 Book detail – Readability + engagement

```django
{% extends "base.html" %}
{% block body_class %}layout-reader{% endblock %}
{% block container_class %}container--narrow{% endblock %}
{% block content %}
<article class="book-detail" itemscope itemtype="https://schema.org/Book">
    <header class="book-detail__header">
        {% if book.cover_image %}
        <div class="book-detail__cover">
            <img src="{{ book.cover_image.url }}" alt="{{ book.title }}" itemprop="image">
        </div>
        {% endif %}
        <div class="book-detail__meta">
            <h1 class="book-detail__title" itemprop="name">{{ book.title }}</h1>
            <p class="book-detail__author" itemprop="author">by {{ book.author }}</p>
            {% if book.category %}
            <p class="book-detail__category"><a href="{% url 'category_detail' book.category.slug %}">{{ book.category.name }}</a></p>
            {% endif %}
            {% if book.average_rating %}
            <p class="book-detail__rating" aria-label="Rating {{ book.average_rating }} out of 5">★ {{ book.average_rating }} ({{ book.reviews_count }} review{{ book.reviews_count|pluralize }})</p>
            {% endif %}
            {% if user.is_authenticated and book.added_by_id == user.id %}
            <nav class="book-detail__actions" aria-label="Book actions">
                <a href="{% url 'summary_add' %}?book={{ book.pk }}">Add summary</a>
                <a href="{% url 'book_edit' book.slug %}">Edit</a>
                <a href="{% url 'book_delete' book.slug %}">Delete</a>
            </nav>
            {% endif %}
        </div>
    </header>
    <section class="book-detail__summaries" aria-labelledby="summaries-heading">
        <h2 id="summaries-heading">Summaries</h2>
        {% if summaries %}
        <ul class="summary-toc">
            {% for summary in summaries %}
            <li><a href="{% url 'summary_detail' summary.pk %}">{{ summary.get_summary_type_display }} · {{ summary.estimated_reading_minutes }} min</a></li>
            {% endfor %}
        </ul>
        {% else %}
        <p class="empty-state">No summaries yet.{% if user.is_authenticated %} <a href="{% url 'summary_add' %}?book={{ book.pk }}">Add one</a>.{% endif %}</p>
        {% endif %}
    </section>
    <section class="book-detail__reviews" aria-labelledby="reviews-heading">
        <h2 id="reviews-heading">Reviews</h2>
        {% for review in reviews %}
        <div class="review" itemprop="review" itemscope itemtype="https://schema.org/Review">
            <p class="review__meta"><span itemprop="author">{{ review.user.username }}</span> · <span itemprop="ratingValue">{{ review.rating }}</span>/5 · {{ review.created_at|date }}</p>
            {% if review.body %}<div class="review__body" itemprop="reviewBody">{{ review.body|linebreaks }}</div>{% endif %}
        </div>
        {% empty %}
        <p class="empty-state">No reviews yet.</p>
        {% endfor %}
        {% if user.is_authenticated and review_form %}
        <form method="post" class="form review-form">{% csrf_token %}{{ review_form.as_p }}<button type="submit">{% if user_review %}Update{% else %}Submit{% endif %} review</button></form>
        {% elif not user.is_authenticated %}
        <p><a href="{% url 'login' %}?next={{ request.get_full_path|urlencode }}">Log in</a> to leave a review.</p>
        {% endif %}
    </section>
</article>
{% endblock %}
```

### 4.4 Add/Edit summary – Rich editor wrapper

```django
{% extends "base.html" %}
{% block title %}{% if object %}Edit summary{% else %}Add summary{% endif %} – BookBrief{% endblock %}
{% block content %}
<header class="page-header">
    <h1 class="page-title">{% if object %}Edit summary{% else %}Add summary{% endif %}</h1>
    {% if book %}<p class="page-subtitle">Book: {{ book.title }} by {{ book.author }}</p>{% endif %}
</header>
<form method="post" class="form summary-form" id="summary-form">
    {% csrf_token %}
    {{ form.summary_type }}
    {{ form.title }}
    <div class="form-group form-group--rich">
        <label for="id_content">Content</label>
        {% include "bookbrief/components/_rich_editor.html" with field=form.content field_id="id_content" field_name="content" %}
    </div>
    {{ form.quick_preview }}
    {{ form.key_takeaways }}
    {{ form.estimated_reading_minutes }}
    {{ form.is_public }}
    <p class="form-actions">
        <button type="submit" class="btn btn--primary">{% if object %}Save changes{% else %}Add summary{% endif %}</button>
        <a href="{% if object %}{% url 'summary_detail' object.pk %}{% else %}{% url 'summary_list' %}{% endif %}">Cancel</a>
    </p>
</form>
{% endblock %}
{% block extra_js %}{% include "bookbrief/components/_rich_editor_js.html" with field_id="id_content" %}{% endblock %}
```

---

## 5. Rich Summary Editor Integration

### 5.1 Library choice

- **Quill.js** (recommended): Lightweight, toolbar (bold, italic, lists, headers, links), outputs HTML, keyboard shortcuts, easy to sync with a hidden `<textarea>` for Django form submission.

### 5.2 Component: `_rich_editor.html`

```django
{# Pass: field (form field), field_id (e.g. id_content), field_name (e.g. content) #}
<div class="rich-editor" data-field-id="{{ field_id }}" data-field-name="{{ field_name }}">
    <div id="quill-{{ field_id }}" class="rich-editor__container" role="textbox" aria-label="Summary content"></div>
    <textarea name="{{ field_name }}" id="{{ field_id }}" class="rich-editor__source" style="display:none;" required>{{ field.value|default:'' }}</textarea>
</div>
<p class="rich-editor__hint">Shortcuts: Ctrl+B bold, Ctrl+I italic, Ctrl+K link</p>
```

### 5.3 Component: `_rich_editor_js.html`

```django
{# Load Quill once in base or here #}
<script src="https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.js"></script>
<link href="https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.snow.css" rel="stylesheet">
<script>
(function() {
    var fieldId = "{{ field_id }}";
    var source = document.getElementById(fieldId);
    if (!source) return;
    var container = document.getElementById("quill-" + fieldId);
    if (!container) return;
    var editor = new Quill(container, {
        theme: "snow",
        placeholder: "Write your summary… Use headings and lists for structure.",
        modules: {
            toolbar: [
                [{ header: [1, 2, 3, false] }],
                ["bold", "italic", "underline"],
                [{ list: "ordered" }, { list: "bullet" }],
                ["link", "code-block"],
                ["clean"]
            ]
        }
    });
    editor.root.innerHTML = source.value;
    editor.on("text-change", function() {
        source.value = editor.root.innerHTML;
    });
})();
</script>
```

### 5.4 Summary detail – Render stored HTML safely

```django
<div class="summary-content prose">
    {{ summary.content|safe }}
</div>
```

**Security:** When storing Quill HTML, sanitize on save (e.g. `bleach` with allowed tags: `p, strong, em, u, h1, h2, h3, ul, ol, li, a, code, pre`). In `summary_detail.html`, use `{{ summary.content|safe }}` only after sanitization is in place; until then keep `{{ summary.content|linebreaks }}` for plain text.

---

## 6. Component Reuse Recommendations

| Component | Use on | Notes |
|-----------|--------|--------|
| `_book_card.html` | Home, book list, dashboard, category | Same card; optional modifier class for compact. |
| `_summary_card.html` | Home, summary list | Full card with excerpt. |
| `_summary_card_compact.html` | Dashboard | Shorter; type + title + link only. |
| `_rich_editor.html` | Summary form (add/edit) | One place; include JS in `extra_js`. |
| `_search_filter.html` | Book list, summary list | Same form; `request.path` for action. |
| `_pagination.html` | All list pages | Pass `page_obj`. |
| `_comment.html` | Summary detail | Recursive for threads. |
| `_status_pill.html` | Dashboard | Want to read / Reading / Read. |

---

## 7. UX Notes & Best Practices

- **Mobile-first:** Base styles for small viewport; `min-width` breakpoints for nav (e.g. hamburger → horizontal nav), grid columns, and reader width.
- **Typography:** Limit line length (~65ch) on reading pages; use Literata (or similar) for body, DM Sans for UI and headings.
- **Spacing:** Consistent spacing scale (e.g. 0.5rem, 1rem, 1.5rem, 2rem); section spacing ≥ 2rem.
- **Public vs logged-in:** Show “Add book”, “Add summary”, “Dashboard”, “Profile” only when authenticated; show “Login / Register” when not. Use `{% if user.is_authenticated %}` in nav and CTAs.
- **Accessibility:** Skip link, `aria-label` on nav/buttons, semantic headings (one H1 per page), form labels, and sufficient contrast.
- **Empty states:** Every list/section has a clear message and primary CTA (e.g. “Add your first book”).
- **Loading:** Optional: add `loading="lazy"` on card images; avoid layout shift with fixed aspect ratio for covers.
