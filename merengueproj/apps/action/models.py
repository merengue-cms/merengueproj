from django.db import models

from registry.models import RegisteredItem


class RegisteredAction(RegisteredItem):
    name = models.CharField(max_length=100)
