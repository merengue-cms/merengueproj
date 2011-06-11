# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models, connection
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.core.management import sql
from django.core.management.color import no_style
from django.utils.encoding import smart_unicode

from merengue.base.models import BaseContent
from merengue.section.models import BaseSection


class SectionChildOne(BaseSection):
    child_foo_attribute = models.CharField(max_length=100, null=True, blank=True)


class SectionChildTwo(BaseSection):
    child_bar_attribute = models.CharField(max_length=100, null=True, blank=True)


class ChildOfSectionChildOne(SectionChildOne):
    child_span_attribute = models.CharField(max_length=100, null=True, blank=True)


class ChildOfChildOfSectionChildOne(ChildOfSectionChildOne):
    child_eggs_attribute = models.CharField(max_length=100, null=True, blank=True)


class ChildOfSectionChildTwo(SectionChildTwo):
    child_span_attribute = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True


class ChildOfChildOfSectionChildTwo(ChildOfSectionChildTwo):
    child_eggs_attribute = models.CharField(max_length=100, null=True, blank=True)


models = [SectionChildOne, SectionChildTwo, ChildOfSectionChildOne, ChildOfChildOfSectionChildOne,
          ChildOfChildOfSectionChildTwo]


def create_table(*models):
    """ Create all tables for the given models """
    cursor = connection.cursor()

    def execute(statements):
        for statement in statements:
            cursor.execute(statement)

    STYLE = no_style()
    table_names = connection.introspection.get_table_list(cursor)
    for model in models:
        if not model._meta.db_table in table_names:
            execute(connection.creation.sql_create_model(model, STYLE)[0])
            execute(connection.creation.sql_indexes_for_model(model, STYLE))
            execute(sql.custom_sql_for_model(model, STYLE, connection))
    for model in models:
        opts = model._meta
        try:
            ct = ContentType.objects.get(app_label=opts.app_label,
                                         model=opts.object_name.lower())
        except ContentType.DoesNotExist:
            ct = ContentType(name=smart_unicode(opts.verbose_name_raw),
                             app_label=opts.app_label, model=opts.object_name.lower())
            ct.save()


class BaseModelTests(TestCase):
    fixtures = ['devel_data']

    def test_class_name_is_not_empty(self):
        class_names = BaseContent.objects.different_class_names()
        self.assert_(None not in class_names)


class GetRealInstanceTests(TestCase):

    def setUp(self):
        create_table(*models)
        self.obj_basecontent = BaseContent.objects.create(
            name='Base content', slug='base-content',
            )
        self.obj_basesection = BaseSection.objects.create(
            name='Base section', slug='base-section',
            )
        self.obj_sectionchildone = SectionChildOne.objects.create(
            name='Section child one', slug='section-child-one',
            )
        self.obj_sectionchildtwo = SectionChildTwo.objects.create(
            name='Section child two', slug='section-child-two',
            )
        self.obj_childofsectionchildone = ChildOfSectionChildOne.objects.create(
            name='Child of section child one',
            slug='child-of-section-child-one',
            )
        self.obj_childofchildofsectionchildone = ChildOfChildOfSectionChildOne.objects.create(
            name='Child of child of section child one',
            slug='child-of-child-of-section-child-one',
            )
        self.obj_childofchildofsectionchildtwo = ChildOfChildOfSectionChildTwo.objects.create(
            name='Child of child of section child two',
            slug='child-of-child-of-section-child-two',
            )

    def test_check_own_objects(self):
        # We check the correctness of each object by itself
        self.assertEquals(self.obj_basecontent.get_real_instance().pk, self.obj_basecontent.pk)
        self.assertEquals(self.obj_basecontent.get_real_instance().__class__,
                          BaseContent)

        self.assertEquals(self.obj_basesection.get_real_instance().pk, self.obj_basesection.pk)
        self.assertEquals(self.obj_basesection.get_real_instance().__class__,
                          BaseSection)

        self.assertEquals(self.obj_sectionchildone.get_real_instance().pk, self.obj_sectionchildone.pk)
        self.assertEquals(self.obj_sectionchildone.get_real_instance().__class__,
                          SectionChildOne)

        self.assertEquals(self.obj_sectionchildtwo.get_real_instance().pk, self.obj_sectionchildtwo.pk)
        self.assertEquals(self.obj_sectionchildtwo.get_real_instance().__class__,
                          SectionChildTwo)

        self.assertEquals(self.obj_childofsectionchildone.get_real_instance().pk,
                          self.obj_childofsectionchildone.pk)
        self.assertEquals(self.obj_childofsectionchildone.get_real_instance().__class__,
                          ChildOfSectionChildOne)

        self.assertEquals(self.obj_childofchildofsectionchildone.get_real_instance().pk,
                          self.obj_childofchildofsectionchildone.pk)
        self.assertEquals(self.obj_childofchildofsectionchildone.get_real_instance().__class__,
                          ChildOfChildOfSectionChildOne)

        self.assertEquals(self.obj_childofchildofsectionchildtwo.get_real_instance().pk,
                          self.obj_childofchildofsectionchildtwo.pk)
        self.assertEquals(self.obj_childofchildofsectionchildtwo.get_real_instance().__class__,
                          ChildOfChildOfSectionChildTwo)

    def test_check_as_base_content(self):
        # First, we fetch all the items using BaseContent instances
        bc_1 = BaseContent.objects.get(slug='base-content')
        bc_2 = BaseContent.objects.get(slug='base-section')
        bc_3 = BaseContent.objects.get(slug='section-child-one')
        bc_4 = BaseContent.objects.get(slug='section-child-two')
        bc_5 = BaseContent.objects.get(slug='child-of-section-child-one')
        bc_6 = BaseContent.objects.get(slug='child-of-child-of-section-child-one')
        bc_7 = BaseContent.objects.get(slug='child-of-child-of-section-child-two')

        self.assertEquals(bc_1.get_real_instance().pk, self.obj_basecontent.pk)
        self.assertEquals(bc_1.get_real_instance().name, self.obj_basecontent.name)
        self.assertEquals(bc_1.get_real_instance().slug, self.obj_basecontent.slug)
        self.assertEquals(bc_1.get_real_instance().__class__, BaseContent)

        self.assertEquals(bc_2.get_real_instance().pk, self.obj_basesection.pk)
        self.assertEquals(bc_2.get_real_instance().name, self.obj_basesection.name)
        self.assertEquals(bc_2.get_real_instance().slug, self.obj_basesection.slug)
        self.assertEquals(bc_2.get_real_instance().__class__, BaseSection)

        self.assertEquals(bc_3.get_real_instance().pk, self.obj_sectionchildone.pk)
        self.assertEquals(bc_3.get_real_instance().name, self.obj_sectionchildone.name)
        self.assertEquals(bc_3.get_real_instance().slug, self.obj_sectionchildone.slug)
        self.assertEquals(bc_3.get_real_instance().__class__, SectionChildOne)

        self.assertEquals(bc_4.get_real_instance().pk, self.obj_sectionchildtwo.pk)
        self.assertEquals(bc_4.get_real_instance().name, self.obj_sectionchildtwo.name)
        self.assertEquals(bc_4.get_real_instance().slug, self.obj_sectionchildtwo.slug)
        self.assertEquals(bc_4.get_real_instance().__class__, SectionChildTwo)

        self.assertEquals(bc_5.get_real_instance().pk, self.obj_childofsectionchildone.pk)
        self.assertEquals(bc_5.get_real_instance().name, self.obj_childofsectionchildone.name)
        self.assertEquals(bc_5.get_real_instance().slug, self.obj_childofsectionchildone.slug)
        self.assertEquals(bc_5.get_real_instance().__class__, ChildOfSectionChildOne)

        self.assertEquals(bc_6.get_real_instance().pk, self.obj_childofchildofsectionchildone.pk)
        self.assertEquals(bc_6.get_real_instance().name, self.obj_childofchildofsectionchildone.name)
        self.assertEquals(bc_6.get_real_instance().slug, self.obj_childofchildofsectionchildone.slug)
        self.assertEquals(bc_6.get_real_instance().__class__, ChildOfChildOfSectionChildOne)

        self.assertEquals(bc_7.get_real_instance().pk, self.obj_childofchildofsectionchildtwo.pk)
        self.assertEquals(bc_7.get_real_instance().name, self.obj_childofchildofsectionchildtwo.name)
        self.assertEquals(bc_7.get_real_instance().slug, self.obj_childofchildofsectionchildtwo.slug)
        self.assertEquals(bc_7.get_real_instance().__class__, ChildOfChildOfSectionChildTwo)

    def test_same_object_different_instances(self):
        foo_obj = ChildOfChildOfSectionChildOne.objects.get(slug='child-of-child-of-section-child-one')
        foo_pk = foo_obj.pk

        all_models = [BaseContent, BaseSection, SectionChildOne,
                      ChildOfSectionChildOne, ChildOfChildOfSectionChildOne]
        for model in all_models:
            obj = model.objects.get(pk=foo_pk)
            self.assertEquals(obj.slug, foo_obj.slug)
            self.assertEquals(obj.name, foo_obj.name)
            self.assertEquals(obj.get_real_instance().__class__,
                              ChildOfChildOfSectionChildOne)

    def test_same_object_different_instances_abstract(self):
        foo_obj = ChildOfChildOfSectionChildTwo.objects.get(slug='child-of-child-of-section-child-two')
        foo_pk = foo_obj.pk

        all_models = [BaseContent, BaseSection, SectionChildTwo,
                      ChildOfSectionChildTwo, ChildOfChildOfSectionChildTwo]
        for model in all_models:
            obj = model.objects.get(pk=foo_pk)
            self.assertEquals(obj.slug, foo_obj.slug)
            self.assertEquals(obj.name, foo_obj.name)
            self.assertEquals(obj.get_real_instance().__class__,
                              ChildOfChildOfSectionChildTwo)

    def tearDown(self):
        BaseContent.objects.all().delete()  # we assume that the table is already created
