import sys, os, glob, pwd, grp, signal, time
from resource_management import *

class ServiceCheck(Script):
    def service_check(self, env):
        import params
        env.set_params(params)

        if None != params.doris_fe_hostname:
            if os.path.exists(params.doris_fe_pid_file):
                print "Doris FE Server is runing on the Current host."
            else:
                print "Doris FE Server is not runing on the Current host."
        else:
            print "Current host is " + params.hostname + " which is not server host."

        if None != params.doris_be_hostname:
            if os.path.exists(params.doris_be_pid_file):
                print "Doris BE is runing on the Current host."
            else:
                print "Doris BE is not runing on the Current host."
        else:
            print "Current host is " + params.hostname + " which is not agent host."

if __name__ == "__main__":
    ServiceCheck().execute()