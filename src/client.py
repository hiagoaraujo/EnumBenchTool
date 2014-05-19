#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Copyright (c) 2011 Federal University of Uberlândia

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation;

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

Authors: Saulo da Mata <damata.saulo@gmail.com>
       : Hiago Silva  <hiago_araujo@hotmail.com>
'''

import socket
import numpy
import time

from subprocess import call, Popen

from setup_tool import SetupTool
from query_file_generator import QueryFileGenerator

PORT = 46912

class Client (object):

    def __init__(self):
        """Initializing the configurations at "Client" """ 
        self.setup_tool = SetupTool()        
        self.paths = self.setup_tool.parse_file('../config/paths.dat')
          
        host = ''                                                             # Bind server to all interfaces
        self.s = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)            # Creating the socket using IPv4, UDP
        self.s.bind((host, PORT))                                             # Binding Server to all interfaces and the chosen port.


        fLog = open(self.paths['LOG_FOLDER_PATH'] + 'enum-bench-tool-client.log', 'w')
        fLog.close()
  
#------------------------------------------------------------------------------ 

    def standby(self):
        """ Starts a session that wait for instructions to start the configurations or run the software"""
        print '>> STANDBY MODE...'              
        try: 
            while 1:
                buf, addr = self.s.recvfrom (2048)
                self.addr = addr
                if buf == 'ping':
                    self.s.sendto('client pong', self.addr)                                                # Answering to confirm that client is ready to setup.                
                if buf == 'setup':                                         
                    self.setup()
                elif buf == 'validate':
                    if self.server_is_validated(): self.run()
                elif buf == 'abort':
                    self.abort()                                           
        except KeyboardInterrupt:
            print '\t>> Exiting...'
            exit()
        
#------------------------------------------------------------------------------ 
    def setup(self):
        """Generates configuration files at client"""
        print '>> Session started...'
        self.write_to_log('>> Starting new session.\n>> Command received: setup. Setting up session...')
        
        self.s.sendto('client 100 OK', self.addr)                                         # Answering to confirm that client is ready to setup.
                
        while 1:
            # Waiting for setup data.
            buf, addr = self.s.recvfrom (4096)
            if self.setup_tool.get_client_setup_data(buf):
                break
            else:
                self.write_to_log('>> The message is corrupted. Requesting new message...\n')
                self.s.sendto('client 400 Bad Request', addr)            
                
        if self.setup_tool.create_q_files():
            QueryFileGenerator(self.setup_tool, self.s, addr)                              # This generate query files.
        else:
            self.s.sendto('q;100', addr)
        
        # Confirming success.
        self.s.sendto('client 200 OK', addr)  
        self.write_to_log('done!\n')    
        
#------------------------------------------------------------------------------ 
    def server_is_validated (self):
        """ Establishes connection with the server and tests the query files and zone files"""
        self.write_to_log('>> Command received: verify. Validating server, query files and zone files...')
              
        # Getting query samples of the queries stored in query files.
        tmp = []
        tmp.append(self.setup_tool.get_fqdn(0, 0))                                          # authoritative and existent
        tmp.append(self.setup_tool.get_fqdn(0, 0 + self.setup_tool.get_zone_size()))        # authoritative and non-existent
        tmp.append(self.setup_tool.get_fqdn_for_non_autho(0, 0))                            # non-authoritative and non-existent
        
        # Using dig command to query the server.
        self.status = []
        for k in tmp:        
            output_file = open (self.paths['TEMP_FOLDER_PATH'] + 'dig-output.dat', 'w')
            call(['dig', '@' + self.setup_tool.get_server_ip_qry(), k, 'NAPTR'], stdout=output_file)
            output_file.close ()
            self.dig_output_parser()
            

        # Verifying if the answers are ok.
        if (self.status == ['autho-exist', 'autho-non-exist', 'non-autho-non-exist']):            
            self.s.sendto('client 200 OK', self.addr)
            self.write_to_log('done!\n')
            return True
        else:
            print '>> Session aborted!'
            self.write_to_log('>> ERROR!! Dig command reported strange behavior. Please verify server connectivity, zone files and query files.\n')
            self.s.sendto('ERROR!! Dig command reported strange behavior. Please verify server connectivity, zone files and query files.', self.addr)
            return False

#------------------------------------------------------------------------------ 
    def dig_output_parser(self):
        """Classifies the type of server between (authoritarian, non - authoritarian, existent and non -  existent)""" 
        f = open (self.paths['TEMP_FOLDER_PATH'] + 'dig-output.dat')
        for line in f:
            if line.startswith(';; flags:'):
                if line.split()[3] == 'aa':
                    if (int(line.split()[8][:-1])):
                        self.status.append('autho-exist')
                    else:
                        if (int(line.split()[10][:-1])):
                            self.status.append('autho-non-exist')
                        else:
                            self.status.append('non-autho-non-exist')
                else:
                    if (int(line.split()[7][:-1])):
                        self.status.append('autho-exist')
                    else:
                        if (int(line.split()[9][:-1])):
                            self.status.append('autho-non-exist')
                        else:
                            self.status.append('non-autho-non-exist')
#------------------------------------------------------------------------------ 
    def run (self):
        """ Is the function that receives the instructions from 'master' and calls the correspondent process"""
        self.completed = []
        self.lost = []
        self.qps = []
        self.mean = []
        self.std = []
        self.cpu_repetitions = []
        self.network_repetitions = []
        self.network_max = []
                                     
        self.write_to_log('>> Waiting for remote command from master...\n')
        try: 
            while 1:                                                # Receive from master the next instructions
                buf, addr = self.s.recvfrom (2048)
                if buf == 'send-result':
                    self.send_result()
                elif buf == 'tear-down':
                    self.tear_down()
                    break
                elif buf == 'abort':
                    self.abort()
                    break
                else:                                                
                    self.num_clients_total = int(buf.split()[0])     
                    self.query_file = buf.split()[1]    
                    self.num_dnsperf_processes = int(self.setup_tool.get_num_dnsperf_processes())                
                    if not self.trigger_dnsperf(): break 
                    if not self.test_is_validated(): break
        except KeyboardInterrupt:
            print '\t>> Exiting...'
            exit (0)


#------------------------------------------------------------------------------ 
    def trigger_dnsperf(self):
        """ Executates the dnsperf tool which  is an authoritative-server-specific DNS performance testing tool""" 
        self.write_to_log('>> Command received: Trigger dnsperf')

        quotient = self.num_clients_total / self.num_dnsperf_processes
        rest = self.num_clients_total % self.num_dnsperf_processes
        if quotient:    
            num_clients_per_process = str(quotient)
            for i in range(self.num_dnsperf_processes):
                if i == self.num_dnsperf_processes - 1:
                    num_clients_per_process = str(quotient + rest)
                    output_file = open(self.paths['TEMP_FOLDER_PATH'] + 'dnsperf-output-' + str(i) + '.dat', 'w')
                    Popen(['dnsperf', '-s', self.setup_tool.get_server_ip_qry(), '-d',
                           self.paths['QUERY_FILES_FOLDER_PATH'] + self.query_file + '-' + str(i) + '.dat',
                           '-l', self.setup_tool.get_limit(), '-q', num_clients_per_process, '-H', '10', '-T', '1', '-c'],
                          stdout=output_file)
                else:
                    output_file = open(self.paths['TEMP_FOLDER_PATH'] + 'dnsperf-output-' + str(i) + '.dat', 'w')
                    Popen(['dnsperf', '-s', self.setup_tool.get_server_ip_qry(), '-d',
                           self.paths['QUERY_FILES_FOLDER_PATH'] + self.query_file + '-' + str(i) + '.dat',
                           '-l', self.setup_tool.get_limit(), '-q', num_clients_per_process, '-H', '10', '-T', '1', '-c'],
                          stdout=output_file)
        else:
            num_clients_per_process = '1'
            self.num_dnsperf_processes = rest        
            for i in range(self.num_dnsperf_processes):    
                output_file = open(self.paths['TEMP_FOLDER_PATH'] + 'dnsperf-output-' + str(i) + '.dat', 'w')
                Popen(['dnsperf', '-s', self.setup_tool.get_server_ip_qry(), '-d',
                       self.paths['QUERY_FILES_FOLDER_PATH'] + self.query_file + '-' + str(i) + '.dat',
                       '-l', self.setup_tool.get_limit(), '-q', num_clients_per_process, '-H', '10', '-T', '1', '-c'],
                      stdout=output_file)            
            
        self.write_to_log('\tdone!\n')
        
        ## Monitoring network flow
        self.trigger_bwm()            
        
        ## Monitoring dnsperf cpu utilization
        if not self.trigger_top():
            return False
        
        ## Waiting 10 seconds to make sure that all dnsperf process were finished.
        self.coutdown_timer(10)
        
        return True
                    
#------------------------------------------------------------------------------ 
    def test_is_validated (self):
        """ Verifies if during the procedure there were usage of CPU and Network and gets the results to put them in lists"""
        self.write_to_log('>> Test completed. Validating test...')
        
        q_sent_total = 0.0
        q_completed_total = 0
        q_lost_total = 0
        qps_total = 0.0
        mean_total = 0.0
        std_total = 0.0

        for i in range(self.num_dnsperf_processes):              
            f = open(self.paths['TEMP_FOLDER_PATH'] + 'dnsperf-output-' + str(i) + '.dat')
            for line in f:
                if line.startswith('  Queries sent:'):
                    q_sent = int(line.split()[2])                  
                elif line.startswith('  Queries completed:'):
                    q_completed = int(line.split()[2])
                elif line.startswith('  Queries lost:'):
                    q_lost = int(line.split()[2])
                elif line.startswith('  Queries per second:'):
                    qps = float(line.split()[3])
                elif line.startswith('Latency:'):
                    mean = float(line.split()[8])
                    std = float(line.split()[11])
                    
                    
# PDNS HAS A BUG WHICH BREAKS THE VALIDATING TEST. I'M LOOKING FOR A SOLUTION.
# FOR WHILE I'LL BELIEVE THAT SHIT DOESN'T HAPPEN! HOW INGENOUS AM I!

#                elif line.startswith('  Returned  NOERROR:'):
#                    noerror = int(line.split()[2])
#                elif line.startswith('  Returned NXDOMAIN:'):
#                    nxdomain = int(line.split()[2])      
#                elif line.startswith('  Returned  REFUSED:') or line.startswith('  Returned SERVFAIL:'):
#                    refused = int(line.split()[2])
#                    
#                                
#            if self.setup_tool.get_software() != 'pdns':            # PDNS has a bug which fails the validating test   
#                # Validating test.
#                if self.query_file == 'qry-autho-exist.dat':
#                    if noerror != q_completed:
#                        self.write_to_log('>> ERROR!! Not querying only existing records.\n')
#                        self.s.sendto('ERROR!! Not querying only existing records.', self.addr)  
#                        return False             
#                elif self.query_file == 'qry-autho-non-exist.dat':
#                    if nxdomain != q_completed:
#                        self.write_to_log('>> ERROR!! Not querying only non existing records.')
#                        self.s.sendto('ERROR!! Not querying only non existing records.', self.addr)
#                        return False
#                elif self.query_file == 'qry-non-autho-non-exist.dat':
#                    if refused != q_completed:
#                        self.write_to_log('>> ERROR!! Not querying only non existing non authoritative records.\n')
#                        self.s.sendto('ERROR!! Not querying only non existing non authoritative records.', self.addr)
#                        return False                                

            q_sent_total += q_sent
            q_completed_total += q_completed
            q_lost_total += q_lost
            qps_total += qps
            mean_total += mean
            std_total += std
        
                       
        self.completed.append(100 * q_completed_total / q_sent_total)
        self.lost.append(100 * q_lost_total / q_sent_total)
        self.mean.append(mean_total / self.num_dnsperf_processes)
        self.std.append(std_total / self.num_dnsperf_processes)
        self.qps.append(qps_total)
        
        if not self.get_dnsperf_cpu_usage():
            return False
                
        if not self.get_network_usage():
            return False

        self.write_to_log('done!\n')
        self.s.sendto('client 200 OK', self.addr)        
        return True
       
#------------------------------------------------------------------------------ 
    def get_dnsperf_cpu_usage(self):
        """ Based on 'top' results gets the numbers that represents the usage of CPU during the process and put them is a list to return"""
        f = open(self.paths['TEMP_FOLDER_PATH'] + 'top-output-dnsperf.dat').readlines()
        cpu_samples = []
        cpu_sum = 0
        not_first_flag = False
        for line in f:
            if line.startswith('top - '):
                if not_first_flag:
                    cpu_samples.append(cpu_sum)
                    cpu_sum = 0
            if line.find('dnsperf') > 0:
                not_first_flag = True
                cpu_sum += float(line.split()[8])
        if not cpu_samples:
            self.write_to_log('>> ERROR!! Process dnsperf is not alive.\n')
            self.s.sendto('ERROR!! Process dnsperf is not alive.', self.addr)
            return False            
        self.cpu_repetitions.append(numpy.mean(cpu_samples))

        return True        
    
#------------------------------------------------------------------------------ 
    def get_network_usage(self):
        """ Gets from log file from BWM the informations about network usage if they exists and returns them """
        f = open(self.paths['TEMP_FOLDER_PATH'] + 'bwm.log').readlines()
        network_samples = []
        for line in f:
            if line.split(';')[1] == 'eth0':                          #Hard code eth0.
                network_samples.append(8 * float(line.split(';')[4]))
        if not network_samples:
            self.write_to_log('>> ERROR!! Network file is empty.\n')
            self.s.sendto('>> ERROR!! Network file is empty.', self.addr)
            return False            
        self.network_repetitions.append(numpy.mean(network_samples))
        self.network_max.append(max(network_samples))
        
        return True
       
#------------------------------------------------------------------------------ 
    def send_result (self):
        """ Gets the data, process them and sends their mean as final results at appropriate units """
        self.write_to_log('>> Command received: send-result')      
          
        completed = round(numpy.mean(self.completed), 3)
        lost = round(numpy.mean(self.lost), 3)
        qps = int(numpy.mean(self.qps))
        mean = round(numpy.mean(self.mean), 6)
        std = round(numpy.mean(self.std), 6)
        cpu = round(numpy.mean(self.cpu_repetitions) / self.setup_tool.get_num_of_cpu(), 2)
        network_mean = round(numpy.mean(self.network_repetitions) * pow(10, -6), 2) ## The result is multiplied by potency due to transform the unity from bits to MegaBytes
        network_max = round(max(self.network_max) * pow(10, -6), 2)
                
        self.completed = []
        self.lost = []
        self.qps = []
        self.mean = []    
        self.std = []
        self.cpu_repetitions = []
        self.network_repetitions = []
        self.network_max = []
        
        self.s.sendto('client 200 OK;' + str(self.num_clients_total) + '\t\t' + 
                      str(completed) + '\t' + str(lost) + '\t' + str(qps) + '\t' + 
                      str(mean) + '\t' + str(std) + '\t' + str(cpu) + '\t' + 
                      str(network_mean) + '\t' + str(network_max), self.addr)
        self.write_to_log('\tdone!\n')        
               
#------------------------------------------------------------------------------ 
    def tear_down(self):
        """ Register at 'enum-bench-tool-client.log' that the procedure has finished"""
        self.write_to_log('>> Command received: tear-down.\n')        
        self.s.sendto ('client 200 OK', self.addr)
        self.write_to_log('>> Session successfully completed!\n')
        print '>> Session successfully completed!'
        print '>> STANDBY MODE...'        

#------------------------------------------------------------------------------ 
    def abort(self):
        """ Register at 'enum-bench-tool-client.log' that the procedure was aborted"""
        self.write_to_log('>> Command received: abort. Session aborted!\n')
        print '>> Session aborted!'
        print '>> STANDBY MODE...'
    
                  
#------------------------------------------------------------------------------ 
    def write_to_log(self, string):
        """ Write information about some process about client at file 'enum-bench-tool-client.log'"""
        fLog = open(self.paths['LOG_FOLDER_PATH'] + 'enum-bench-tool-client.log', 'a')
        fLog.write(string)
        fLog.close()

#------------------------------------------------------------------------------ 
    def trigger_top(self):
        """ executes the top command which provides informations about selected process indicates by the PID """
        self.write_to_log('>> Triggering Top...')
         
        pid_list = self.get_dnsperf_pid_list()        
        if pid_list:
            pid_arg = ''                                                                    # process id arguments for command top.
            for p in pid_list:
                pid_arg += ' -p ' + p
        else:
            return False
        call('top' + pid_arg + ' -d ' + '1' + ' -n ' + self.setup_tool.get_limit() + 
             ' -b > ' + self.paths['TEMP_FOLDER_PATH'] + 'top-output-dnsperf.dat', shell=True)
                
        self.write_to_log('\tdone!\n')
        return True
        
#------------------------------------------------------------------------------ 
    def get_dnsperf_pid_list(self):
        """ Gets the dnsperf pid's(process identification number) to put them in a list if them  exist"""                   
        pid_list = []                      
        call("ps -C dnsperf | grep dnsperf | tr -c '0123456789 \n' '?' | cut -d '?' -f1 | tr -d ' ' > " + 
             self.paths['TEMP_FOLDER_PATH'] + "dnsperf-pid.dat", shell=True)                       
        f = open(self.paths['TEMP_FOLDER_PATH'] + 'dnsperf-pid.dat').readlines()
        if f:
            for line in f:
                pid_list.append(line.rstrip())
        else:
            self.write_to_log('>> ERROR: the process dnsperf is not alive.\n')
            self.s.sendto ('ERROR: the process dnsperf is not alive.', self.addr)  
            return []
            
        return pid_list        

#------------------------------------------------------------------------------ 
    def coutdown_timer(self, interval): ## COLOCAR UM "N" no COUNTDOWN
        """ Regressive timmer """
        timeout_count_down = interval
        while (timeout_count_down > 0):
            time.sleep (1.0)
            timeout_count_down -= 1       

#------------------------------------------------------------------------------ 
    def trigger_bwm(self): 
        """ starts bwm tool with is as bandwidth monitor """
        self.write_to_log('>> Triggering bwm-ng...')
        
        call(['rm', '-f', self.paths['TEMP_FOLDER_PATH'] + 'bwm.log']) #VERIFICAR SE NAO ABRE UM ARQUIVO "W" 
        
        #Hard code 'eth0'.
        Popen(['bwm-ng', '-I', 'eth0', '-t', '1000', '-c', self.setup_tool.get_limit(),
               '-o', 'csv', '-F', self.paths['TEMP_FOLDER_PATH'] + 'bwm.log'])
                
        self.write_to_log('\tdone!\n')
