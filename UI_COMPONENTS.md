# UI Components – Buttons, Search, and Inputs

## 1. UI Component Style Guidelines

### 1.1 Buttons

| Token | Value | Use |
|-------|--------|-----|
| **Base** | `.btn` | All buttons and button-like links |
| **Primary** | `.btn--primary` | Main actions: Add, Submit, Save, Log in, Register |
| **Secondary** | `.btn--secondary` | Cancel, back, low emphasis |
| **Danger** | `.btn--danger` | Delete, remove destructive actions |
| **Small** | `.btn--sm` | Inline actions, pagination (optional) |

**Rules:**
- Padding: `0.6rem 1.25rem` (base), `0.5rem 1rem` (sm).
- Border-radius: `var(--radius)` (8px).
- Font: `1rem`, `font-weight: 500`.
- Primary: solid `--primary`, white text; hover: `--primary-hover`, slight shadow.
- Secondary: transparent bg, `--border` border, `--text-muted` text; hover: `--surface` bg.
- Danger: solid `--error` or red; hover: darker red.
- Focus: `outline: 2px solid var(--border-focus)`; `outline-offset: 2px`.
- Disabled: `opacity: 0.6`, `cursor: not-allowed`, no hover.

**Action mapping:**
- Add book / Add summary / Submit / Save / Log in / Register → `btn btn--primary`
- Cancel / View all → `btn btn--secondary`
- Delete → `btn btn--danger` (or `btn--primary` for confirm delete)
- Edit / small links that are actions → `btn btn--secondary` or `btn--sm`

### 1.2 Search boxes

| Token | Value | Use |
|-------|--------|-----|
| **Container** | `.search-box` | Wrapper for input + submit button (and optional select) |
| **Input** | `.search-box__input` | Single search input; same height as button |
| **Select** | `.search-box__select` | Optional category/type filter |
| **Submit** | `.search-box__btn` or `.btn.btn--primary` | Same as primary button; aligned right |

**Rules:**
- One shared placeholder: **"Search books or authors…"** (books) / **"Search summaries…"** (summaries) / **"Search…"** (generic).
- Height: input and button same (e.g. 40px); border 1px solid `--border`; radius `var(--radius)`.
- Focus: input border `--border-focus`, box-shadow `0 0 0 3px rgba(37,99,235,0.15)`.
- Spacing: gap between input and button 0.5rem; optional select 0.5rem from input.
- Responsive: stack on small screens (input full width, select full width, button full width).

### 1.3 Form fields (inputs, selects, textareas)

- Use existing `.form--light` and `.form-group`; inputs already share border, padding, focus.
- Ensure all text inputs, selects, textareas use the same border, radius, padding, and focus ring as in LIGHT_THEME_FORMS.

---

## 2. Jinja Snippets

### 2.1 Button component

**Usage:** `{% include "bookbrief/components/_button.html" with href=url label="Add book" variant="primary" %}`  
**Or:** `{% include "bookbrief/components/_button.html" with label="Submit" variant="primary" type="submit" %}`

```django
{# _button.html: Pass href (link) OR type="submit" (button). Optional: variant=primary|secondary|danger, size=sm #}
{% if href %}
    <a href="{{ href }}" class="btn btn--{{ variant|default:'primary' }}{% if size %} btn--{{ size }}{% endif %}" {% if aria_label %}aria-label="{{ aria_label }}"{% endif %}>{{ label }}</a>
{% else %}
    <button type="{{ type|default:'submit' }}" class="btn btn--{{ variant|default:'primary' }}{% if size %} btn--{{ size }}{% endif %}" {% if aria_label %}aria-label="{{ aria_label }}"{% endif %}>{{ label }}</button>
{% endif %}
```

### 2.2 Search box component

**Usage:** `{% include "bookbrief/components/_search_box.html" with action=request.path name="search" value=request.GET.search placeholder="Search books or authors…" categories=categories %}`

```django
{# _search_box.html: Pass action, name, value, placeholder. Optional: categories (for select), select_name="category" #}
<form method="get" action="{{ action }}" class="search-box" role="search">
    <label for="search-box-{{ name }}" class="visually-hidden">{{ placeholder }}</label>
    <input id="search-box-{{ name }}" type="search" name="{{ name }}" value="{{ value }}" class="search-box__input" placeholder="{{ placeholder }}" aria-label="{{ placeholder }}">
    {% if categories %}
        <select name="{{ select_name|default:'category' }}" class="search-box__select" aria-label="Category">
            <option value="">All categories</option>
            {% for cat in categories %}
                <option value="{{ cat.slug }}" {% if request.GET.category == cat.slug %}selected{% endif %}>{{ cat.name }}</option>
            {% endfor %}
        </select>
    {% endif %}
    <button type="submit" class="btn btn--primary search-box__btn">Search</button>
</form>
```

### 2.3 Form actions (reuse existing)

```django
<p class="form-actions">
    <button type="submit" class="btn btn--primary">{{ submit_label }}</button>
    {% if cancel_url %}<a href="{{ cancel_url }}" class="btn btn--secondary">Cancel</a>{% endif %}
</p>
```

---

## 3. Base Template Structure for Reusable Elements

**Base does not define new blocks for buttons/search.** Include components in page templates.

- **Buttons:** Use `_button.html` with `href` + `label` + `variant`, or `<button class="btn btn--primary">` / `<a class="btn btn--secondary" href="...">`.
- **Search:** Use `_search_box.html` on home (hero), book list, summary list; pass `action`, `name`, `value`, `placeholder`, and optional `categories`.

---

## 4. UX Notes for Consistent Interaction

- **One search pattern:** Same `.search-box` layout and placeholder style on hero, book list, and summary list.
- **Actions as buttons:** No plain-text links for Add / Edit / Delete / Submit / Save; use `.btn` and variant.
- **Hover:** All buttons and search input get a clear hover state (darker primary, light background secondary).
- **Focus:** Visible focus ring (2px outline) on all interactive elements for keyboard users.
- **Disabled:** Buttons that submit forms can use `disabled`; style with opacity and cursor.
- **Responsive:** Search box stacks on narrow viewports; buttons in form-actions can stack and full-width on mobile.

---

## 5. Example Usage

| Page | Search | Buttons |
|------|--------|---------|
| **Home** | Hero: `_search_box.html` action=book_list, placeholder="Search books or authors…" | Section CTAs: `<a href="..." class="btn btn--secondary">View all books</a>` |
| **Book list** | `_search_box.html` action=request.path, categories=categories, placeholder="Search books or authors…" | "Add book" → `_button.html` href=book_add, variant=primary |
| **Summary list** | `_search_box.html` action=request.path, placeholder="Search summaries…" | "Add summary" → `_button.html` href=summary_add, variant=primary |
| **Book detail** | — | "Add summary" / "Edit book" / "Delete book" → `btn btn--primary`, `btn btn--secondary`, `btn btn--danger` |
| **Dashboard** | — | "Add book", "Add summary", "View all" → `btn btn--primary`, `btn btn--secondary` |
| **Forms** | — | Submit → `btn btn--primary`; Cancel → `btn btn--secondary`; Delete (confirm) → `btn btn--danger` |
