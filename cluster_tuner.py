#!/usr/bin/env python
#
# Optimize blocksize of apps/mmm_block.cpp
#
# This is an extremely simplified version meant only for tutorials
#

import opentuner
import sys
import shutil
from opentuner import ConfigurationManipulator
from opentuner import IntegerParameter
from opentuner import EnumParameter
from opentuner import MeasurementInterface
from opentuner import Result
import os
import subprocess
import re
import time

#class for start job on cluster!
class ClusterRunner:
    def __init__(self):
        self.reason = ["",
        "Job execution failed, before files, no retry",
        "Job execution failed, after files, no retry",
        "Job execution failed, do retry",
        "Job aborted on MOM initialization",
        "Job aborted on MOM init, chkpt, no migrate",
        "Job aborted on MOM init, chkpt, ok migrate",
        "Job restart failed",
        "Exec() of user command failed",
        "Could not create/open stdout stderr files",
        #"Job exceeded a memory limit",
        "Job exceeded a walltime limit", # we use outdated TORQUE on hadoop2
        "Job exceeded a walltime limit",
        "Job exceeded a CPU time limit"]
            
    def submit(self,command,dir,nodes,ppn,walltime):
        if not os.access(dir, os.F_OK):  
            os.makedirs(dir) 
        job_file_str = os.path.join(os.path.abspath(dir),"jobfile")
        #~ print job_file_str
        job_file = open (job_file_str,"w")
        
        job_file.write("#PBS -d ")
        job_file.write(os.path.abspath(dir))
        job_file.write("\n#PBS -e stderr\n")
        job_file.write("#PBS -o stdout\n")
        job_file.write("#PBS -l nodes=%(nodes)d:ppn=%(ppn)d\n"%{'nodes':nodes,'ppn':ppn})
        job_file.write("#PBS -l walltime=%(walltime)d\n"%{'walltime':walltime})
        job_file.write("#PBS -q batch\n")
        
        job_file.write(command)
        
        job_file.close()
        try:
            p = subprocess.Popen(["qsub",job_file_str],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (id,er) = p.communicate()
            return int(id.split('.',1)[0])
        except Exception as e:
            raise Exception("Unable to initiate PBS")

    def get_state(self,pid):
        try:
            p = subprocess.Popen(["qstat", "-f",str(pid)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (resp,er) = p.communicate()
        except Exception as e:
            raise Exception("Unable to get the status of the job")
        
        stat_m = re.search("job_state = (?P<status>\w)", resp)
        if stat_m:
            if (stat_m.group('status') == 'R') or (stat_m.group('status') == 'E'):
                return ("RUNNING",0)
            elif (stat_m.group('status') == 'Q') or (stat_m.group('status') == 'S') or (stat_m.group('status') == 'W') or (stat_m.group('status') == 'H') or (stat_m.group('status') == 'T'):
                return ("QUEUED",0)
            elif (stat_m.group('status') == 'C'):
                exit_m = re.search("exit_status = (?P<status>-?\d+)", resp)
                if exit_m:
                    exit_code = int(exit_m.group('status'))
                    if exit_code == 0:
                        wall_reg = re.search("resources_used\.walltime = (?P<wallh>\d+):(?P<wallm>\d+):(?P<walls>\d+)", resp)
                        time = int(wall_reg.group("wallh"))*3600 + int(wall_reg.group("wallm"))*60 + int(wall_reg.group("walls"))
                        return ("DONE",time)
                    else:
                        st = "FAILED Exit code: "+str(exit_code)
                        if exit_code < 0:
                            ec = -1*exit_code
                            if ec in range(1,13):
                                st += " ("
                                st += self.reason[ec]
                                st += ")"
                        return (st,0)
                else:
                    raise Exception("Unable to parse the status of the job")
        else:
            raise Exception("Unable to parse the status of the job")
        
    def cancel(self,pid):
        try:
            p = subprocess.Popen(["qdel", str(pid)])
            p.wait()
        except:
            pass


##
class GccFlagsTuner(MeasurementInterface):
    name = ''
    variables = []
    gcc_cmd = ''
    run_cmd = ''
    def parse_line(self,line,manipulator):
        line=line.split()
        if(line[0]=='parameter'):
            self.variables.append(line[2])
            if(line[1]=='int'):
                manipulator.add_parameter(IntegerParameter(line[2], line[3], line[4]))
            elif(line[1]=='float'):
                manipulator.add_parameter(FloatParameter(line[2], line[3], line[4]))
            elif(line[1]=='enum'):
                manipulator.add_parameter(EnumParameter(line[2],line[3:]))
            else:
                raise NameError('Incorrect Configuration file')
        elif(line[0]=='compile'):
            self.gcc_cmd = ' '.join(line[1:])
        elif(line[0]=='run'):
            self.run_cmd = ' '.join(line[1:])
        else:
            raise NameError('Incorrect Configuration file')         

    def param_parser(self,manipulator):
      with open('configuration.txt', 'r') as f:
        for line in f:
            self.parse_line(line,manipulator)
    cluster = ClusterRunner()
    def manipulator(self):
        """
        Define the search space by creating a
        ConfigurationManipulator
        """
        self.parallel_compile = True
        manipulator = ConfigurationManipulator()
        if(len(self.variables)==0):
            self.param_parser(manipulator)
#    self.param1 = manipulator.PermutationParameter("BLOCK_SIZE", [0,1,2,3,4,5,6,7,8,9])
    #self.manipulator.add_parameter(self.param1)
        return manipulator

    def compile(self, cfg, id):
        """
        Compile and run a given configuration then
        return performance
        """
    #cfg = desired_result.configuration.data
        run_dir = os.path.join(os.getcwd(), 'job{0}'.format(str(id)))
        nodes = 1 # cluster nodes
        ppn = 1 # processor cores
        wtime_limit = 60 # seconds
##    gcc_cmd = 'g++ ../{0}'.format(name)
##    for v in variables:
##      gcc_cmd += ' -D{0}={1}'.format(v,cfg[v])                                     
##    gcc_cmd += ' -o ./tmp.bin -std=c++11'.format(str(id))
        self.gcc_cmd = self.gcc_cmd.format(**cfg)
    #call compile
        job_id = self.cluster.submit(self.gcc_cmd, run_dir, nodes, ppn, wtime_limit)
        job_state = None
        while job_state == None or job_state == "QUEUED" or job_state == "RUNNING":
            time.sleep(1)
            job_state = self.cluster.get_state(job_id)[0]
        assert job_state == "DONE"
        self.run_cmd = self.run_cmd.format(**cfg)
        job_id = self.cluster.submit(self.run_cmd, run_dir, nodes, ppn, wtime_limit)
        job_state = None
        while job_state == None or job_state == "QUEUED" or job_state == "RUNNING":
            time.sleep(1)
            job_state = self.cluster.get_state(job_id)[0]
        print job_state
        if job_state.find('-10')==-1:
            assert job_state == "DONE"
            t = self.cluster.get_state(job_id)[1]
            shutil.rmtree('job{0}'.format(str(id)))
            return Result(time=t)
        else:
            return Result(time= wtime_limit+1)


    def run_precompiled(self, desired_result, input, limit, compile_result, id):
        return compile_result

    def run(self, desired_result, input, limit):
        pass

    def save_final_config(self, configuration):
        """called at the end of tuning"""
        print "Optimal block size written to mmm_final_config.json:", configuration.data
        self.manipulator().save_to_file(configuration.data,
                                    'mmm_final_config.json')


if __name__ == '__main__':
##  name = sys.argv[1]
##  sys.argv.remove(name)
    argparser = opentuner.default_argparser()
    GccFlagsTuner.main(argparser.parse_args())



