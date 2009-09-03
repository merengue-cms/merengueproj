from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.models import Comment


class Feedback(Comment):

    parent = models.ForeignKey('Feedback', verbose_name=_('parent feedback'),
                               null=True, blank=True)
