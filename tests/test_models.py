from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.utils import timezone

from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning.test_utils.factories import (
    AnswerFactory,
    PollContentWithVersionFactory,
    PollVersionFactory,
)
from djangocms_versioning.test_utils.polls.models import (
    Answer,
    Poll,
    PollContent,
    PollVersion,
    VersionWithoutGrouperField,
)


class ModelsVersioningTestCase(CMSTestCase):

    def setUp(self):
        self.initial_version = PollVersionFactory()
        AnswerFactory.create_batch(
            2, poll_content=self.initial_version.content)

    def test_content_object_gets_duplicated(self):
        new_version = self.initial_version.copy()
        self.assertEqual(
            self.initial_version.content.text,
            new_version.content.text,
        )
        self.assertEqual(
            self.initial_version.content.language,
            new_version.content.language,
        )
        self.assertNotEqual(
            self.initial_version.content_id,
            new_version.content_id,
        )

    def test_answers_get_duplicated(self):
        new_version = self.initial_version.copy()
        self.assertEqual(
            list(self.initial_version.content.answer_set.values_list('text')),
            list(new_version.content.answer_set.values_list('text')),
        )
        self.assertNotEqual(
            list(self.initial_version.content.answer_set.values_list('pk')),
            list(new_version.content.answer_set.values_list('pk')),
        )

    def test_distinct_groupers(self):
        self.initial_version.copy()
        poll2_version = PollVersionFactory()
        poll2_version.copy()
        poll2_version.copy()

        self.assertEqual(PollVersion.objects.distinct_groupers().count(), 2)

    def test_for_grouper(self):
        self.initial_version.copy()
        poll2_version = PollVersionFactory()
        poll2_version.copy()
        poll2_version.copy()

        qs = PollVersion.objects.for_grouper(self.initial_version.content.poll)
        self.assertEqual(qs.count(), 2)

    def test_for_grouper_extra_filters(self):
        version2 = self.initial_version.copy()
        version2.content.language = 'de'
        version2.content.save()
        poll2_version = PollVersionFactory()
        poll2_version.copy()
        poll2_version.copy()

        qs = PollVersion.objects.for_grouper(
            self.initial_version.content.poll,
            Q(content__language='en'),
        )
        self.assertEqual(qs.count(), 1)

    def test_runtime_error_raised_without_grouper_field_override(self):
        version_without_grouper = VersionWithoutGrouperField()

        with self.assertRaises(ImproperlyConfigured):
            version_without_grouper.grouper_field
