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
# mypy: disable-error-code="method-assign"

from openstack.network.v2 import subnet_pool as _subnet_pool
from openstack.tests.functional.network.v2 import common


class TestSubnetPool(common.TestTagNeutron):
    SUBNET_POOL_ID = None
    MINIMUM_PREFIX_LENGTH = 8
    DEFAULT_PREFIX_LENGTH = 24
    MAXIMUM_PREFIX_LENGTH = 32
    DEFAULT_QUOTA = 24
    IS_SHARED = False
    IP_VERSION = 4
    PREFIXES = ["10.100.0.0/24", "10.101.0.0/24"]

    def setUp(self):
        super().setUp()
        self.SUBNET_POOL_NAME = self.getUniqueString()
        self.SUBNET_POOL_NAME_UPDATED = self.getUniqueString()
        subnet_pool = self.user_cloud.network.create_subnet_pool(
            name=self.SUBNET_POOL_NAME,
            min_prefixlen=self.MINIMUM_PREFIX_LENGTH,
            default_prefixlen=self.DEFAULT_PREFIX_LENGTH,
            max_prefixlen=self.MAXIMUM_PREFIX_LENGTH,
            default_quota=self.DEFAULT_QUOTA,
            shared=self.IS_SHARED,
            prefixes=self.PREFIXES,
        )
        assert isinstance(subnet_pool, _subnet_pool.SubnetPool)
        self.assertEqual(self.SUBNET_POOL_NAME, subnet_pool.name)
        self.SUBNET_POOL_ID = self.ID = subnet_pool.id
        self.get_command = self.user_cloud.network.get_subnet_pool

    def tearDown(self):
        sot = self.user_cloud.network.delete_subnet_pool(self.SUBNET_POOL_ID)
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_subnet_pool(self.SUBNET_POOL_NAME)
        self.assertEqual(self.SUBNET_POOL_ID, sot.id)

    def test_get(self):
        sot = self.user_cloud.network.get_subnet_pool(self.SUBNET_POOL_ID)
        self.assertEqual(self.SUBNET_POOL_NAME, sot.name)
        self.assertEqual(self.MINIMUM_PREFIX_LENGTH, sot.minimum_prefix_length)
        self.assertEqual(self.DEFAULT_PREFIX_LENGTH, sot.default_prefix_length)
        self.assertEqual(self.MAXIMUM_PREFIX_LENGTH, sot.maximum_prefix_length)
        self.assertEqual(self.DEFAULT_QUOTA, sot.default_quota)
        self.assertEqual(self.IS_SHARED, sot.is_shared)
        self.assertEqual(self.IP_VERSION, sot.ip_version)
        self.assertEqual(self.PREFIXES, sot.prefixes)

    def test_list(self):
        names = [o.name for o in self.user_cloud.network.subnet_pools()]
        self.assertIn(self.SUBNET_POOL_NAME, names)

    def test_update(self):
        sot = self.user_cloud.network.update_subnet_pool(
            self.SUBNET_POOL_ID, name=self.SUBNET_POOL_NAME_UPDATED
        )
        self.assertEqual(self.SUBNET_POOL_NAME_UPDATED, sot.name)
