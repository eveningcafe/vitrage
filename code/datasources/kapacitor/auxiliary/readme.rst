Kapacitor-Vitrage
=================

Kapacitor will send alert to vitrage by using [ exec-handle ], send to messeage queue topic of vitrage.
https://docs.influxdata.com/kapacitor/v1.5/working/alerts/


Installation
------------

Copy the 'kapacitor_vitrage.py' script into the Kapacitor servers.

.. code-block:: bash

  $ cp kapacitor_vitrage.py /etc/kapacitor/kapacitor_vitrage.py
  $ chmod 755 /etc/kapacitor/kapacitor_vitrage.py


Configuration
-------------



1. Define topic , which use for alert publish to. Create file ``foward_to_vitrage.yaml``:


      | topic: foward_to_vitrage
      | id: foward_to_vitrage
      | kind: exec
      | options:
      | prog: '/usr/bin/python'
      | args: ['/etc/kapacitor/kapacitor_vitrage.py','rabbit://<rabbit_user>:<rabbit_pass>@controller']

 **Note:** rabbit://<rabbit_user>:<rabbit_pass>@controller is  Vitrage message bus url,  ``rabbit_user:rabbit_pass`` for devstack rabbitmq is ``stackrabbit/secret``

Run command to define topic

.. code-block:: bash

$ kapacitor define-topic-handler ./foward_to_vitrage.yaml


2. Asssign your Task to topic, in Tick script define that alert, add in "alert()" step:

      | ...
      | |alert()
      |  ...
      |  .topic('foward_to_vitrage')

In case your Task aready in topic and you don't want to add another, you only need to do: append 'exec handler' to TICK scipt which define it.
      
      | ...
      | |alert()
      |  ...
      |  .exec('/usr/bin/python', '/etc/kapacitor/kapacitor_vitrage.py', 'rabbit://<rabbit_user>:<rabbit_pass>@controller')

Run command define your task:

.. code::

   $ kapacitor define <task_name> -tick <tick_script>


Vitrage configuration:

1. Add kapacitor to list of datasources in ``/etc/vitrage/vitrage.conf``

.. code::

    [datasources]
    types = kapacitor,zabbix,nova.host,nova.instance,nova.zone,static_physical,aodh,cinder.volume,neutron.network,neutron.port,heat.stack

2. Add section to ``/etc/vitrage/vitrage.conf``

.. code::

    [kapacitor]
    config_file = /etc/vitrage/kapacitor_conf.yaml

3. Create ``/etc/vitrage/kapacitor_conf.yaml`` with this content

.. code ::

    kapacitor:
    - kapacitor_host: hostname of host is raised alert by kapacitor
      type: nova.host
      name: resouce name 

**Note** if type is nova.instance, you may replace ``name: resouce name`` by ''name: id of instance'')

4. Restart vitrage service in devstack/openstack

DONE
----

