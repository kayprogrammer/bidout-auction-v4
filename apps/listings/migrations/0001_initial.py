# Generated by Django 4.2.2 on 2023-06-24 22:02

import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("common", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "pkid",
                    models.BigAutoField(
                        editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=30, unique=True)),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        always_update=True,
                        editable=False,
                        populate_from="name",
                        unique=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Listing",
            fields=[
                (
                    "pkid",
                    models.BigAutoField(
                        editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=70)),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        always_update=True,
                        editable=False,
                        populate_from="title",
                        unique=True,
                    ),
                ),
                ("desc", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "highest_bid",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                ("bids_count", models.IntegerField(default=0)),
                ("closing_date", models.DateTimeField(null=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "auctioneer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        to_field="id",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="listings.category",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="common.file",
                        to_field="id",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="WatchList",
            fields=[
                (
                    "pkid",
                    models.BigAutoField(
                        editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "guest",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="common.guestuser",
                    ),
                ),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="listings.listing",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="watchlists",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="Bid",
            fields=[
                (
                    "pkid",
                    models.BigAutoField(
                        editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="listings",
                        to="listings.listing",
                        to_field="id",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="listings",
                        to=settings.AUTH_USER_MODEL,
                        to_field="id",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="watchlist",
            constraint=models.UniqueConstraint(
                fields=("user", "listing"), name="unique_user_listing_watchlists"
            ),
        ),
        migrations.AddConstraint(
            model_name="watchlist",
            constraint=models.UniqueConstraint(
                fields=("guest", "listing"), name="unique_guest_listing_watchlists"
            ),
        ),
        migrations.AddConstraint(
            model_name="bid",
            constraint=models.UniqueConstraint(
                fields=("user", "listing"), name="unique_user_listing_bid"
            ),
        ),
        migrations.AddConstraint(
            model_name="bid",
            constraint=models.UniqueConstraint(
                fields=("listing", "amount"), name="unique_listing_amount_bid"
            ),
        ),
    ]
