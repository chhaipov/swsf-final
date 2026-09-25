"""
Broken Shop REST API (Module 2 + Module 3).

This is a deliberately vulnerable teaching API. Every weakness below is
intentional and tagged with a `VULN (...)` comment so instructors can grade
against it. Do NOT copy this style into real code.

Auth model: token-based. POST /api/login/ returns a Bearer token; send it as
    Authorization: Bearer <token>
on the protected endpoints.
"""

import json
import secrets

from django.db import connection
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Item, CartItem, ApiToken


def _json_body(request):
    """Read a JSON request body, tolerating form posts too."""
    if request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            pass
    return request.POST


def _current_token(request):
    """Return the ApiToken for the Authorization: Bearer <key> header, or None."""
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if not header.lower().startswith("bearer "):
        return None
    key = header.split(" ", 1)[1].strip()
    return ApiToken.objects.filter(key=key).first()


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@csrf_exempt
def api_register(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    data = _json_body(request)
    username = data.get("username")
    password = data.get("password")
    email = data.get("email", "")
    if not username or not password:
        return JsonResponse({"error": "username and password required"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "user exists"}, status=409)
    user = User.objects.create_user(username=username, password=password, email=email)
    token = ApiToken.objects.create(key=secrets.token_hex(16), user=user)
    return JsonResponse({"id": user.id, "username": user.username, "token": token.key})


@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    data = _json_body(request)
    user = authenticate(
        request, username=data.get("username"), password=data.get("password")
    )
    if user is None:
        return JsonResponse({"error": "invalid credentials"}, status=401)
    # A fresh token every login; old tokens are never revoked (intentional).
    token = ApiToken.objects.create(key=secrets.token_hex(16), user=user)
    return JsonResponse({"token": token.key, "user_id": user.id})


def api_me(request):
    token = _current_token(request)
    if token is None:
        return JsonResponse({"error": "missing or invalid token"}, status=401)
    u = token.user
    return JsonResponse({"id": u.id, "username": u.username, "email": u.email})


# ---------------------------------------------------------------------------
# Product search  (Module 4: SQL Injection)
# ---------------------------------------------------------------------------

def api_products(request):
    """Search products by name.

    VULN (SQL Injection): the `q` parameter is concatenated straight into a raw
    SQL string instead of using a parameterised query or the ORM. Try:
        /api/products/?q=nothing' OR '1'='1
        /api/products/?q=x' UNION SELECT id, password, 1 FROM auth_user --
    """
    q = request.GET.get("q", "")
    sql = (
        "SELECT id, name, price FROM dapp_item "
        "WHERE name LIKE '%" + q + "%'"
    )
    results = []
    with connection.cursor() as cursor:
        cursor.execute(sql)  # raw, unparameterised -> injectable
        for row in cursor.fetchall():
            results.append({"id": row[0], "name": row[1], "price": row[2]})
    return JsonResponse({"query": q, "results": results})


# ---------------------------------------------------------------------------
# Cart  (Module 2 Lab 4 / Module 4: Broken Access Control / IDOR)
# ---------------------------------------------------------------------------

def api_cart(request):
    """Return a user's cart.

    VULN (Broken authorization / IDOR): a valid token is required, but the
    endpoint returns whatever `user_id` the caller asks for and never checks
    that it matches the token's owner. Any logged-in user can read every other
    user's cart:  GET /api/cart/?user_id=1  with their own token.
    """
    token = _current_token(request)
    if token is None:
        return JsonResponse({"error": "missing or invalid token"}, status=401)

    user_id = request.GET.get("user_id", token.user.id)  # trusts client input
    items = CartItem.objects.filter(user_id=user_id)
    data = [
        {"item": ci.item.name, "price": ci.item.price, "quantity": ci.quantity}
        for ci in items
    ]
    return JsonResponse({"user_id": user_id, "cart": data})
