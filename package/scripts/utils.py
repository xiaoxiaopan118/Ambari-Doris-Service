from resource_management import *
from resource_management.core.resources.system import Execute, Directory, File, Link
import os
import socket
import time


def install():
    import params
    if not is_service_installed(params):
        # download doris tar.gz
        cmd = format("mkdir -p {doris_install_dir}; cd {doris_install_dir}; wget {download_url} ")
        Execute(cmd, user=params.default_user)

        # install doris
        cmd = format("cd {doris_install_dir}; tar -xf {doris_filename}.tar.gz")
        Execute(cmd, user=params.default_user)

        # remove doris installation file
        cmd = format("cd {doris_install_dir}; rm -rf {doris_filename}.tar.gz")
        Execute(cmd, user=params.default_user)


def is_service_installed(params):
    """
    Judge if service installed
    :param params: params.py
    :return: installed
    """
    install_dirs = params.doris_dir
    installed = False
    if os.path.isdir(install_dirs):
        installed = True
        Logger.info(format("Service already installed."))
    return installed


def split_be_storage_path(params):
    """
    split_be_storage_path
    :return:
    """
    split_path = params.doris_be_storage_root_path.split(';')
    Logger.info("Doris BE storage path is {0}.".format(split_path))
    if len(split_path) >= 1:
        for tmp_path in split_path:
            path = tmp_path.split('.')
            if None != path:
                Logger.info("Starting mkdir Doris BE storage path, The path is {0}.".format(path))
                Directory(path,
                          create_parents = True,
                          owner=params.default_user,
                          group=params.default_group)


def change_root_passowrd(params):
    """
    change root passowrd
    # TODO the function is not appropriate
    :return:
    """
    doris_fe_hostname = params.doris_fe_hostname[0]
    doris_root_password = params.doris_fe_root_password
    doris_fe_query_port = params.doris_fe_query_port
    doris_be_heartbeat_service_port = params.doris_be_heartbeat_service_port

    cmd_no_password = format("mysql -uroot -h {doris_fe_hostname} -P {doris_fe_query_port} "
                 "-e \"SET PASSWORD FOR \'root\' = PASSWORD(\'{doris_root_password}\') \" ")
    cmd_has_password = format("mysql -uroot -p{doris_root_password} -h {doris_fe_hostname} -P {doris_fe_query_port} "
                 "-e \"SET PASSWORD FOR \'root\' = PASSWORD(\'{doris_root_password}\') \" ")
    try:
        Logger.info("Add Doris Server password, commonds is {0}.".format(cmd_no_password))
        Execute(cmd_no_password, user=params.default_user, logoutput=True, tries=10, try_sleep=3)
    except:
        Logger.info("Changed Doris Server password, commonds is {0}.".format(cmd_has_password))
        Execute(cmd_has_password, user=params.default_user, logoutput=True, ignore_failures=True, tries=10, try_sleep=3)


def add_doris_backend(params):
    """
    add_doris_backend
    # TODO the function is not appropriate
    :return:
    """
    doris_fe_hostname = params.doris_fe_hostname[0]
    doris_root_password = params.doris_fe_root_password
    doris_fe_query_port = params.doris_fe_query_port
    doris_be_heartbeat_service_port = params.doris_be_heartbeat_service_port
    if None != params.doris_be_hostname:
        for be_host in params.doris_be_hostname:
            cmd = format("mysql -uroot -p{doris_root_password} -h {doris_fe_hostname} -P {doris_fe_query_port} "
                         "-e \"ALTER SYSTEM ADD BACKEND \'{be_host}:{doris_be_heartbeat_service_port}\' \"")
            Logger.info("Starting Doris FE Server, commonds is {0}.".format(cmd))
            Execute(cmd, user=params.default_user, logoutput=True, tries=5, try_sleep=5)


def add_frontend(fe_role, params):
    """
    add_frontend
    :return:
    """

    # TODO the function is not appropriate
    # Before add backend change root password, This is not appropriate.
    change_root_passowrd(params)

    # add doris fe
    doris_fe_hostname = params.doris_fe_hostname[0]
    doris_fe_observer_hostname = params.doris_fe_observer_hostname
    doris_root_password = params.doris_fe_root_password
    doris_fe_query_port = params.doris_fe_query_port
    doris_fe_edit_log_port = params.doris_fe_edit_log_port
    if (len(params.doris_fe_hostname) >= 1) and (fe_role == 'FOLLOWER'):
        for fe_host in params.doris_fe_hostname:
            if fe_host != doris_fe_hostname:
                cmd = format("mysql -uroot -p{doris_root_password} -h {doris_fe_hostname} -P {doris_fe_query_port} "
                             "-e \"ALTER SYSTEM ADD {fe_role} \'{fe_host}:{doris_fe_edit_log_port}\' \"")
                Logger.info("Adding Doris FE Follower Server, commonds is {0}.".format(cmd))
                Execute(cmd, user=params.default_user, logoutput=True, tries=5, try_sleep=5)
    if (len(params.doris_fe_observer_hostname) >= 1) and (fe_role == 'OBSERVER'):
        for fe_observer in params.doris_fe_observer_hostname:
            cmd = format("mysql -uroot -p{doris_root_password} -h {doris_fe_hostname} -P {doris_fe_query_port} "
                         "-e \"ALTER SYSTEM ADD {fe_role} \'{fe_observer}:{doris_fe_edit_log_port}\' \"")
            Logger.info("Adding Doris FE Follower Server, commonds is {0}.".format(cmd))
            Execute(cmd, user=params.default_user, logoutput=True, tries=5, try_sleep=5)


def fe_init_start(fe_role,params):
    """
    the first start follower and observer fe
    :return:
    """
    cmd = None
    doris_fe_hostname = params.doris_fe_hostname[0]
    doris_fe_edit_log_port = params.doris_fe_edit_log_port

    # stop it first begin start
    # if os.path.exists(params.doris_fe_pid_file):
    #     self.stop()

    # if doris_fe is follower and observer,add them
    if (fe_role == 'FOLLOWER') or (fe_role == 'OBSERVER'):
        cmd = format("cd {doris_fe_bin_path};"
                     "sh start_fe.sh --helper {doris_fe_hostname}:{doris_fe_edit_log_port} --daemon")
    else:
        cmd = format("cd {doris_fe_bin_path}; "
                     "sh start_fe.sh --daemon")
    Logger.info("Starting Doris FE Server, commonds is {0}.".format(cmd))
    Execute(cmd, user=params.default_user, logoutput=True)

def wait_fe_started(params):
    """
    check if master fe is started.
    waiting 36 * 5 sec
    :param params:
    :return:
    """
    started = False
    result = ''
    interval = 5
    times = 36
    cmd = format("grep 'success on {doris_fe_query_port}' {doris_fe_sys_log_dir}/fe.log")
    for go in range(times):
        if started:
            Logger.info("Doris FE Master Server started, {0}.".format(result.read()))
            break
        else:
            time.sleep(interval)
            Logger.info("Waiting Doris FE Master Server start, waiting time:{0}.".format( go * 5 ))
            result = os.popen(cmd)
            if (result.read() != ''):
                started = True

