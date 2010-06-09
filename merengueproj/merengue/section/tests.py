"""
Section tests
"""

__test__ = {"doctest": """

Testing menu creation when a section is created.

>>> from merengue.section.models import Section
>>> section = Section.objects.create(name_en='foo section', slug='foo-section')
>>> section.main_menu is None
False

"""}
