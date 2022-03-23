"""Models in the clubs app."""

import uuid

from django.db import models


class MyUUIDModel(models.Model):
    class Meta:
        app_label = "clubs"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
