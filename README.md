# RecipeBoxd (Django + MySQL)

This repository now ships a **Django** implementation (English UI) split into two apps to match the team modules:

- **Member 2** (Recipe & Review Module)
  - Backend: `Member2Backend/recipes/`
  - Frontend: `Member2Frontend/recipes/`
- **Member 3** (Ingredient Search & Social Features)
  - Backend: `Member3Backend/social/`
  - Frontend: `Member3Frontend/social/`

## Quickstart

1) Install dependencies:

```bash
python -m pip install -r requirements_django.txt
```

2) Configure environment:

- Copy `.env.django.example` to `.env`
- Set `DATABASE_URL` (MySQL recommended). If your password contains `@`, encode it as `%40`.
- If you use MySQL, install the driver: `python -m pip install mysql-connector-python`

Example:

```bash
DATABASE_URL="mysql://root:Mysql%402025@127.0.0.1:3306/recipeboxd_django?charset=utf8mb4"
DJANGO_SECRET_KEY="change-me"
DJANGO_DEBUG=1
```

3) Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

4) Seed demo data:

```bash
python manage.py seed_demo
```

Demo users: `alice`, `bob`, `chef_lee`, `admin1` (password: `demo1234`)

5) Start the server:

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Member 2 - Recipe & Review Module

- CRUD recipes (create/edit/delete)
- Recipe list & detail pages
- AJAX review upsert (create/edit) + delete (no full page reload)
- Rating system (1-5) + dynamic star display
- Tests: `Member2Backend/recipes/tests.py`

## Member 3 - Ingredient Search & Social Features

- Ingredient model + Recipe<->Ingredient Many-to-Many
- Ingredient-based search (strict/loose) with AJAX results
- Follow/unfollow users (AJAX)
- Wishlist / cooked toggles (AJAX)
- Wishlist page + review notifications page
- Tests: `Member3Backend/social/tests.py`

## User Guide

### 1) Sign in / Demo Accounts

- Demo users are created by: `python manage.py seed_demo`
- Demo accounts: `alice`, `bob`, `chef_lee`, `admin1`
- Password for all demo accounts: `demo1234`
- Sign in page: `/accounts/login/`

### 2) Browse Recipes

- Home / list page: `/`
- Click a recipe card to open the detail page.
- Each recipe card may show a photo thumbnail, cooking time, ingredients, and rating summary.

### 3) Create / Edit / Delete a Recipe (Member 2)

- Create recipe: click **Create Recipe** in the top navigation (or visit `/recipes/new/`)
- You can upload an optional recipe photo while creating/editing.
  - Stored locally under: `static/uploads/recipes/`
- Edit/delete: open your own recipe detail page and use **Edit** / **Delete** buttons.

### 4) Add / Edit / Delete Reviews (AJAX, Member 2)

- Open a recipe detail page and submit **Your review** (rating 1-5 + comment).
- Submitting a review uses AJAX (no full page reload).
- If you submit again for the same recipe, it updates your previous review.
- You can delete your own review using the **Delete** button on your review item.

### 5) Ingredient Search (AJAX, Member 3)

- Go to **Ingredient Search** (or `/social/ingredients/search/`)
- Select ingredients, choose:
  - **Strict**: recipe requires only selected ingredients (all required)
  - **Loose**: any overlap is a match
- Click **Search** to update results without a full page reload.

### 6) Wishlist / Cooked (Member 3)

- On recipe detail page, use:
  - **Add to wishlist / In wishlist (remove)**
  - **Mark as cooked / Cooked (undo)**
- Wishlist page: `/social/wishlist/`

### 7) Follow / Unfollow Users (Member 3)

- Open a user profile page: `/social/u/<username>/`
- Click **Follow** / **Following** to toggle without refresh.

### 8) Review Notifications (Member 3)

- Notifications page: `/social/notifications/`
- Shows reviews left by other users on recipes you authored.
  - Count is also shown in the top-right user dropdown.

### 9) World Map (Countries Completed)

- Tag a recipe with **Country of origin** in the create/edit recipe form.
- Mark that recipe as **cooked** on the recipe detail page.
- World map page: `/social/map/`
  - Highlights countries you have completed (based on cooked recipes).

## Offline Map Setup (Optional)

`/social/map/` loads the map library from a CDN by default. To run fully offline, download the assets and switch the template to `{% static %}` paths.

PowerShell example:

```powershell
mkdir static\\vendor\\jsvectormap\\css, static\\vendor\\jsvectormap\\js, static\\vendor\\jsvectormap\\maps -Force
iwr https://cdn.jsdelivr.net/npm/jsvectormap@1.5.3/dist/css/jsvectormap.min.css -OutFile static\\vendor\\jsvectormap\\css\\jsvectormap.min.css
iwr https://cdn.jsdelivr.net/npm/jsvectormap@1.5.3/dist/js/jsvectormap.min.js -OutFile static\\vendor\\jsvectormap\\js\\jsvectormap.min.js
iwr https://cdn.jsdelivr.net/npm/jsvectormap@1.5.3/dist/maps/world.js -OutFile static\\vendor\\jsvectormap\\maps\\world.js
```

Then update `Member3Frontend/social/world_map.html` to use:

- `{% static 'vendor/jsvectormap/css/jsvectormap.min.css' %}`
- `{% static 'vendor/jsvectormap/js/jsvectormap.min.js' %}`
- `{% static 'vendor/jsvectormap/maps/world.js' %}`
