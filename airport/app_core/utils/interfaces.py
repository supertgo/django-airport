import uuid
from django.db import models


class UUIDCustomModel(models.Model):
    """
    Model to replace incremental id for best security pratices
    """

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )

    class Meta:
        abstract = True
