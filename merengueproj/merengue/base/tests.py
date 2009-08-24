from django.test import TestCase
from merengue.base.models import BaseContent


class BaseModelTests(TestCase):
    fixtures = ['devel_data']

    def test_class_name_is_not_empty(self):
        class_names = BaseContent.objects.different_class_names()
        self.assert_(None not in class_names)
