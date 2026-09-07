# Light Theme Forms – Redesign

## 1. Light Theme Palette Suggestion

| Token | Hex | Use |
|-------|-----|-----|
| **Primary** | `#2563eb` | Buttons, links, focus ring |
| **Primary hover** | `#1d4ed8` | Button/link hover |
| **Secondary** | `#64748b` | Muted text, placeholders |
| **Background** | `#ffffff` | Page background |
| **Surface** | `#f8fafc` | Form containers, cards |
| **Surface elevated** | `#ffffff` | Inputs, dropdowns (with border) |
| **Border** | `#e2e8f0` | Input borders, dividers |
| **Border focus** | `#2563eb` | Focus state |
| **Text** | `#0f172a` | Body text |
| **Text muted** | `#64748b` | Labels, hints |
| **Error** | `#dc2626` | Error text, error border |
| **Error bg** | `#fef2f2` | Error message background |
| **Success** | `#16a34a` | Success messages |
| **Shadow** | `0 1px 3px rgba(0,0,0,0.08)` | Soft shadow for inputs/cards |
| **Shadow hover** | `0 4px 12px rgba(0,0,0,0.1)` | Card/button hover |
| **Radius** | `8px` | Inputs, buttons, cards |

---

## 2. Redesigned Form Snippets

### 2.1 Login

```django
<div class="form-wrap form-wrap--auth">
    <h1 class="form-wrap__title">Log in</h1>
    <form method="post" action="{% url 'login' %}" class="form form--light">
        {% csrf_token %}
        <input type="hidden" name="next" value="{{ next }}">
        {% for field in form %}
            {% include "bookbrief/components/_form_field.html" with field=field %}
        {% endfor %}
        {% include "bookbrief/components/_form_actions.html" with submit_label="Log in" %}
    </form>
    <p class="form-wrap__footer"><a href="{% url 'register' %}" class="form-wrap__link">Create an account</a></p>
</div>
```

### 2.2 Registration

```django
<div class="form-wrap form-wrap--auth">
    <h1 class="form-wrap__title">Create an account</h1>
    <form method="post" action="{% url 'register' %}" class="form form--light" enctype="multipart/form-data">
        {% csrf_token %}
        {% if form.non_field_errors %}{% include "bookbrief/components/_form_errors.html" with errors=form.non_field_errors %}{% endif %}
        {% for field in form %}
            {% include "bookbrief/components/_form_field.html" with field=field %}
        {% endfor %}
        {% include "bookbrief/components/_form_actions.html" with submit_label="Register" %}
    </form>
    <p class="form-wrap__footer"><a href="{% url 'login' %}" class="form-wrap__link">Already have an account? Log in</a></p>
</div>
```

### 2.3 Book form (add/edit)

```django
<div class="form-wrap form-wrap--page">
    <h1 class="form-wrap__title">{% if object %}Edit book{% else %}Add book{% endif %}</h1>
    <form method="post" enctype="multipart/form-data" class="form form--light form--book">
        {% csrf_token %}
        {% if form.non_field_errors %}{% include "bookbrief/components/_form_errors.html" with errors=form.non_field_errors %}{% endif %}
        {% for field in form %}
            {% include "bookbrief/components/_form_field.html" with field=field %}
        {% endfor %}
        {% include "bookbrief/components/_form_actions.html" with submit_label=object|yesno:"Save changes,Add book" cancel_url=object|yesno:object.slug,"" %}
    </form>
</div>
```

### 2.4 Summary form (with rich editor)

```django
<div class="form-wrap form-wrap--page">
    <h1 class="form-wrap__title">{% if object %}Edit summary{% else %}Add summary{% endif %}</h1>
    {% if book %}<p class="form-wrap__subtitle">Book: {{ book.title }} by {{ book.author }}</p>{% endif %}
    <form method="post" class="form form--light form--summary" id="summary-form">
        {% csrf_token %}
        {% if form.non_field_errors %}{% include "bookbrief/components/_form_errors.html" with errors=form.non_field_errors %}{% endif %}
        {% include "bookbrief/components/_form_field.html" with field=form.book %}
        {% include "bookbrief/components/_form_field.html" with field=form.summary_type %}
        {% include "bookbrief/components/_form_field.html" with field=form.title %}
        <div class="form-group form-group--rich">
            <label for="id_content" class="form-label">Content</label>
            {% include "bookbrief/components/_rich_editor.html" with field=form.content field_id="id_content" field_name="content" %}
            {% if form.content.errors %}{% include "bookbrief/components/_form_errors.html" with errors=form.content.errors %}{% endif %}
        </div>
        {% include "bookbrief/components/_form_field.html" with field=form.quick_preview %}
        {% include "bookbrief/components/_form_field.html" with field=form.key_takeaways %}
        {% include "bookbrief/components/_form_field.html" with field=form.estimated_reading_minutes %}
        <div class="form-group form-group--checkbox">
            <label class="form-label form-label--checkbox">{{ form.is_public }} Public (visible to everyone)</label>
            {% if form.is_public.errors %}{% include "bookbrief/components/_form_errors.html" with errors=form.is_public.errors %}{% endif %}
        </div>
        {% include "bookbrief/components/_form_actions.html" with submit_label=object|yesno:"Save changes,Add summary" %}
    </form>
</div>
```

### 2.5 Review form (on book detail)

```django
<div class="form-wrap form-wrap--inline">
    <h3 class="form-wrap__title">{% if user_review %}Update your review{% else %}Leave a review{% endif %}</h3>
    <form method="post" class="form form--light form--review">
        {% csrf_token %}
        {% for field in review_form %}
            {% include "bookbrief/components/_form_field.html" with field=field %}
        {% endfor %}
        <p class="form-actions">
            <button type="submit" class="btn btn--primary">{% if user_review %}Update{% else %}Submit{% endif %} review</button>
        </p>
    </form>
</div>
```

### 2.6 Comment form (on summary detail)

```django
<div class="form-wrap form-wrap--inline">
    <h3 class="form-wrap__title">Add a comment</h3>
    <form method="post" action="{% url 'summary_detail' summary.pk %}" class="form form--light form--comment">
        {% csrf_token %}
        {% for field in comment_form %}
            {% include "bookbrief/components/_form_field.html" with field=field %}
        {% endfor %}
        <p class="form-actions"><button type="submit" class="btn btn--primary">Post comment</button></p>
    </form>
</div>
```

### 2.7 Profile form

```django
<div class="form-wrap form-wrap--page">
    <h1 class="form-wrap__title">Profile</h1>
    {% if profile.avatar %}<img src="{{ profile.avatar.url }}" alt="" class="form-wrap__avatar">{% endif %}
    <form method="post" enctype="multipart/form-data" class="form form--light form--profile">
        {% csrf_token %}
        {% for field in form %}
            {% include "bookbrief/components/_form_field.html" with field=field %}
        {% endfor %}
        {% include "bookbrief/components/_form_actions.html" with submit_label="Save profile" %}
    </form>
    <p class="form-wrap__footer form-wrap__footer--muted">Username: {{ user.username }}</p>
</div>
```

---

## 3. Template Folder Structure (Light-Themed Forms)

```
templates/
├── base.html
├── registration/
│   ├── login.html
│   ├── register.html
│   └── logged_out.html
└── bookbrief/
    ├── book_form.html
    ├── book_confirm_delete.html
    ├── summary_form.html
    ├── summary_confirm_delete.html
    ├── profile.html
    └── components/
        ├── _form_field.html      (label + input + errors)
        ├── _form_errors.html     (ul of errors)
        ├── _form_actions.html    (submit + cancel)
        ├── _rich_editor.html
        └── _rich_editor_js.html
```

Inline forms (review, comment) live inside book_detail.html and summary_detail.html; they use the same `_form_field` and `_form_errors` components.

---

## 4. Reusable Components Notes

| Component | Purpose | Passed context |
|-----------|---------|----------------|
| `_form_field.html` | Single field: label, widget, error list. Handles text, select, textarea, checkbox. | `field` (BoundField) |
| `_form_errors.html` | List of error strings with light-theme error styling. | `errors` (list) |
| `_form_actions.html` | Submit button + optional cancel link. Consistent `.btn .btn--primary` and `.btn--secondary`. | `submit_label`, `cancel_url` (optional) |
| `_rich_editor.html` | Quill container + hidden textarea; light theme via Quill CSS override. | `field`, `field_id`, `field_name` |

**Form wrapper classes:**
- `.form-wrap` – White/surface background, padding, border-radius, shadow.
- `.form-wrap--auth` – Centered, max-width for login/register.
- `.form-wrap--page` – Full width within container for book/summary/profile.
- `.form-wrap--inline` – No full card; for review/comment inside content.

**Input classes (applied via CSS to `.form--light`):**
- `.form-input` – text, email, password, number, search.
- `.form-select` – select.
- `.form-textarea` – textarea.
- `.form-checkbox` – checkbox (with `.form-label--checkbox`).

---

## 5. UX Notes for Light Theme

- **Contrast:** Text `#0f172a` on white `#ffffff` meets WCAG AA. Muted text `#64748b` for labels and hints.
- **Focus:** All inputs and buttons use `outline: 2px solid var(--border-focus)` and `outline-offset: 2px` for focus visibility.
- **Errors:** Red border on invalid fields; error list with `.form-errors` and light red background.
- **Spacing:** Form groups use consistent margin-bottom (e.g. 1.25rem). Form-wrap padding 1.5rem–2rem.
- **Buttons:** Primary solid blue; secondary/cancel as text or outline. Consistent height and padding.
- **Rich editor:** Quill toolbar and editor background in light theme (white/surface); border and shadow consistent with other inputs.
- **Responsive:** Form-wrap and inputs full width on mobile; max-width on auth forms (e.g. 400px).
