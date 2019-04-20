# Copyright 2019 - Kapacitor
#
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

from datetime import datetime
from oslo_config import cfg

from vitrage.common.constants import DatasourceOpts as DSOpts
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.datasources.kapacitor import KAPACITOR_DATASOURCE
from vitrage.datasources.kapacitor.driver import KapacitorDriver
from vitrage.datasources.kapacitor.properties \
    import KapacitorProperties as KProps
from vitrage.tests import base
from vitrage.tests.mocks import utils
from vitrage.tests.mocks import mock_driver


# noinspection PyProtectedMember
WARN_SEVERITY = 'warning'
WARNING_EVENT_TYPE = 'collectd.alarm.warning'
HOST = 'compute-1'


class TestKapacitorDriver(base.BaseTest):
    OPTS = [
        cfg.StrOpt(DSOpts.CONFIG_FILE,
                   help='Kapacitor configuration file',
                   default=utils.get_resources_dir()
                           + '/kapacitor/kapacitor.yaml'),
    ]
    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(TestKapacitorDriver, cls).setUpClass()
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.OPTS, group=KAPACITOR_DATASOURCE)

    # noinspection PyAttributeOutsideInit
    def setUp(self):
        super(TestKapacitorDriver, self).setUp()
        self.driver = KapacitorDriver(self.conf)

    def test_enrich_event_with_alarm_up(self):
        now = datetime.now().isoformat()

        event = self._enrich_event(now, HOST,
                                   WARN_SEVERITY,
                                   WARNING_EVENT_TYPE)

        self._assert_event_equal(event, WARNING_EVENT_TYPE,
                                 HOST, WARN_SEVERITY, now)

    def _enrich_event(self, time_now, hostname, severity, event_type):
        event = self._generate_event(time_now, hostname, severity)
        event = self.driver.enrich_event(event, event_type)
        return event

    @staticmethod
    def _generate_event(timestamp, hostname, severity):
        update_vals = {}
        if hostname:
            update_vals[KProps.HOST] = hostname
        if severity:
            update_vals[KProps.SEVERITY] = severity

        if timestamp:
            update_vals[KProps.TIMESTAMP] = timestamp

        generators = mock_driver.simple_doctor_alarm_generators(
            update_vals=update_vals)

        return mock_driver.generate_sequential_events_list(generators)[0]

    def _assert_event_equal(self,
                            event,
                            expected_event_type,
                            expected_hostname,
                            expected_severity,
                            expected_sample_date):
        self.assertIsNotNone(event, 'No event returned')
        self.assertEqual(expected_hostname, event[KProps.HOST])
        self.assertEqual(expected_severity, event[KProps.PRIORITY])
        self.assertEqual(expected_sample_date, event[KProps.TIMESTAMP])
        self.assertEqual(expected_event_type, event[DSProps.EVENT_TYPE])

    def _generate_event(self,k_resource_name='compute01',
                            description='high mem',
                            status='0',
                            value='0',
                            priority='1',
                            triggerid='0'):

        ID = 'id'
        RESOURCE_TYPE = 'resource_type'
        RESOURCE_NAME = 'resource_name'
        DETAILS = 'details'
        STATUS = 'status'
        HOST = 'host'
        PRIORITY = 'priority'
        TIME = 'time'
        MESSAGE = 'message'
        KAPACITOR_RESOURCE_NAME = 'kapacitor_resource_name'
        return {KProps.ZABBIX_RESOURCE_NAME: k_resource_name,
                KProps.DETAILS: description,
                KProps.STATUS: status,
                KProps.VALUE: value,
                KProps.PRIORITY: priority,
                KProps.RESOURCE_NAME: k_resource_name,
                }