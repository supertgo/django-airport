from django.db import models

from app_core.utils.interfaces import UUIDCustomModel


# Create your models here.
class Airport(UUIDCustomModel):
    state = models.CharField(max_length=2, blank=True, null=True)
    iata = models.CharField(max_length=3, unique=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    lat = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    inactive_reason = models.TextField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "airport"
