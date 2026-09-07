# Book Summary Web Application – Complete Design (bookbrief app)

## 1. Product Architecture Overview

- **User flow**: Anonymous → Browse books/summaries, search, filter by category. Authenticated → Register/Login → Dashboard (my books, my summaries, read status) → Add/edit books and summaries → Like, rate, comment.
- **Book/summary lifecycle**: User adds Book (draft/published) with category; adds Summary (short, detailed, chapter-wise, key takeaways) per book; Summary is editable by owner; public sees only published books and public summaries.
- **Public vs authenticated**: Public: list books (published), list summaries (public), book detail by slug, summary detail, search, filter by category. Authenticated: create/edit/delete own books and summaries, like/dislike, comment, rate, save book (Want to Read/Reading/Read), profile, dashboard.
- **Search & discovery**: Full-site search on books (title, author) and summaries (content, book title); filter by category; sort by trending (likes + views + recency), newest, rating.
- **Engagement**: Like/Dislike per summary (one vote per user, toggle = remove); 1–5 star rating per book (one review per user); threaded comments on summaries; view count on book/summary; trending = weighted score (likes − dislikes, views, recency).
- **Admin**: Moderate reports (summary/review), approve/dismiss; manage categories; analytics (counts, top books, reported items).
- **Template mapping**: Django (or Jinja2) templates; one base template; views render list/detail/form pages; context includes user, pagination, filters, SEO meta.

---

## 2. Database Models (complete Django models.py)

Implemented in `bookbrief/models.py`. Summary of entities:

- **Category**: name, slug (unique); for genre/category filter.
- **UserProfile**: user (OneToOne), display_name, bio, avatar, is_contributor.
- **Book**: title, author, slug (unique), isbn, cover_image, category (FK), status (draft/published), added_by (FK User), view_count, created_at, updated_at.
- **Summary**: book (FK), user (FK), summary_type (quick/detailed/chapter_wise/bullet_points/key_lessons/actionable_insights), title, content, quick_preview, key_takeaways (optional), estimated_reading_minutes, word_count, is_public, is_featured, view_count, created_at, updated_at.
- **Chapter**: summary (FK), title, content, order (for chapter-wise).
- **Review**: book (FK), user (FK), rating (1–5), body; unique_together (book, user).
- **SummaryVote**: summary (FK), user (FK), value (1 or -1); unique_together (summary, user).
- **UserBookStatus**: user (FK), book (FK), status (want_to_read, reading, read), created_at, updated_at; unique_together (user, book).
- **Comment**: summary (FK), user (FK), parent (self FK, null=True for top-level), body, created_at, updated_at.
- **Report**: reporter (FK), report_type (summary/review), summary (FK, null), review (FK, null), reason, status (pending/resolved/dismissed), created_at.

(BookSave is repurposed as UserBookStatus with status field for Read/Reading/Want to Read; or keep BookSave as “saved” and add UserBookStatus for the three states. Design uses **UserBookStatus** with status field to cover both “saved” and reading state.)

---

## 3. Relationships Diagram Explanation

- **User** ↔ **UserProfile** (OneToOne).
- **User** → **Book** (added_by): one user adds many books.
- **User** → **Summary** (user): one user has many summaries.
- **Book** → **Category** (many-to-one); **Book** → **Summary** (one-to-many); **Book** → **Review** (one-to-many); **Book** → **UserBookStatus** (one-to-many).
- **Summary** → **Chapter** (one-to-many); **Summary** → **SummaryVote** (one-to-many); **Summary** → **Comment** (one-to-many).
- **Comment** → **Comment** (parent, self-referential for threading).
- **Review** → **Report** (optional); **Summary** → **Report** (optional).
- **Report** → reporter (User), summary (nullable), review (nullable).

---

## 4. URL Structure Design

| URL | Purpose | Auth |
|-----|---------|------|
| `/` | Home (featured, recent, trending) | Public |
| `/books/` | List books (search, filter by category, pagination) | Public |
| `/books/<slug>/` | Book detail (slug, public) | Public |
| `/books/add/` | Add book | Login |
| `/books/<slug>/edit/` | Edit book | Owner |
| `/summaries/` | List summaries (filter by type, book, search) | Public |
| `/summaries/<id>/` | Summary detail (view count increment) | Public |
| `/summaries/add/` | Add summary (select book) | Login |
| `/summaries/<id>/edit/` | Edit summary | Owner |
| `/accounts/register/` | Registration | Public |
| `/accounts/login/` | Login | Public |
| `/accounts/logout/` | Logout | Login |
| `/accounts/profile/` | Profile view/edit | Login |
| `/dashboard/` | User dashboard (my books, my summaries, read status) | Login |
| `/my/books/` | My added books | Login |
| `/my/summaries/` | My summaries | Login |
| `/category/<slug>/` | Books by category | Public |
| `/sitemap.xml` | Sitemap | Public |
| `/robots.txt` | Robots | Public |
| `/api/` | Optional API (existing DRF) | Per view |

**Note:** Current app mounts bookbrief under `/api/` (e.g. `/api/books/<slug>/`). For SEO-friendly public pages, add parallel routes at root (e.g. `/books/<slug>/`, `/accounts/login/`) that render Django/Jinja templates; keep `/api/` for programmatic access.

---

## 5. Views Structure

- **Class-based (recommended)**:
  - `HomeView` (TemplateView): recent books, recent summaries, trending (e.g. top 8).
  - `BookListView` (ListView): filter by category, search (title, author), ordering (newest, trending, rating); paginate 24; public.
  - `BookDetailView` (DetailView): slug lookup; increment view_count (e.g. in get_object or middleware); public.
  - `BookCreateView` (CreateView), `BookUpdateView` (UpdateView): login_required; owner for update.
  - `SummaryListView` (ListView): filter by book, summary_type, search (content, book title); paginate 24; public.
  - `SummaryDetailView` (DetailView): increment view_count; public.
  - `SummaryCreateView` (CreateView), `SummaryUpdateView` (UpdateView): login_required; owner for update.
  - `CategoryDetailView` (ListView filtered by category slug).
  - `RegisterView`, `LoginView`, `LogoutView`: Django auth or custom forms.
  - `ProfileView` (UpdateView or TemplateView + form): login_required.
  - `DashboardView` (TemplateView): my books, my summaries, UserBookStatus list; login_required.
  - `SummaryVoteView` (View, POST): toggle like/dislike (value 1 or -1); idempotent (same value = delete vote); login_required.
  - `CommentCreateView` (CreateView): login_required; parent for reply.
  - `ReviewCreateView` / `ReviewUpdateView`: one review per user per book; login_required.
  - `UserBookStatusUpdateView` (View, POST): set want_to_read / reading / read; login_required.
- **Search/filter**: Use Django Q (title__icontains, author__icontains, category__slug); optional django-filter for GET params. Pagination: Paginator with page size 24 (or 12).
- **Public vs login_required**: List/detail of books and summaries = public; create/edit/delete, vote, comment, review, status, profile, dashboard = login_required; owner or staff for edit/delete content.

---

## 6. Template Structure (folder tree)

```
templates/
├── base.html
├── registration/
│   ├── login.html
│   ├── register.html
│   └── logged_out.html
├── bookbrief/
│   ├── home.html
│   ├── book_list.html
│   ├── book_detail.html
│   ├── book_form.html (add/edit)
│   ├── summary_list.html
│   ├── summary_detail.html
│   ├── summary_form.html (add/edit)
│   ├── category_detail.html (books by category)
│   ├── dashboard.html
│   ├── profile.html
│   └── components/
│       ├── _book_card.html
│       ├── _summary_card.html
│       ├── _comment.html (recursive for threads)
│       ├── _review_form.html
│       └── _pagination.html
├── sitemap.xml (or generated via view)
└── robots.txt
```

---

## 7. Authentication & Permissions Logic

- **Registration**: Django form; username, password, optional email; create User + UserProfile; optional email verification (ASSUMPTION: not implemented initially).
- **Login/Logout**: Django built-in auth (session); login_required for dashboard, profile, create/edit, vote, comment, review.
- **Permissions**:
  - **Book**: Create = authenticated; Edit/Delete = added_by (owner) or staff; List/Detail (published) = public; Draft = only owner and staff.
  - **Summary**: Create = authenticated; Edit/Delete = user (owner) or staff; List/Detail (is_public) = public; owner sees own drafts.
  - **Like/Dislike, Comment, Review, UserBookStatus**: authenticated only.
  - **Report**: authenticated; moderation = staff (resolve/dismiss).
- **Draft vs published**: Book list/detail for public shows only status=published; book detail by slug for owner shows draft; Summary list/detail shows only is_public=True for non-owners.

---

## 8. Like/Dislike System Design

- **Model**: `SummaryVote(summary, user, value)` with value in (1, -1); `unique_together = [["summary", "user"]]`.
- **Idempotent toggle**: POST to e.g. `/summaries/<id>/vote/` with `value=1` or `value=-1`. If user already voted same value → delete vote; if opposite value → update to new value.
- **Queries**: `likes_count = SummaryVote.objects.filter(summary=obj, value=1).count()`; `dislikes_count = SummaryVote.objects.filter(summary=obj, value=-1).count()`; for current user: `request.user.summary_votes.filter(summary=obj).first()` → .value.
- **Context**: In SummaryDetailView, pass `user_vote` (1, -1, or None) and `likes_count`, `dislikes_count`.

---

## 9. Comment System Design

- **Model**: `Comment(summary, user, parent, body, created_at, updated_at)`. `parent` is nullable; null = top-level; non-null = reply to Comment.
- **Threading**: Children via `comment.children` (reverse FK: parent_id). Order by `created_at`. In template, render top-level comments then recurse for children.
- **Permissions**: Authenticated can create; optional: edit/delete own within 15 min (ASSUMPTION: implement edit/delete own, no time window initially).
- **Report**: Report can target summary or review; comments can be reported by extending Report content_type or adding CommentReport (ASSUMPTION: report on summary/review only; comment reports as future expansion).

---

## 10. Search & Filtering Logic

- **Book search**: GET param `q` or `search`; `Q(title__icontains=query) | Q(author__icontains=query)`; filter by `category__slug`; ordering: `-created_at`, `-view_count`, `-rating` (aggregate from Review); only status=published for public.
- **Summary search**: GET param `q`; `Q(content__icontains=query) | Q(quick_preview__icontains=query) | Q(book__title__icontains=query)`; filter by `book`, `summary_type`; only is_public=True for public.
- **Indexes**: Book (title, author, slug, category_id, status); Summary (book_id, user_id, summary_type, is_public); Review (book_id, user_id).
- **ASSUMPTION**: Django ORM + indexes; PostgreSQL full-text (SearchVector) or Elasticsearch later for scale.

---

## 11. SEO Optimization Plan

- **Canonical URLs**: Book detail `/books/<slug>/`, summary `/summaries/<id>/` (or slug if added).
- **Meta title**: `{{ book.title }} – BookBrief`; **Meta description**: first 155 chars of summary quick_preview or content.
- **Open Graph / Twitter cards**: og:title, og:description, og:image (cover_image), og:url in base/detail templates.
- **Sitemap**: Dynamic sitemap view: home, /books/, /summaries/, /books/<slug>/ for each published book, /summaries/<id>/ for each public summary; lastmod from updated_at.
- **Structured data (JSON-LD)**: On book detail: Book schema (name, author, image); Review schema (rating, author); BreadcrumbList. In `<script type="application/ld+json">`.

---

## 12. Performance Optimization Plan

- **Queries**: `select_related("category", "added_by")` for Book list/detail; `prefetch_related("summaries", "reviews")` for book detail; `select_related("book", "user")` for Summary list; `prefetch_related("chapters", "likes")` for summary detail if needed.
- **Pagination**: Page size 24 (or 12); avoid large page sizes.
- **Caching**: Cache list pages and hot book/summary by slug/id (e.g. `cache.get/set` with TTL 5–15 min); cache key includes query params for filtered lists. ASSUMPTION: Redis or Django cache backend.
- **Images**: Cover/avatar: use ImageField; optional thumbnails (django-imagekit or similar) and CDN for media in production.

---

## 13. Scalability Plan

- **DB**: Connection pooling (pgBouncer); read replicas for read-heavy traffic; indexes as in §10.
- **Cache**: Redis for sessions, fragment cache, rate limiting (e.g. django-ratelimit).
- **Async**: Celery for email, report processing, future export/notifications; Redis as broker.
- **Static/Media**: CDN; optional separate media domain; collectstatic for static.

---

## 14. Security Considerations

- **CSRF**: All POST forms use `{% csrf_token %}`; ensure CSRF middleware enabled.
- **Rate limiting**: Apply to login, register, comment, vote (e.g. 10/min per IP or user).
- **Input validation**: Max length on CharField/TextField; sanitize content (e.g. bleach or markdown safe subset for summary/comment body).
- **Report flow**: Store reporter, status (pending/resolved/dismissed); admin actions only; optional auto-hide after N reports (ASSUMPTION: manual moderation).

---

## 15. Deployment Plan

- **App**: Gunicorn (or uWSGI) behind Nginx.
- **DB**: PostgreSQL; migrations in release script; `DATABASE_URL` + dj-database-url.
- **Env**: DEBUG=False, SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL, REDIS_URL if cache, CORS if API.
- **Static/Media**: collectstatic; serve via Nginx or S3 + CDN; MEDIA_ROOT on volume or S3.
- **HTTPS**: Terminate at Nginx; SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE.

**Migrations:** Run `python manage.py makemigrations bookbrief` then `migrate`. If your DB has the old `BookSummary` table (from a prior schema), either add a data migration to copy rows into `Summary` before removing `BookSummary`, or start from a fresh DB.

---

## 16. Future Expansion Ideas

- **Reading lists (shelves)**: Already covered by UserBookStatus (Want to Read / Reading / Read); add “started_at” / “finished_at” dates.
- **Notifications**: New comments, likes, or new summary on saved book; in-app or email via Celery.
- **Export**: PDF/EPUB of summary (e.g. WeasyPrint, reportlab).
- **Recommendations**: “Similar books” (same category, same author); “Users who liked this also liked” (collaborative filtering later).
- **API versioning**: `/api/v1/` for future mobile or SPA; keep session auth for web.

---

## Validation Checklist

- [x] Models normalized (Category, FKs; no redundant data).
- [x] Permissions clear (public vs auth vs owner vs staff).
- [x] Public vs private separation (draft/published, is_public).
- [x] Search efficient (indexes, Q filters).
- [x] UI structure simple (templates map to views).
- [x] System scalable (caching, async, DB pooling in plan).
