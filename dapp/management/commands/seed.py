"""
Seed Broken Shop with realistic demo data so it behaves like a complete shop.

    python manage.py seed          # add/update data, keep existing
    python manage.py seed --reset  # wipe items/carts/tokens and reseed

Creates a catalogue of products across categories, several demo users, and a
few populated carts (so the IDOR labs have real data to leak).
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from dapp.models import Item, CartItem, ApiToken


PRODUCTS = [
    # name, price, category, stock, image_url, description
    ("Aurora Wireless Headphones", 129, "Audio", 40,
     "https://picsum.photos/seed/headphones/600/400",
     "Over-ear Bluetooth headphones with active noise cancelling and 30-hour battery."),
    ("Nimbus Mechanical Keyboard", 89, "Computers", 60,
     "https://picsum.photos/seed/keyboard/600/400",
     "Hot-swappable 75% mechanical keyboard with tactile brown switches and RGB."),
    ("Pixel Pro Webcam 4K", 75, "Computers", 35,
     "https://picsum.photos/seed/webcam/600/400",
     "4K UHD webcam with autofocus and dual noise-cancelling mics."),
    ("Voyager 20000mAh Power Bank", 45, "Accessories", 120,
     "https://picsum.photos/seed/powerbank/600/400",
     "Fast-charging USB-C power bank that tops up a laptop or two phones."),
    ("Terra Insulated Bottle 1L", 24, "Outdoors", 200,
     "https://picsum.photos/seed/bottle/600/400",
     "Double-walled stainless steel bottle, keeps drinks cold 24h / hot 12h."),
    ("Summit 40L Hiking Backpack", 110, "Outdoors", 25,
     "https://picsum.photos/seed/backpack/600/400",
     "Lightweight weather-resistant pack with rain cover and hydration sleeve."),
    ("Lumen Smart Desk Lamp", 39, "Home", 80,
     "https://picsum.photos/seed/lamp/600/400",
     "Dimmable LED desk lamp with wireless charging base and USB port."),
    ("Barista Pro Coffee Grinder", 149, "Kitchen", 18,
     "https://picsum.photos/seed/grinder/600/400",
     "Conical burr grinder with 40 grind settings for espresso to French press."),
    ("Cloud9 Ergonomic Chair", 249, "Furniture", 12,
     "https://picsum.photos/seed/chair/600/400",
     "Mesh-back ergonomic office chair with adjustable lumbar and armrests."),
    ("Pulse Fitness Smartwatch", 159, "Wearables", 50,
     "https://picsum.photos/seed/watch/600/400",
     "GPS smartwatch with heart-rate, SpO2, and 7-day battery life."),
    ("Echo Mini Bluetooth Speaker", 34, "Audio", 90,
     "https://picsum.photos/seed/speaker/600/400",
     "Pocket-size waterproof speaker with surprisingly big sound."),
    ("Nova Wireless Mouse", 29, "Computers", 140,
     "https://picsum.photos/seed/mouse/600/400",
     "Silent-click wireless mouse with adjustable DPI and USB-C charging."),
    ("Zen Bamboo Monitor Stand", 27, "Home", 70,
     "https://picsum.photos/seed/standb/600/400",
     "Natural bamboo monitor riser with a storage drawer and phone slot."),
    ("Trailhead Merino Socks (3-pack)", 22, "Outdoors", 300,
     "https://picsum.photos/seed/socks/600/400",
     "Breathable merino wool hiking socks, cushioned heel and toe."),
    ("Chef's Edge 8\" Knife", 64, "Kitchen", 45,
     "https://picsum.photos/seed/knife/600/400",
     "High-carbon stainless chef's knife, hand-finished and razor sharp."),
    ("Halo LED Ring Light 18\"", 55, "Photography", 30,
     "https://picsum.photos/seed/ringlight/600/400",
     "18-inch bi-colour ring light with phone mount and remote."),
]

# username, password, email, is_staff/superuser
USERS = [
    ("admin", "admin123", "admin@brokenshop.local", True),
    ("alice", "Passw0rd!", "alice@example.com", False),
    ("bob",   "Bobstrong9", "bob@example.com", False),
    ("carol", "Carol#2024", "carol@example.com", False),
]

# who has what in their cart: username -> [(product_name, qty), ...]
CARTS = {
    "alice": [("Aurora Wireless Headphones", 1), ("Nova Wireless Mouse", 2)],
    "bob":   [("Cloud9 Ergonomic Chair", 1), ("Lumen Smart Desk Lamp", 2),
              ("Echo Mini Bluetooth Speaker", 1)],
    "carol": [("Summit 40L Hiking Backpack", 1), ("Terra Insulated Bottle 1L", 2),
              ("Trailhead Merino Socks (3-pack)", 3)],
}


class Command(BaseCommand):
    help = "Seed Broken Shop with demo products, users, and carts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true",
            help="Delete existing items, carts, and API tokens before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            CartItem.objects.all().delete()
            ApiToken.objects.all().delete()
            Item.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared items, carts, and tokens."))

        # Products
        by_name = {}
        for name, price, category, stock, image, desc in PRODUCTS:
            item, _ = Item.objects.update_or_create(
                name=name,
                defaults={
                    "price": price, "category": category, "stock": stock,
                    "image_url": image, "description": desc,
                },
            )
            by_name[name] = item
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PRODUCTS)} products."))

        # Users
        users = {}
        for username, password, email, is_admin in USERS:
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": email},
            )
            user.email = email
            user.set_password(password)
            user.is_staff = is_admin
            user.is_superuser = is_admin
            user.save()
            users[username] = user
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(USERS)} users (admin/admin123, alice/Passw0rd!, ...)."))

        # Carts
        cart_count = 0
        for username, lines in CARTS.items():
            user = users[username]
            CartItem.objects.filter(user=user).delete()
            for product_name, qty in lines:
                CartItem.objects.create(user=user, item=by_name[product_name], quantity=qty)
                cart_count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {cart_count} cart items."))
        self.stdout.write(self.style.SUCCESS("Done. Log in as alice / Passw0rd!"))
