## Ambari-Doris-Service
An Ambari Stack for Doris.
Ambari stack for easily installing and managing Doris on HDP cluster

## 1. introduce
This ambari doris stack have 3 roles, DORIS_FE\FE_Observer\DORIS_BE,
The doris package name is doris-0.14.0-release.tar.gz and tree path below:
```text
doris-0.14.0-release
├── be
│ ├── bin
│ │ ├── start_be.sh
│ │ └── stop_be.sh
│ ├── conf
│ │ ├── be.conf
│ │ └── odbcinst.ini
│ ├── lib
│ │ ├── meta_tool
│ │ └── palo_be
│ └── www
│     ├── ...
├── fe
│ ├── bin
│ │ ├── start_fe.sh
│ │ └── stop_fe.sh
│ ├── conf
│ │ └── fe.conf
│ ├── lib
│ │ ├── ...
│ ├── spark-dpp
│ │ └── spark-dpp-1.0.0-jar-with-dependencies.jar
│ └── webroot
│     └── static
│         ├── ...
├── hdfs_broker
│ ├── bin
│ │ ├── start_broker.sh
│ │ └── stop_broker.sh
│ ├── conf
│ │ ├── apache_hdfs_broker.conf
│ │ ├── hdfs-site.xml
│ │ └── log4j.properties
│ └── lib
│     ├── ...
│     └── ...
└── udf
    ├── include
    │ ├── uda_test_harness.h
    │ └── udf.h
    └── lib
        └── libDorisUdf.a
```
## 2.notice
```
Do not install DORIS_FE and FE_Observer in the same node.
```

## 3.install
1. Change project dir name.
```
mv Ambari-Doris-Service Doris
```
2. edit package/scripts/params.py
```
change the version and doris_filename as your true value.
 eg:
 version = '3.1.0.0-78'   
 doris_filename = 'doris-0.14.0-release'
```
4. check your yum repos file. change it as your own download_url, before install check the download_url can used.
```
download_url = commands.getoutput(
   'cat /etc/yum.repos.d/ambari-1.repo | grep "baseurl" | head -1 | awk -F \'=\' \'{print $2"doris/' + doris_filename + '.tar.gz"}\''
  )
```
5. put Doris dir to ambari-server node /var/lib/ambari-server/resources/common-services
```
ambari-server restart //in manager node
ambari-agent restart //in all node
```
6. installing.
```
Do not install DORIS_FE and FE_Observer in the same node.
input doris root password at doris.fe.root.password property.
```
7. After install succeed
```
handle the Doris service operations 'ADD_FE_FOLLOWER' or 'ADD_FE_OBSERVER' or 'ADD_BACKEND'.
```
## 4. TODO
```
1. Add hdfs_broker 
2. Some other TODO list
3. Bugs
```
## 5.Links
```
How-To Define Stacks and Services
https://cwiki.apache.org/confluence/display/AMBARI/How-To+Define+Stacks+and+Services
```
## Welcome to contribute it together.
