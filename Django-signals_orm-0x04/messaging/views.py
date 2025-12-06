#!/usr/bin/env python3
"""Views for messaging app.

"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import User


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_user(request):
    """Delete the authenticated user's account."""
    user = request.user
    user.delete()
    return JsonResponse(
        {"message": "User account deleted successfully."},
        status=200
    )

