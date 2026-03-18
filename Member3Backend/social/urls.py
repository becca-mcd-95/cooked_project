from django.urls import path

from . import views

urlpatterns = [
    path("u/<str:username>/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("ingredients/search/", views.ingredient_search, name="ingredient_search"),
    path("ingredients/filter/", views.ingredient_filter, name="ingredient_filter"),
    path("map/", views.world_map, name="world_map"),
    path("follow/<str:username>/toggle/", views.follow_toggle, name="follow_toggle"),
    path("recipes/<int:recipe_id>/status/toggle/", views.status_toggle, name="status_toggle"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("notifications/", views.notifications, name="notifications"),
]
