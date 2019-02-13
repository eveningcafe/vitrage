## Hướng dẫn cài đặt vitrage:

Sau khi so sánh các phiên bản pike-queens, Em thấy sử dụng bản queen phù hợp hơn, do:
Bản vitrage pike gặp một số issue như:
- Darshboard giao tiếp với api keystone version_2. Sử dụng sẽ thấy lỗi "missing project id, project name,.." . Cách fix: sửa trong code
- Các template được đọc trực tiếp trong thư mục, cần reset dịch vụ khi thêm template mới. <br/>
Sang bản queen , template được lưu vào mysql . Database bắt đầu mới dược vitrage sử dụng tại bản queens.
- Hỗ trợ aodh chưa hoàn chỉnh. Sang bản queen mới có thể nhận  alarm dạng "Aodh Gnocchi threshold alarm"

Thử nghiệm bản queen em thấy cũng giao tiếp tốt với các service openstack khác (nova, neutron,..) verion pike

Vậy dưới đây là hướng dẫn cài đặt cho vitrage version queens

### Cài trên devstack:

- Tuân theo các hướng dẫn cơ bản tại https://docs.openstack.org/devstack/latest/
- file local.conf:
```
[[local|localrc]]
GIT_BASE=http://github.com
HOST_IP=192.168.2.54
ADMIN_PASSWORD=secret
DATABASE_PASSWORD=$ADMIN_PASSWORD
RABBIT_PASSWORD=$ADMIN_PASSWORD
SERVICE_PASSWORD=$ADMIN_PASSWORD
MULTI_HOST=True
enable_plugin vitrage https://git.openstack.org/openstack/vitrage stable/queens
enable_plugin vitrage-dashboard https://git.openstack.org/openstack/vitrage-dashboard stable/queens
enable_plugin heat https://git.openstack.org/openstack/heat stable/queens
enable_plugin ceilometer https://git.openstack.org/openstack/ceilometer stable/queens
enable_plugin aodh https://git.openstack.org/openstack/aodh stable/queens
[[post-config|$NOVA_CONF]]
[DEFAULT]
notification_topics = notifications,vitrage_notifications
notification_driver=messagingv2

[notifications]
versioned_notifications_topics = versioned_notifications,vitrage_notifications
notification_driver = messagingv2

[[post-config|$NEUTRON_CONF]]
[DEFAULT]
notification_topics = notifications,vitrage_notifications
notification_driver=messagingv2

[[post-config|$CINDER_CONF]]
[DEFAULT]
notification_topics = notifications,vitrage_notifications
notification_driver=messagingv2

[[post-config|$HEAT_CONF]]
[DEFAULT]
notification_topics = notifications,vitrage_notifications
notification_driver=messagingv2

[[post-config|$AODH_CONF]]
[oslo_messaging_notifications]
driver = messagingv2
topics = notifications,vitrage_notifications
```
