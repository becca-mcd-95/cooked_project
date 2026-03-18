from __future__ import annotations

from django.db.models import Count

from models import Review


def notification_count(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"notification_count": 0}
    cnt = (
        Review.objects.filter(recipe__author=request.user)
        .exclude(user=request.user)
        .aggregate(c=Count("id"))
        .get("c")
        or 0
    )
    return {"notification_count": cnt}

