# Book Summary Platform – Technical Blueprint

**Product requirements**: See [PRODUCT_SPEC.md](PRODUCT_SPEC.md) for full feature set, UX/SEO/admin goals, and required design outputs (architecture, models, URLs, views, templates, auth, engagement, SEO, performance, security, deployment).

---

## 1. Project Overview

**lrv** is a Django-based Book Summary Platform. Users add books they have read, write short (5–10 line) and detailed summaries, view their own and others’ public summaries, and discover content via search. Backend is REST API (DRF) with JWT auth; DB is PostgreSQL in production, SQLite for local dev.

---

## 2. Database Schema (models.py)

Implemented in `bookbrief/models.py`:

- **UserProfile**: OneToOne to User; `display_name`, `bio`, `avatar`; for display only.
- **Book**: `title`, `author`, `isbn`, `cover_image`, `added_by` (FK User), `created_at`. Indexes on title, author, isbn.
- **BookSummary**: `book` (FK), `user` (FK), `short_summary` (min 50 chars), `detailed_summary` (min 100 chars), `is_public`, `created_at`, `updated_at`. Indexes on book, user, is_public.

(Full code is in `bookbrief/models.py`.)

---

## 3. API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Register (username, password, email) |
| POST | `/api/auth/token/` | No | Obtain JWT access + refresh |
| POST | `/api/auth/token/refresh/` | Refresh | Refresh access token |
| GET/POST | `/api/books/` | GET: No, POST: Yes | List books (filter/search) / Create book |
| GET | `/api/books/<id>/` | No | Book detail with public summaries |
| GET | `/api/books/my/` | Yes | Current user’s added books |
| GET/POST | `/api/summaries/` | GET: No, POST: Yes | List public summaries (filter/search) / Create summary |
| GET/PUT/PATCH/DELETE | `/api/summaries/<id>/` | Owner for write | Summary detail / Update / Delete |
| GET | `/api/summaries/my/` | Yes | Current user’s summaries |
| GET/PUT/PATCH | `/api/profile/` | Yes | Get/update profile |

Query params: `search`, `title`, `author`, `book`, `ordering` (e.g. `-created_at`). Pagination: 20 per page.

---

## 4. Folder Structure

```
lrv/
├── manage.py
├── requirements.txt
├── TECHNICAL_BLUEPRINT.md
├── venv_lrv/
├── lrv/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── bookbrief/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── templates/
│   └── base.html
├── static/
│   └── css/
│       └── style.css
├── media/
└── staticfiles/
```

---

## 5. Auth & Permissions Design

- **Auth**: Django User + JWT (Simple JWT). Access token in header: `Authorization: Bearer <token>`. Register → `POST /api/auth/register/`; login → `POST /api/auth/token/`.
- **Permissions**:
  - Public: list books, list public summaries, book detail, summary detail (if public).
  - Authenticated: create book/summary, edit/delete own summary, own profile, `/books/my/`, `/summaries/my/`.
  - Custom: `IsBookSummaryOwner` – only owner can update/delete a summary; read allowed for public or owner.

---

## 6. Search Design

- **Books**: DRF `SearchFilter` on `title`, `author`, `isbn`; `BookFilter` (django-filter) for `title`, `author`, `search` (combined title/author).
- **Summaries**: `BookSummaryFilter` for `book` (id), `search` (short_summary, detailed_summary); only public summaries in search.
- **Assumption**: In-database search only. For large scale, consider PostgreSQL full-text search or Elasticsearch later.

---

## 7. Deployment Strategy

- **App**: Gunicorn + Django (or uWSGI). Reverse proxy: Nginx.
- **DB**: PostgreSQL (e.g. managed DB). Use `DATABASE_URL` + `dj-database-url` in settings.
- **Env**: `DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ORIGINS`, `DATABASE_URL`.
- **Static/Media**: `collectstatic` → serve via Nginx or CDN; media on volume or S3.
- **HTTPS**: Terminate at Nginx; set `SECURE_*` and `SESSION_COOKIE_SECURE` etc. in production settings.

---

## 8. Scalability Improvements

- Add DB connection pooling (e.g. pgBouncer).
- Cache list/detail with Redis (e.g. cache book list, summary list by query).
- Async tasks for heavy work (e.g. email, future exports) via Celery + Redis.
- CDN for static/media; optional read replicas for DB if read-heavy.

---

## 9. Potential Risks

- **Duplicate books**: Same title/author can be added multiple times; consider deduplication or “book master” entity later.
- **Content size**: No hard cap on summary length; add validation/max length if needed.
- **Abuse**: Rate limiting and moderation (e.g. report flag) not implemented; add as needed.

---

## 10. Validation Checklist

- [x] Models match endpoints (Book, BookSummary, UserProfile).
- [x] Auth: JWT; permissions align (public read, owner write for summaries).
- [x] Search/filter on books and summaries.
- [x] Admin for Book, BookSummary, UserProfile.
- [x] Pagination and ordering on list APIs.
- [ ] Run `python manage.py migrate` and smoke-test APIs.
- [ ] Production: use PostgreSQL, set env vars, run migrations and collectstatic.
