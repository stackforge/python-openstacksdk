# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_volume
----------------------------------

Functional tests for `shade` block storage methods.
"""
import testtools
from shade.exc import OpenStackCloudException
from shade.tests.functional import base


class TestVolumeType(base.BaseFunctionalTestCase):

    def _assert_project(self, volume_name_or_id, project_id, allowed=True):
        acls = self.operator_cloud.get_volume_type_access(volume_name_or_id)
        allowed_projects = [x.get('project_id') for x in acls]
        self.assertEqual(allowed, project_id in allowed_projects)

    def setUp(self):
        super(TestVolumeType, self).setUp()
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        self.operator_cloud.cinder_client.volume_types.create(
            'test-volume-type', is_public=False)

    def tearDown(self):
        ret = self.operator_cloud.get_volume_type('test-volume-type')
        if ret.get('id'):
            self.operator_cloud.cinder_client.volume_types.delete(ret.id)
        super(TestVolumeType, self).tearDown()

    def test_list_volume_types(self):
        volume_types = self.operator_cloud.list_volume_types()
        self.assertTrue(volume_types)
        self.assertTrue(any(
            x for x in volume_types if x.name == 'test-volume-type'))

    def test_add_remove_volume_type_access(self):
        volume_type = self.operator_cloud.get_volume_type('test-volume-type')
        self.assertEqual('test-volume-type', volume_type.name)

        self.operator_cloud.add_volume_type_access(
            'test-volume-type',
            self.operator_cloud.current_project_id)
        self._assert_project(
            'test-volume-type', self.operator_cloud.current_project_id,
            allowed=True)

        self.operator_cloud.remove_volume_type_access(
            'test-volume-type',
            self.operator_cloud.current_project_id)
        self._assert_project(
            'test-volume-type', self.operator_cloud.current_project_id,
            allowed=False)

    def test_add_volume_type_access_missing_project(self):
        # Project id is not valitaded and it may not exist.
        self.operator_cloud.add_volume_type_access(
            'test-volume-type',
            '00000000000000000000000000000000')

        self.operator_cloud.remove_volume_type_access(
            'test-volume-type',
            '00000000000000000000000000000000')

    def test_add_volume_type_access_missing_volume(self):
        with testtools.ExpectedException(
                OpenStackCloudException,
                "VolumeType not found.*"
        ):
            self.operator_cloud.add_volume_type_access(
                'MISSING_VOLUME_TYPE',
                self.operator_cloud.current_project_id)

    def test_remove_volume_type_access_missing_volume(self):
        with testtools.ExpectedException(
                OpenStackCloudException,
                "VolumeType not found.*"
        ):
            self.operator_cloud.remove_volume_type_access(
                'MISSING_VOLUME_TYPE',
                self.operator_cloud.current_project_id)

    def test_add_volume_type_access_bad_project(self):
        with testtools.ExpectedException(
                OpenStackCloudException,
                "Unable to authorize.*"
        ):
            self.operator_cloud.add_volume_type_access(
                'test-volume-type',
                'BAD_PROJECT_ID')

    def test_remove_volume_type_access_missing_project(self):
        with testtools.ExpectedException(
                OpenStackCloudException,
                "Unable to revoke.*"
        ):
            self.operator_cloud.remove_volume_type_access(
                'test-volume-type',
                '00000000000000000000000000000000')
