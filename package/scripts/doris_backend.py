# -*- coding: utf-8 -*-

from resource_management import *
from resource_management.core.resources.system import Execute, Directory, File
import os
import utils


class DorisBE(Script):
    def install(self, env):
        import params
        env.set_params(params)
        # create doris be_storage_path
        utils.split_be_storage_path(params)
        # create doris be log file dir
        Directory(params.doris_be_log_dir,
                  create_parents = True,
                  owner=params.default_user,
                  group=params.default_group)

        # install doris
        utils.install()
        # modify file permissions
        cmd = format("chmod -R 755 {doris_install_dir}")
        Execute(cmd, user=params.default_user)


    def start(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        # config server
        self.configure(env)
        # start doris fe
        cmd = format("cd {doris_be_bin_path}; sh start_be.sh --daemon")
        Logger.info("Starting Doris BE Server, commonds is {0}.".format(cmd))
        Execute(cmd, user=params.default_user, logoutput=True)

    def stop(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        # start doris fe
        cmd = format("cd {doris_be_bin_path}; sh stop_be.sh --daemon")
        Logger.info("Stoping Doris BE Server, commonds is {0}.".format(cmd))
        Execute(cmd, user=params.default_user, logoutput=True, ignore_failures=True)

    def status(self, env):
        import params
        env.set_params(params)
        # check status using pid file
        check_process_status(params.doris_be_pid_file)

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

        # write be.conf file
        Logger.info(format("Creating {params.doris_be_conf_dir}/be.conf config file"))
        File(os.path.join(params.doris_be_conf_dir + '/be.conf'),
             content=InlineTemplate(params.doris_be_conf_file),
             owner=params.default_user,
             group=params.default_group
             )



if __name__ == "__main__":
    DorisBE().execute()
