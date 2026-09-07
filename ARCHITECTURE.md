# Book Summary Platform – Architecture (Appended)

## 1. Product overview
- **Purpose**: Users read high-quality summaries instead of full books; save time while keeping clarity and engagement.
- **Stack**: Django (latest), Jinja templates, PostgreSQL, no React/Vue, SEO-friendly.

## 2. Database models (summary)
- **UserProfile**: user, display_name, bio, avatar, is_contributor.
- **Book**: title, author, slug, isbn, cover_image, added_by.
- **Summary**: book, user, summary_type (quick/detailed/chapter_wise/bullet_points/key_lessons/actionable_insights), content, quick_preview, estimated_reading_minutes, word_count, is_public, is_featured.
- **Chapter**: summary, title, content, order (for chapter-wise).
- **Review**: book, user, rating (1–5), body.
- **SummaryLike**: summary, user (unique together).
- **BookSave**: book, user (unique together).
- **Report**: reporter, summary/review, report_type, reason, status (pending/resolved/dismissed).

## 3. URL structure
- `/` → Home (template).
- `/admin/` → Admin.
- `/api/` → bookbrief API (auth, books, summaries, profile).
- Books: `GET/POST /api/books/`, `GET /api/books/<id>/`, `GET /api/books/my/`.
- Summaries: `GET/POST /api/summaries/`, `GET/PUT/PATCH/DELETE /api/summaries/<id>/`, `GET /api/summaries/my/`.
- Auth: `POST /api/auth/register/`, `POST /api/auth/token/`, `POST /api/auth/token/refresh/`.
- Profile: `GET/PUT/PATCH /api/profile/`.

## 4. Engagement & moderation
- **Like**: One like per user per summary; count for trending.
- **Review**: One review per user per book; rating 1–5, body optional.
- **Save**: One save per user per book.
- **Report**: Report summary or review; reason, status workflow (pending → resolved/dismissed).

## 5. SEO & performance
- Slug-based URLs for books/summaries.
- Meta description from summary preview.
- Pagination (e.g. 20 per page).
- Caching for popular books/summaries (recommended).

## 6. Security
- Prevent duplicate summaries (same book + type + user).
- Rate limiting on reviews/likes (optional).
- Report abuse flow; admin can resolve/dismiss.
