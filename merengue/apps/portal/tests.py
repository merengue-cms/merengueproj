# -*- coding: utf-8 -*-
import os.path
import unittest
import re

from random import randrange

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.db.models import get_model

from django.test import TestCase

from cmsutils.spidertests import BaseSpiderTests, OptimizedSpiderSuite

garbage = r'[ |\t|\n]*'
group_content_type = r'(?P<app_label>\w+).(?P<model>\w+)(\[0?:(?P<limit>\d+)\])?.(?P<field>\w+)'
group_range = r'\[%(g)s([a-z0-9]+)%(g)s\-?%(g)s([a-z0-9]*)%(g)s\]+' % {'g': garbage}
group_text_annoyed = r'annoyed\(\)'
group_text_random = r'random\(\)'

group = r'%(g)s{%(g)s%(content)s%(g)s}%(g)s' %{'g': garbage, 'content': '%s'}

content_type_re = re.compile(group % group_content_type)
range_re = re.compile(group % "(%(g)s%(r)s%(g)s)+" %{'g': garbage, 'r': group_range})
text_annoyed_re = re.compile(group % group_text_annoyed)
text_random_re = re.compile(group % group_text_random)

TEXT_ANNOYED = u"·%23$~%%26%2F¬()=?'¿¡^`[*+]\"'{Ç}-_.:,<>1QÑáÉ€"


class BaseDatabaseTestCase(TestCase):
    db_loaded = False

    def setUp(self):
        if not BaseDatabaseTestCase.db_loaded:
            call_command('load_production_db', interactive=False)
            user, created = User.objects.get_or_create(username='spider')
            if created:
                user.set_password("spider")
                user.is_staff = True
                user.is_superuser = True
                user.save()
            BaseDatabaseTestCase.db_loaded = True
            connection.connection.commit()


class SpiderTests(BaseDatabaseTestCase, BaseSpiderTests):

    urls_file = os.path.join(settings.BASEDIR, 'urls.ini')

    def _test_url(self, url, method='GET', data={}, login=None, maxqueries=None):
        limit = settings.LIMIT_URL_SPIDER_TEST
        urls = self._url_pattern_recursive(url)[:limit]
        data = self._data_pattern(data)
        for url_pattern in urls:
            BaseSpiderTests._test_url(self, url_pattern, method, data, login, maxqueries)

    def _data_pattern(self, data):
        if data:
            for key, value in data.items():
                match_annoyed = re.search(text_annoyed_re, value)
                if match_annoyed:
                    data[key] = self._get_random_text(TEXT_ANNOYED)
                else:
                    match_random = re.search(text_random_re, value)
                    if match_random:
                        data[key] = self._get_random_text()
        return data

    def _get_random_text(self, text="", number_characters=10):
        for i in range(number_characters):
            text+= chr(randrange(32, 127))
        return unicode(text)

    def _url_pattern_recursive(self, url, url_list=None):
        if url_list is None:
            url_list = []
        match_group = re.search(content_type_re, url)
        limit_settings = settings.LIMIT_URL_SPIDER_TEST
        if match_group:
            app_label = match_group.group('app_label')
            model_name = match_group.group('model')
            field = match_group.group('field')
            limit = match_group.groupdict().get('limit')
            query_set = get_model(app_label, model_name).objects.all().order_by('?')
            if limit is not None:
                query_set = query_set[:limit]
            elif limit_settings is not None:
                query_set = query_set[:limit_settings]
            for obj in query_set:
                start = max(0, match_group.start()-1)
                end = min(len(url), match_group.end()+1)
                self._url_pattern_aux(url, url_list, start, end, getattr(obj, field))
        else:
            match_range = re.search(range_re, url)
            if match_range:
                list_values = []
                start = max(0, match_range.start()-1)
                end = min(len(url), match_range.end()+1)
                url_range = url[start:end]
                while match_range:
                    len_range = len(match_range.groups()[0])
                    first_group = match_range.groups()[1]
                    if first_group.isdigit(): # i.e.: [3] or [2-5]
                        range_start = int(first_group)
                        range_end = int(match_range.groups()[2] or (range_start + 1))
                        list_values.extend(range(range_start, range_end))
                    else: # i.e. [foo]
                        list_values.append(first_group)
                    pos_start = len(url_range) - (len_range + 2)
                    url_range = "%s%s"%(url_range[:pos_start], url_range[-2:])
                    match_range = re.search(range_re, url_range)
                list_values = list_values
                for obj in list_values:
                    self._url_pattern_aux(url, url_list, start, end, obj)
            else:
                match_annoyed = re.search(text_annoyed_re, url)
                if match_annoyed:
                    start = max(0, match_annoyed.start())
                    end = min(len(url), match_annoyed.end()+1)
                    self._url_pattern_aux(url, url_list, start, end, self._get_random_text(TEXT_ANNOYED))
                else:
                    match_random = re.search(text_random_re, url)
                    if match_random:
                        start = max(0, match_random.start()-1)
                        end = min(len(url), match_random.end()+1)
                        self._url_pattern_aux(url, url_list, start, end, self._get_random_text())
                    else:
                        url_list.append(url)
        return url_list

    def _url_pattern_aux(self, url, url_list, start, end, field_value):
        url_new = "%s/%s/%s"%(url[:start], field_value, url[end:])
        return self._url_pattern_recursive(url_new, url_list)


def suite():
    return unittest.TestSuite((
            unittest.makeSuite(SpiderTests, suiteClass=OptimizedSpiderSuite),
           ))
