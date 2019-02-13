## Hướng dẫn cài đặt vitrage:

Sau khi so sánh các phiên bản pike-queens, Em thấy sử dụng bản queen phù hợp hơn, do:
Bản vitrage pike gặp một số issue như:
- Darshboard giao tiếp với api keystone version_2. Sử dụng sẽ thấy lỗi "missing project id, project name,.." . Cách fix: sửa trong code
- Các template được đọc trực tiếp trong thư mục, cần r dịch vụ khi thêm template mới. <br/>
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
### Cài trên openstack
#### chuẩn bị cho keystone-endpoint, database:
- Tại keystone chạy các lệnh để tạo user, serivce, endpoint
```
openstack user create vitrage --password Welcome123 --domain=Default
openstack role add admin --user vitrage --project service
openstack role add admin --user vitrage --project admin
openstack service create rca --name vitrage --description="Root Cause Analysis Service"
openstack endpoint create --region RegionOne  metric public http://controller:8041
openstack endpoint create --region RegionOne  rca public http://controller:8999
openstack endpoint create --region RegionOne  vitrage internal http://controller:8999 
openstack endpoint create --region RegionOne  vitrage admin http://controller:8999 
```
- Tại mysql tạo vitrage database:
```
mysql -u root -p
CREATE DATABASE vitrage;
GRANT ALL PRIVILEGES ON vitrage.* TO 'vitrage'@'localhost' \
  IDENTIFIED BY 'Welcome123';
GRANT ALL PRIVILEGES ON vitrage.* TO 'vitrage'@'%' \
  IDENTIFIED BY 'Welcome123';
```


#### cài vitrage-core

- Cài các gói 
```
wget http://tarballs.openstack.org/vitrage/vitrage-stable-queens.tar.gz
tar xvzf vitrage-stable-queens.tar.gz
cd vitrage-2.3.1.dev3/
pip install -r requirements.txt
python setup.py install
```
- Tạo thư mục conf
```
cd vitrage-2.3.1.dev3/
cp -r etc/vitrage /etc/
mkdir /etc/vitrage/static_datasources
chmod 755 /etc/vitrage/static_datasources
mkdir /var/log/vitrage
```
- Tạo file conf /etc/vitrage/vitrage.conf nội dung :
```
[DEFAULT]
transport_url = rabbit://openstack:Welcome123@controller
log_dir = /var/log/vitrage
[datasources]
types = nova.host,nova.instance,nova.zone,static,aodh,cinder.volume,neutron.network,neutron.port,heat.stack,doctor
[database]
connection = = mysql+pymysql://vitrage:Welcome123@controller/vitrage

[keystone_authtoken]
auth_uri = http://controller:5000/v3
auth_version = v3
region_name = RegionOne
project_domain_name = Default
project_name = service
user_domain_name = Default
password = Welcome123
username = vitrage
auth_url = http://controller:35357/v3
auth_type = password

[service_credentials]
auth_url = http://controller:5000/v3
auth_version = v3
region_name = RegionOne
project_name = admin
password = Welcome123
project_domain_id = default
user_domain_id = default
username = admin
auth_type = password

[oslo_messaging_notifications]
driver = messagingv2
topics = notifications,vitrage_notifications
```
( sửa các phần authen cho phù hợp hệ thống cụ thể) 

#### cài vitrage-drashboard
- Cài các gói: 
```
wget http://tarballs.openstack.org/vitrage-dashboard/vitrage-dashboard-stable-queens.tar.gz
tar xvzf vitrage-dashboard-stable-queens.tar.gz
cd vitrage-dashboard-1.4.3.dev1/
pip install -r requirements.txt
python setup.py install
cp enabled/* /usr/share/openstack-dashboard/openstack_dashboard/local/enabled/
```
( gói /usr/share/openstack-dashboard có thể có địa chỉ khác biệt tùy hệ thống)
- compress horion
```
sudo python /usr/share/openstack-dashboard/manage.py compress
sudo service apache2 restart
```
#### cài vitrage-cli-client (python_vitrageclient)
```
pip install python_vitrageclient==2.1.0 
```
#### Thiết đặt cho các serivice khác 
vitrage lấy thông tin datasouce từ rabbitmq topic . thay đổi trong aodh.conf, nova.conf, neutron.conf, cinder.conf, heat.conf:
```
[oslo_messaging_notifications]
driver = messagingv2
topics = notifications,vitrage_notifications
```
restart các dịch vụ này
### Khởi chạy:
Tạo database:
```
vitrage-dbsync --conf...
```

Chạy các dịch vụ:
```
vitrage-collector 
vitrage-graph
vitrage-api
vitrage-notifier
```
### Một số lỗi khi cài đặt đã gặp:
Khi khởi tạo data, gặp lỗi báo:

```
DBError: (pymysql.err.InternalError) (1075, u'Incorrect table definition; there can be only one auto column and it must be defined as a key')
```
Nguyên nhân: kịch bản tạo database của vitrage lỗi. Transaction trong kịch bản này bị từ chối của storage engine
Khắc phục : sửa defaut storage engine từ InnoDB về MyISAM 

https://stackoverflow.com/questions/6479655/how-do-i-set-myisam-as-default-table-handler-in-mysql
