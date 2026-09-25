from django.contrib.auth.models import User # import default user
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="General")
    image_url = models.CharField(max_length=300, blank=True, default="")
    stock = models.IntegerField(default=100)

    def __str__(self):
        return self.name

class CartItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.item.name


class ApiToken(models.Model):
    """Very small Bearer-token store for the REST API (Module 2).

    NOTE (intentional weaknesses for the course):
      - token has no expiry / rotation
      - token is a plain random hex string stored in clear text
    """
    key = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} : {self.key[:8]}..."
