from resource_management import *
import commands

config = Script.get_config()

# some doris common config
version = '3.1.0.0-78' # your hdp service version
doris_filename = 'doris-0.14.0-release' # your doris package name

# download path
download_url = commands.getoutput(
    'cat /etc/yum.repos.d/ambari-1.repo | grep "baseurl" | head -1 | awk -F \'=\' \'{print $2"doris/' + doris_filename + '.tar.gz"}\''
)

# get system local priority_networks
doris_fe_priority_networks = commands.getoutput(
    'ip a | grep `hostname -i` | awk -F \' \' \'{print $2}\''
)

# get some hostname
doris_fe_hostname = default("/clusterHostInfo/doris_fe_hosts", [])
# doris_fe_hostname.sort()
doris_be_hostname = default("/clusterHostInfo/doris_be_hosts", [])
doris_fe_observer_hostname = default("/clusterHostInfo/fe_observer_hosts", [])

Logger.info(format("doris install hosts is : "
                   "doris_fe_hostname={doris_fe_hostname} ;" 
                   "doris_be_hostname={doris_be_hostname} ;"
                   "doris_fe_observer_hostname={doris_fe_observer_hostname}"))

# user and group
default_user = 'root'
default_group = 'root'

# doris install path
stack_root = Script.get_stack_root()
doris_install_base_dir = format('{stack_root}/{version}')
doris_install_dir = doris_install_base_dir + '/doris'
doris_dir = doris_install_dir + '/' + doris_filename

# configuration path
doris_fe_conf_dir = doris_dir + '/fe/conf'
doris_be_conf_dir = doris_dir + '/be/conf'

# bin path
doris_fe_bin_path = doris_dir + '/fe/bin'
doris_be_bin_path = doris_dir + '/be/bin'

# pid file
doris_fe_pid_file = doris_fe_bin_path + '/fe.pid'
doris_be_pid_file = doris_be_bin_path + '/be.pid'


# system limits config
limits_conf_dir = "/etc/security/limits.d"
doris_user_nofile_limit = default("/configurations/system/doris_user_nofile_limit", "128000")
doris_user_nproc_limit = default("/configurations/system/doris_user_nproc_limit", "65536")

# get fe.xml values to fe.conf
doris_fe_java_opts = config['configurations']['fe']['doris.fe.java_opts']
doris_fe_sys_log_level = config['configurations']['fe']['doris.fe.sys_log_level']
doris_fe_meta_dir = config['configurations']['fe']['doris.fe.meta_dir']
doris_fe_sys_log_dir = config['configurations']['fe']['doris.fe.sys_log_dir']
doris_fe_http_port = config['configurations']['fe']['doris.fe.http_port']
doris_fe_rpc_port = config['configurations']['fe']['doris.fe.rpc_port']
doris_fe_query_port = config['configurations']['fe']['doris.fe.query_port']
doris_fe_edit_log_port = config['configurations']['fe']['doris.fe.edit_log_port']
doris_fe_mysql_service_nio_enabled = config['configurations']['fe']['doris.fe.mysql_service_nio_enabled']
doris_fe_root_password = config['configurations']['fe']['doris.fe.root.password']
# get fe.conf values
doris_fe_conf_file = config['configurations']['fe']['content']

# get be.xml values to be.conf
doris_be_log_dir = config['configurations']['be']['doris.be.log_dir']
doris_be_sys_log_level = config['configurations']['be']['doris.be.sys_log_level']
doris_be_be_port = config['configurations']['be']['doris.be.be_port']
doris_be_rpc_port = config['configurations']['be']['doris.be.rpc_port']
doris_be_webserver_port = config['configurations']['be']['doris.be.webserver_port']
doris_be_brpc_port = config['configurations']['be']['doris.be.brpc_port']
doris_be_heartbeat_service_port = config['configurations']['be']['doris.be.heartbeat_service_port']
# be use fe priority_networks get function
doris_be_priority_networks = doris_fe_priority_networks
doris_be_storage_root_path = config['configurations']['be']['doris.be.storage_root_path']
# get be.conf values
doris_be_conf_file = config['configurations']['be']['content']


