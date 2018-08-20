from django.test import RequestFactory

from cms.test_utils.testcases import CMSTestCase
from cms.toolbar.toolbar import CMSToolbar

from djangocms_versioning import constants
from djangocms_versioning.cms_toolbars import VersioningToolbar
from djangocms_versioning.test_utils.factories import (
    PollVersionFactory,
    UserFactory,
)
from djangocms_versioning.test_utils.polls.cms_config import PollsCMSConfig


class VersioningToolbarTestCase(CMSTestCase):

    def _get_toolbar(self, content_obj, **kwargs):
        """Helper method to set up the toolbar
        """
        request = RequestFactory().get('/')
        request.user = UserFactory()
        request.session = {}
        cms_toolbar = CMSToolbar(request)
        toolbar = VersioningToolbar(
            request, toolbar=cms_toolbar, is_current_app=True, app_path='/')
        toolbar.toolbar.obj = content_obj
        if kwargs.get('edit_mode', False):
            toolbar.toolbar.edit_mode_active = True
            toolbar.toolbar.content_mode_active = False
            toolbar.toolbar.structure_mode_active = False
        elif kwargs.get('preview_mode', False):
            toolbar.toolbar.edit_mode_active = False
            toolbar.toolbar.content_mode_active = True
            toolbar.toolbar.structure_mode_active = False
        elif kwargs.get('structure_mode', False):
            toolbar.toolbar.edit_mode_active = False
            toolbar.toolbar.content_mode_active = False
            toolbar.toolbar.structure_mode_active = True
        return toolbar

    def _get_publish_url(self, version):
        """Helper method to return the expected publish url
        """
        versionable = PollsCMSConfig.versioning[0]
        admin_url = self.get_admin_url(
            versionable.version_model_proxy, 'publish', version.pk)
        return admin_url

    def _get_edit_url(self, version):
        """Helper method to return the expected edit redirect url
        """
        versionable = PollsCMSConfig.versioning[0]
        admin_url = self.get_admin_url(
            versionable.version_model_proxy, 'edit_redirect', version.pk)
        return admin_url

    def test_publish_in_toolbar_in_edit_mode(self):
        version = PollVersionFactory()
        toolbar = self._get_toolbar(version.content, edit_mode=True)

        toolbar.post_template_populate()

        publish_button = toolbar.toolbar.get_right_items()[0].buttons[0]
        self.assertEqual(publish_button.name, 'Publish')
        self.assertEqual(publish_button.url, self._get_publish_url(version))
        self.assertFalse(publish_button.disabled)
        self.assertListEqual(publish_button.extra_classes, ['cms-btn-action'])

    def test_publish_not_in_toolbar_in_preview_mode(self):
        version = PollVersionFactory()
        toolbar = self._get_toolbar(version.content, preview_mode=True)

        toolbar.post_template_populate()

        buttons = toolbar.toolbar.get_right_items()[0].buttons
        self.assertListEqual(
            [b for b in buttons if b.name == 'Publish'], [])

    def test_publish_not_in_toolbar_in_structure_mode(self):
        version = PollVersionFactory()
        toolbar = self._get_toolbar(version.content, structure_mode=True)

        toolbar.post_template_populate()

        buttons = toolbar.toolbar.get_right_items()
        self.assertListEqual(buttons, [])

    def test_dont_add_publish_for_models_not_registered_with_versioning(self):
        # User objects are not registered with versioning, so attempting
        # to populate a user toolbar should not attempt to add a publish
        # button
        toolbar = self._get_toolbar(UserFactory(), edit_mode=True)

        toolbar.post_template_populate()

        buttons = toolbar.toolbar.get_right_items()
        self.assertListEqual(buttons, [])

    def test_edit_in_toolbar_in_preview_mode(self):
        version = PollVersionFactory()
        toolbar = self._get_toolbar(version.content, preview_mode=True)

        toolbar.post_template_populate()

        edit_button = toolbar.toolbar.get_right_items()[0].buttons[0]
        self.assertEqual(edit_button.name, 'Edit')
        self.assertEqual(edit_button.url, self._get_edit_url(version))
        self.assertFalse(edit_button.disabled)
        self.assertListEqual(edit_button.extra_classes, ['cms-btn-action'])

    def test_edit_not_in_toolbar_in_edit_mode(self):
        version = PollVersionFactory()
        toolbar = self._get_toolbar(version.content, edit_mode=True)

        toolbar.post_template_populate()

        buttons = toolbar.toolbar.get_right_items()[0].buttons
        self.assertListEqual(
            [b for b in buttons if b.name == 'Edit'], [])

    def test_edit_not_in_toolbar_in_structure_mode(self):
        version = PollVersionFactory()
        toolbar = self._get_toolbar(version.content, structure_mode=True)

        toolbar.post_template_populate()

        buttons = toolbar.toolbar.get_right_items()
        self.assertListEqual(buttons, [])

    def test_dont_add_edit_for_models_not_registered_with_versioning(self):
        # User objects are not registered with versioning, so attempting
        # to populate a user toolbar should not attempt to add a edit
        # button
        toolbar = self._get_toolbar(UserFactory(), preview_mode=True)

        toolbar.post_template_populate()

        buttons = toolbar.toolbar.get_right_items()
        self.assertListEqual(buttons, [])
