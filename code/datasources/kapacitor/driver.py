# Copyright 2019 - Viettel
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

from collections import namedtuple
from oslo_log import log

from vitrage.common.constants import DatasourceAction
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import DatasourceOpts as DSOpts
from vitrage.datasources.alarm_driver_base import AlarmDriverBase
from vitrage.datasources.kapacitor.properties import KapacitorProperties \
    as KProps
from vitrage.datasources.kapacitor.properties import KapacitorState
from vitrage.datasources.kapacitor import KAPACITOR_DATASOURCE
from vitrage.utils import file as file_utils

LOG = log.getLogger(__name__)


class KapacitorDriver(AlarmDriverBase):
    ServiceKey = namedtuple('ServiceKey', ['hostname', 'alarmid'])
    conf_map = None

    def __init__(self, conf):
        super(KapacitorDriver, self).__init__()
        self.cfg = conf
        if not KapacitorDriver.conf_map:
            KapacitorDriver.conf_map =\
                KapacitorDriver._configuration_mapping(conf)
        self._client = None

    @staticmethod
    def get_event_types():
        return ['kapacitor.alarm.ok',
                'kapacitor.alarm.info',
                'kapacitor.alarm.warning',
                'kapacitor.alarm.critical']

    def _vitrage_type(self):
        return KAPACITOR_DATASOURCE

    def _alarm_key(self, alarm):
        return self.ServiceKey(hostname=alarm[KProps.RESOURCE_NAME],
                               alarmid=alarm[KProps.ALARM_ID])

    @staticmethod
    def _configuration_mapping(conf):
        try:
            kapacitor_config_file = conf.kapacitor[DSOpts.CONFIG_FILE]
            kapacitor_config = file_utils.load_yaml_file(kapacitor_config_file)
            kapacitor_config_elements = kapacitor_config[KAPACITOR_DATASOURCE]

            mappings = {}
            for element_config in kapacitor_config_elements:
                mappings[element_config['kapacitor_host']] = {
                    KProps.RESOURCE_TYPE: element_config['type'],
                    KProps.RESOURCE_NAME: element_config['name']
                }

            return mappings
        except Exception as e:
            LOG.exception('failed in init %s ', e)
            return {}

    def _enrich_alarms(self, alarms):
        """Enrich kapacitor alarm using kapacitor configuration file

        converting Kapacitor host name to Vitrage resource type and name

        :param alarms: Kapacitor alarm
        :return: enriched alarm
        """

        for alarm in alarms:
            kapacitor_host = alarm[KProps.KAPACITOR_RESOURCE_NAME]
            vitrage_host = KapacitorDriver.conf_map[kapacitor_host]
            alarm[KProps.RESOURCE_TYPE] = vitrage_host[KProps.RESOURCE_TYPE]
            alarm[KProps.RESOURCE_NAME] = vitrage_host[KProps.RESOURCE_NAME]

    def enrich_event(self, event, event_type):
        event[DSProps.EVENT_TYPE] = event_type

        if KapacitorDriver.conf_map:
            kapacitor_host = event[KProps.HOST]
            event[KProps.KAPACITOR_RESOURCE_NAME] = kapacitor_host
            v_resource = KapacitorDriver.conf_map[kapacitor_host]
            event[KProps.RESOURCE_NAME] = v_resource[KProps.RESOURCE_NAME]
            event[KProps.RESOURCE_TYPE] = v_resource[KProps.RESOURCE_TYPE]
        return KapacitorDriver.make_pickleable([event], KAPACITOR_DATASOURCE,
                                               DatasourceAction.UPDATE)[0]

    def _is_erroneous(self, alarm):
        return alarm and alarm[KProps.PRIORITY] != KapacitorState.OK

    def _status_changed(self, new_alarm, old_alarm):
        return new_alarm and old_alarm and \
            not new_alarm[KProps.PRIORITY] == old_alarm[KProps.PRIORITY]

    def _is_valid(self, alarm):
        return alarm[KProps.RESOURCE_TYPE] is not None and \
            alarm[KProps.RESOURCE_NAME] is not None

    def _get_alarms(self):
        """Query all alarm and send to vitrage
        
        not implement yet
        """
        return []
