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
#import MySQLdb as mdb
import random

from subprocess import call
from threading import Timer

from setup_tool import SetupTool
from config_bind import ConfigBind
#from config_nsd import ConfigNsd
#from config_pdns import ConfigPdns
#from config_mydns import ConfigMydns

PORT = 36912

class Server (object):

    def __init__ (self):
        
        self.setup_tool = SetupTool()
        self.paths = self.setup_tool.parse_file('../config/paths.dat')
        
        host = ''                                                             # Bind server to all interfaces
        self.s = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)            # Creating the socket using IPv4, UDP
        self.s.bind((host, PORT))                                             # Binding Server to all interfaces and the chosen port.
        

        fLog = open(self.paths['LOG_FOLDER_PATH'] + 'enum-bench-tool-server.log', 'w')
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
                    self.s.sendto('server pong', self.addr)                                                # Answering to confirm that server is ready to setup.                    
                elif buf == 'setup':                
                    self.setup()
                elif buf == 'validate':
                    if self.process_is_validated(): self.run()                    
                elif buf == 'abort':
                    self.abort()
        except KeyboardInterrupt:
            print '\t>> Exiting...'
            exit()
            
#------------------------------------------------------------------------------ 
    def setup(self):
        """ Configure the parameters to run the tool """
        print '>> Session started...'                    
        self.write_to_log('>> Starting new session.\n>> Command received: setup. Setting up session...')
        
        self.s.sendto('server 100 OK', self.addr)                                                # Answering to confirm that server is ready to setup.
        
        while 1:
            # Waiting for setup data.        
            buf, addr = self.s.recvfrom (4096)
            if self.setup_tool.get_server_setup_data(buf):
                break
            else:
                self.write_to_log('>> The message is corrupted. Requesting new message...\n')
                self.s.sendto('server 400 Bad Request', addr)                

        
        # This generate database.
        self.config_server()        
        
        # Confirming success.        
        self.s.sendto('server 200 OK', addr)
        self.write_to_log('done!\n')
        
#------------------------------------------------------------------------------ 
    def process_is_validated(self):
        """ Parses if the process is valid when get the data of processes performances """
        self.write_to_log('>> Command received: verify. Validating processes and process users...')
        
        self.processes_list = self.setup_tool.get_processes().split()
        self.processes_users_list = self.setup_tool.get_processes_users().split()
        
        # Get process id list
        pid_list = self.get_pid_list() 
        if pid_list:
            self.pid_arg = ''                                                                    # process id arguments for command top.
            for p in pid_list:
                self.pid_arg += ' -p ' + p
        else:
            return False
        
        call('top' + self.pid_arg + ' -d 1 -n 1 -b > ' + 
             self.paths['TEMP_FOLDER_PATH'] + 'top-output.dat', shell=True)
                
        f = open(self.paths['TEMP_FOLDER_PATH'] + 'top-output.dat').readlines()
        self.cpu_repetitions = []                                                                # list with cpu utilization in each repetition
        mem = ''
        for user in self.processes_users_list:
            self.cpu_repetitions.append([]) 
            cpu = []
            for line in f:
                if line.find(user + ' ') > 0:
                    cpu.append(float(line.split()[8]))
                    mem += user + ' memory usage\tVir: ' + line.split()[4] + '\tRes: ' + line.split()[5] + '\tShd: ' + line.split()[6] + '\t' + line.split()[9] + '%;'
            if not cpu:
                self.write_to_log('>> ERROR!! User process (' + user + ') not identified.\n')
                self.s.sendto('ERROR!! User process (' + user + ') not identified.', self.addr)
                return False

        self.s.sendto('server 200 OK;' + mem, self.addr)
        self.write_to_log('done!\n')
        return True
                       
#------------------------------------------------------------------------------ 
    def run (self):
        """ Receive from 'master' the instructions and call the corresponding functions """                     
        if self.setup_tool.update_enabled():
            if self.setup_tool.get_software() == 'pdns':
                self.connect_to_mysql()
                self.start_update()
               
        self.write_to_log('>> Waiting for remote command from master...\n')
        try:         
            while 1:
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
                    self.trigger_top()
                    if not self.test_is_validated():
                        break
        except KeyboardInterrupt:
            print '\t>> Exiting...'
            exit(0)
            
#------------------------------------------------------------------------------ 
    def update(self):
        """ Updates all data corresponding with parameters """
        zone_sufix = self.setup_tool.get_zone_sufix()                 
        
        self.cur.execute("UPDATE records SET content =  %s WHERE name = %s",
                         (str(self.ordem) + ' 0 "u" "sip+E2U" "!^.*$!sip:' + self.setup_tool.get_user_sip_address(self.zone, self.record, 0) + '!" .',
                          self.setup_tool.get_sub_fqdn(self.record) + "." + str(self.zone) + "." + zone_sufix))
        self.record += 1
        if self.record >= self.setup_tool.get_zone_size():
            self.record = 0
            self.zone += 1
        if self.zone >= self.setup_tool.get_num_of_zones():
            self.record = 0
            self.zone = 0
            self.ordem += 1
        # sets a update rate                    
        self.timer = Timer(random.expovariate(self.setup_tool.get_update_rate()), self.update)
        self.timer.start()


#------------------------------------------------------------------------------ 
    def get_pid_list(self):
        """ Gets all id from each process  alive and put them in a list """
        pid_list = []                      
        for i in self.processes_list:
            call("ps -C " + i + " | grep " + i + 
                 " | tr -c '0123456789 \n' '?' | cut -d '?' -f1 | tr -d ' ' > " + 
                 self.paths['TEMP_FOLDER_PATH'] + "pid.dat", shell=True)                       
            f = open(self.paths['TEMP_FOLDER_PATH'] + 'pid.dat').readlines()
            if f:
                for line in f:
                    if self.setup_tool.get_software() == 'nsd':
                        if not (f.index(line) == 0 or f.index(line) == 1):
                            pid_list.append(line.rstrip())
                    elif i == 'mydns':
                        if not (f.index(line) == 0):
                            pid_list.append(line.rstrip())                            
                    else:
                        pid_list.append(line.rstrip())
            else:
                self.write_to_log('>> ERROR: the process (' + i + ') is not alive.\n')
                self.s.sendto ('ERROR: the process (' + i + ') is not alive.', self.addr)  
                return []
            
        return pid_list

#------------------------------------------------------------------------------ 
    def send_result(self):
        """ Gets the data, process them and sends their mean as final results at appropriate units """
        self.write_to_log('>> Command received: send-result')
        
        cpu_process = ''
        for u in self.processes_users_list:
            mean = round(numpy.mean(self.cpu_repetitions[self.processes_users_list.index(u)]) / self.setup_tool.get_num_of_cpu(), 2)
            cpu_process += '\t' + str(mean)
            
        # refresh cpu_repetitions list            
        self.cpu_repetitions = []            
        for user in self.processes_users_list:
            self.cpu_repetitions.append([]) 
            
        self.s.sendto('server 200 OK;' + cpu_process, self.addr)
        self.write_to_log('\tdone!\n')            
            
#------------------------------------------------------------------------------   
    def test_is_validated(self):
        """ Verifies if during the procedure there were usage of CPU and Network and gets the results to put them in lists"""
        self.write_to_log('>> Test completed. Validating test...')
        
        f = open(self.paths['TEMP_FOLDER_PATH'] + 'top-output.dat').readlines()
        for user in self.processes_users_list: 
            cpu_samples = []
            cpu_sum = 0
            not_first_flag = False
            for line in f:
                if self.setup_tool.get_software() == 'nsd':
                    if line.startswith('top - '):
                        if not_first_flag:
                            cpu_samples.append(cpu_sum)
                            cpu_sum = 0
                    if line.find('nsd') > 0:
                        not_first_flag = True
                        cpu_sum += float(line.split()[8])
                elif user == 'mydns':
                    if line.startswith('top - '):
                        if not_first_flag:
                            cpu_samples.append(cpu_sum)
                            cpu_sum = 0
                    if line.find('mydns') > 0:
                        not_first_flag = True
                        cpu_sum += float(line.split()[8])                        
                else:
                    if line.find(user + ' ') > 0:
                        cpu_samples.append(float(line.split()[8]))
            if not cpu_samples:
                self.write_to_log('>> ERROR!! User process (' + user + ') not identified.\n')
                self.s.sendto('ERROR!! User process (' + user + ') not identified.', self.addr)
                return False            
            self.cpu_repetitions[self.processes_users_list.index(user)].append(numpy.mean(cpu_samples))

        self.write_to_log('done!\n')
        self.write_to_log('>> Replying to master...\n')
        self.s.sendto('server 200 OK', self.addr)
        return True 
        
#------------------------------------------------------------------------------ 
    def tear_down(self):
        """ Register at 'enum-bench-tool-server.log' that the procedure has finished"""
        self.write_to_log('>>Command received: tear-down.\n')
                
        if self.setup_tool.update_enabled():
            if self.setup_tool.get_software() == 'pdns':
                self.timer.cancel()
                self.sql_con.close()
                
        self.s.sendto ('server 200 OK', self.addr)
        self.write_to_log('>> Session successfully completed!\n')
        print '>> Session successfully completed!'
        print '>> STANDBY MODE...'           
    
#------------------------------------------------------------------------------ 
    def write_to_log(self, string):
        """ Write information about some process about client at file 'enum-bench-tool-server.log'"""
        fLog = open(self.paths['LOG_FOLDER_PATH'] + 'enum-bench-tool-server.log', 'a')
        fLog.write(string)
        fLog.close()

#------------------------------------------------------------------------------ 
    def abort(self):    
        """ Register at log file the 'abort' instruction and indicate the tool is on 'standby mode' """                
        self.write_to_log('>> Command received: abort. Session aborted!\n')
        print '>> Session aborted!'
        print '>> STANDBY MODE...' 

#------------------------------------------------------------------------------ 
    def connect_to_mysql(self):
                
        try:
            self.sql_con = mdb.connect('localhost', self.setup_tool.get_mysql_user(),
                                   self.setup_tool.get_mysql_user_pass(), self.setup_tool.get_mysql_database());
            self.cur = self.sql_con.cursor()
        except mdb.Error, e: 
            print "Error %d: %s" % (e.args[0], e.args[1])
            exit()

#------------------------------------------------------------------------------ 
    def start_update(self):
        """ Set the initial parameters and start the 'update' procedure after a defined period"""                        
        self.zone = 0
        self.record = 0
        self.ordem = 1
                                         
        self.timer = Timer(random.expovariate(self.setup_tool.get_update_rate()), self.update) 
        self.timer.start()

#------------------------------------------------------------------------------ 
    def trigger_top(self):
        """ executes the top command which provides informations about selected process indicates by the PID """
        self.write_to_log('>> Command received: Trigger Top') 
        self.setup_tool.delete_file(self.paths['TEMP_FOLDER_PATH'] + 'top-output.dat')
        call('top' + self.pid_arg + ' -d ' + '1' + ' -n ' + self.setup_tool.get_limit() + 
             ' -b >> ' + self.paths['TEMP_FOLDER_PATH'] + 'top-output.dat', shell=True)
                
        self.write_to_log('\tdone!\n')


#------------------------------------------------------------------------------ 
    def config_server (self):
        """ Configurates the 'server' according to the tool desired"""              
        if self.setup_tool.get_software() == 'bind': 
            ConfigBind(self.setup_tool, self.s, self.addr)
        elif self.setup_tool.get_software() == 'nsd':
            ConfigNsd(self.setup_tool, self.s, self.addr)
        elif self.setup_tool.get_software() == 'mydns':
            ConfigMydns(self.setup_tool, self.s, self.addr)            
        elif self.setup_tool.get_software() == 'pdns':
            ConfigPdns(self.setup_tool, self.s, self.addr)    
