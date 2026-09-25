"""
URL configuration for dproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dapp import views # import view from app
from dapp import api_views # REST API (Module 2)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index_view, name='index'),
    path('hello/', views.hello_view, name='hello'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path("cart/", views.cart_view, name="cart"),
    path('item/', views.item_view, name="item"),
    path('store/', views.store_view, name="store"),  # API-driven SPA (Module 2)
    # set view to be accessed by route

    # --- REST API (Module 2 / Module 3) ---
    path('api/register/', api_views.api_register, name='api_register'),
    path('api/login/', api_views.api_login, name='api_login'),
    path('api/me/', api_views.api_me, name='api_me'),
    path('api/products/', api_views.api_products, name='api_products'),
    path('api/cart/', api_views.api_cart, name='api_cart'),
]
