# -*- coding: utf-8 -*-

from resource_management import *
from resource_management.core.resources.system import Execute, Directory, File
import os
import socket
import utils
import sys
import time

class DorisFE(Script):

    def install(self, env):
        import params
        env.set_params(params)
        local_hostname = socket.gethostname()

        # TODO if has any better ways to solve FE_OBSERVER not in FE_FOLLOWER nodes?
        for fe in params.doris_fe_hostname:
            if fe in params.doris_fe_observer_hostname:
                log_error = "!!! Importance Error !!! FE_Host:{0} is in fe_observer_hosts: {1} , " \
                            "They can not on the same node !!!!".format(fe, params.doris_fe_observer_hostname)
                Logger.info(log_error)
                raise Fail(log_error)
                sys.exit(1);

        # create doris fe metadata dir
        self.init_fe_metadata_dir(env)
        # install doris
        Logger.info("Starting install Doris FE.")
        utils.install()

        # modify file permissions
        cmd = format("chmod -R 755 {doris_install_dir}")
        Execute(cmd, user=params.default_user)

        # the first start follower and observer fe
        # Doris HA add follower FE
        self.configure(env)
        if local_hostname == params.doris_fe_hostname[0]:
            utils.fe_init_start(fe_role= 'MASTER', params = params)
            utils.wait_fe_started(params)
            utils.add_frontend(fe_role='FOLLOWER', params = params)
            utils.add_frontend(fe_role='OBSERVER', params = params)
        elif (local_hostname in params.doris_fe_hostname) and (local_hostname != params.doris_fe_hostname[0]):
            fe_role = 'FOLLOWER'
            utils.fe_init_start(fe_role, params)
        elif local_hostname in params.doris_fe_observer_hostname:
            fe_role = 'OBSERVER'
            utils.fe_init_start(fe_role, params)

        # modify file user and group
        #cmd = format("chown {doris_user}:{doris_group} -R {diros_install_dir}")
        #Execute(cmd, user=params.default_user)


    def start(self, env, upgrade_type=None, fe_role=None):
        import params
        env.set_params(params)
        # config server
        self.configure(env)
        if os.path.exists(params.doris_fe_pid_file):
            Logger.info("Doris PID file:{0} existed ,Doris FE Server already started. Nothing do!".format(params.doris_fe_pid_file))
        else:
            cmd = format("cd {doris_fe_bin_path}; sh start_fe.sh --daemon")
            Logger.info("Starting Doris FE Server, commonds is {0}.".format(cmd))
            Execute(cmd, user=params.default_user, logoutput=True)

    def stop(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        cmd = format("cd {doris_fe_bin_path}; sh stop_fe.sh --daemon")
        Logger.info("Stoping Doris FE Server, commonds is {0}.".format(cmd))
        Execute(cmd, user=params.default_user, logoutput=True, ignore_failures=True)


    def status(self, env):
        import params
        env.set_params(params)
        # check status using pid file
        check_process_status(params.doris_fe_pid_file)


    def configure(self, env):
        import params
        env.set_params(params)
        # On some OS this folder could be not exists, so we will create it before pushing there files
        Directory(params.limits_conf_dir,
                  create_parents = True,
                  owner='root',
                  group='root')

        # config doris user nprofile limit
        Logger.info(format("Creating {params.limits_conf_dir}system.conf system config file"))
        File(os.path.join(params.limits_conf_dir, 'system.conf'),
             owner='root',
             group='root',
             mode=0644,
             content=Template("system.conf.j2")
             )

        # config doris fe fe.conf file
        Logger.info(format("Creating {params.doris_fe_conf_dir}/fe.conf config file"))
        File(os.path.join(params.doris_fe_conf_dir + '/fe.conf'),
             content=InlineTemplate(params.doris_fe_conf_file),
             owner=params.default_user,
             group=params.default_group
         )


    def add_fe_follower(self, env):
        """
        add fe follower to cluster
        :param env:
        :return:
        """
        import params
        env.set_params(params)
        # TODO the function is not appropriate
        # Before add backend change root password, This is not appropriate.
        utils.add_frontend(fe_role='FOLLOWER', params = params)

    def add_fe_observer(self, env):
        '''
        add fe observer to cluster
        :param env:
        :return:
        '''
        import params
        env.set_params(params)
        # TODO the function is not appropriate
        # Before add backend change root password, This is not appropriate.
        utils.add_frontend(fe_role='OBSERVER', params = params)


    def add_backend(self, env):
        import params
        env.set_params(params)
        # TODO the function is not appropriate
        # Before add backend change root password, This is not appropriate.
        #utils.change_root_passowrd(params)
        utils.add_doris_backend(params)


    def init_fe_metadata_dir(self, env):
        import params
        env.set_params(params)
        # create doris fe metadata dir
        Directory(params.doris_fe_meta_dir,
                  create_parents = True,
                  owner=params.default_user,
                  group=params.default_group)

        Directory(params.doris_fe_sys_log_dir,
                  create_parents = True,
                  owner=params.default_user,
                  group=params.default_group)


if __name__ == "__main__":
    DorisFE().execute()
