from django.db import models

from merengue.base.models import BaseContent


class Vote(models.Model):
    vote = models.IntegerField()
    content = models.ForeignKey(BaseContent)
