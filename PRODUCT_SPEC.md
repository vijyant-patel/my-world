# Book Summary Web Application – Product Specification

> **Source**: Requirements appended to bookbrief project.  
> **Companion**: See `TECHNICAL_BLUEPRINT.md` for current API/schema. This doc defines product scope and required design outputs.

---

## Role & Goal

- **Role**: Senior Django architect and product system designer.
- **Goal**: Design a complete, stable Book Summary Web Application.
- **Core purpose**: Users read high-quality summaries instead of full books; system saves time while maintaining clarity, completeness, and engagement.

---

## Tech Stack

- Backend: Django (latest stable)
- Templates: Jinja (server-side rendering)
- Database: PostgreSQL
- No React/Vue
- SEO-friendly pages required

---

## Primary Features

### 1. User System

- User registration / login / logout
- Profile page
- User dashboard
- User can manage their books
- Track: **Read** / **Reading** / **Want to Read**

### 2. Book System

- Add new book
- Cover image
- Category / genre
- Author
- Publish status (draft / published)
- Public book detail page (accessible without login)

### 3. Summary System

Each book supports:

- Crisp short summary (5–10 lines)
- Detailed full summary
- Chapter-wise summary (optional)
- Point-wise key takeaways
- Editable by book owner

### 4. Public Access

- Anyone (without login) can:
  - Browse books
  - Read summaries
  - Search books
  - Filter by category

### 5. Review & Engagement

- Like / Dislike system
- Comment system (threaded)
- Rating (1–5 stars)
- View count tracking
- Trending books logic

### 6. UX Goals

- Clean, minimal UI
- Easy navigation
- Fast search
- Sticky engagement
- Users should want to stay and explore

### 7. SEO & Discoverability

- Slug-based URLs
- Meta description from summary
- Sitemap
- Structured layout

### 8. Admin Features

- Moderate content
- Approve reported summaries
- Manage categories
- Analytics overview

---

## Required Output Format (Strict)

Deliverables to align implementation:

### 1. Product Architecture Overview

High-level components: user flow, book/summary lifecycle, public vs authenticated, search and discovery, engagement (likes, comments, ratings), admin moderation. How Jinja pages map to Django views and URLs.

### 2. Database Models (complete Django `models.py` code)

- All entities with fields, `Meta`, indexes, and relationships.
- UserProfile, Book (with category/genre, status), Summary (types: quick, detailed, chapter-wise, bullet/key takeaways), Chapter (optional), Review, SummaryLike, BookSave (read status), Report, Category/Genre as needed.

### 3. Relationships Diagram Explanation

- Text or diagram: User ↔ Profile; User → Books added; Book → Summaries, Reviews, Likes, Saves; Summary → Chapters (optional); Report → Summary or Review.

### 4. URL Structure Design

- List: e.g. `/books/`, `/summaries/`, `/my/books/`.
- Detail: `/books/<slug>/`, `/summaries/<id>/`.
- Auth: `/accounts/register/`, `/accounts/login/`, `/accounts/logout/`.
- Sitemap and robots for SEO.

### 5. Views Structure (class-based or function-based)

- Which views are class-based (ListView, DetailView, CreateView, etc.) vs function-based.
- How search/filter and pagination are applied.
- Which views are public vs login_required.

### 6. Template Structure (folder tree format)

```
templates/
├── base.html
├── registration/
├── dashboard/
├── books/
│   ├── list.html
│   ├── detail.html
│   ├── form.html
├── summaries/
│   ├── list.html
│   ├── detail.html
│   ├── form.html
├── components/   (optional partials)
└── ...
```

### 7. Authentication & Permissions Logic

- Registration: form validation, optional email verification.
- Login/logout: session + optional “remember me”.
- Permissions: who can create/edit/delete books vs summaries; who can like/comment; draft vs published visibility; report and moderation.

### 8. Like/Dislike System Design

- Model: e.g. SummaryLike (user, summary, value=1 or -1) or separate Like/Dislike; one vote per user per summary.
- Idempotent toggle: same action again = remove vote.
- Queries: count likes/dislikes per summary; “current user’s vote” in context.

### 9. Comment System Design

- Model: Comment (user, summary or review, parent for threading, body, created_at).
- Threaded: children via `parent` FK; order by `created_at`.
- Permissions: authenticated can comment; optional edit/delete own within window; report for moderation.

### 10. Search & Filtering Logic

- Book search: by title, author, category; full-text or icontains.
- Summary search: by book, summary type, text in content.
- Filter by category, date range, rating; combine with pagination.
- Assumption: Django ORM + indexes; optional PostgreSQL full-text or Elasticsearch later for scale.

### 11. SEO Optimization Plan

- Canonical URLs (slug for books).
- Meta title/description from book title + first summary snippet.
- Open Graph / Twitter cards for sharing.
- Sitemap: dynamic for books and summary pages; static for home, list.
- Structured data (JSON-LD): Book, Review, breadcrumbs.

### 12. Performance Optimization Plan

- Select_related / prefetch_related for list and detail views (books, summaries, reviews, likes).
- Pagination: fixed page size (e.g. 12–24); cursor-based optional for infinite scroll.
- Caching: cache list pages and hot book/summary by slug/id (e.g. Redis, TTL 5–15 min).
- Image: cover/avatar thumbnails; CDN for media in production.

### 13. Scalability Plan

- DB: connection pooling (pgBouncer); read replicas if read-heavy.
- Cache layer: Redis for sessions, fragment cache, rate limiting.
- Async: Celery for email, report processing, future export/notifications.
- Static/media: CDN; optional separate media domain.

### 14. Security Considerations

- CSRF for all POST forms; secure cookies in production.
- Rate limiting: login, register, comment, like endpoints.
- Input validation: max lengths, sanitization (e.g. bleach or markdown safe subset).
- Report flow: store reporter, status (pending/resolved/dismissed), admin actions; optional auto-hide after N reports.

### 15. Deployment Plan

- App: Gunicorn (or uWSGI) behind Nginx.
- DB: PostgreSQL (managed or self-hosted); migrations in release script.
- Env: DEBUG=False, SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL, CORS if API, REDIS_URL if cache.
- Static/media: collectstatic; serve via Nginx or S3 + CDN.
- HTTPS: terminate at Nginx; SECURE_* and SESSION_COOKIE_SECURE.

### 16. Future Expansion Ideas

- Reading lists (shelves): Want to Read / Reading / Read with dates.
- Notifications: new comments, likes, or summary on saved book.
- Export: PDF/epub of summary.
- Recommendations: “similar books” or “users who liked this also liked”.
- API versioning (e.g. /api/v1/) for future mobile or SPA.

---

## Constraints (from requirements)

- Do not give generic advice; provide real Django implementation suggestions.
- Maintain clean separation of concerns.
- Avoid unnecessary third-party packages unless justified.
- Do not invent frontend frameworks.
- Assume moderate traffic initially but scalable later.
- If making assumptions, clearly label them as **ASSUMPTION**.

---

## Validation Checklist

- [ ] Models normalized (no redundant data; FKs where needed).
- [ ] Permissions clear (public vs auth vs owner vs staff).
- [ ] Public vs private (draft/published, is_public) separation clean.
- [ ] Search efficient (indexes, query patterns documented).
- [ ] UI structure simple (templates map to views; no over-engineering).
- [ ] System scalable (caching, async, DB pooling in plan).
