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
import time

from threading import Timer
from datetime import timedelta, datetime

from animation import Animation
from setup_tool import SetupTool


PORT = 26912
SERVERPORT = 36912
CLIENTPORT = 46912

class Master(object):

#------------------------------------------------------------------------------ 
    def __init__(self):
        
        self.anime = Animation ()
        
        host = ''                                                              # Bind server to all interfaces
        self.s = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)             # Creating the socket using IPv4, UDP
        self.s.bind((host, PORT))                                              # Binding Server to all interfaces and the chosen port.
        

        self.setup_tool = SetupTool()
        self.paths = self.setup_tool.parse_file('../config/paths.dat')
        self.setup_tool.get_setup_data('../config/session-setup.dat')

        self.clients_list = self.setup_tool.get_clients_list()
                
        self.query_type = self.setup_tool.get_query_type().split()
        self.repetitions = int(self.setup_tool.get_repetitions())
               
        fLog = open(self.paths['LOG_FOLDER_PATH'] + 'enum-bench-tool-master.log', 'w')
        fLog.close()
        
        
        # Refreshing results folder and temp folder
        for s in self.setup_tool.get_scenario_list():
            self.setup_tool.refresh_folder(self.setup_tool.get_save_dir() + self.setup_tool.get_session_name() + 
                                           '/' + s + '/')
        self.setup_tool.refresh_folder(self.paths['TEMP_FOLDER_PATH'])    
             
#------------------------------------------------------------------------------
    # Hiago, this module is temporary. Don't worry about it
    def test_estimation_time (self):
        
        #Number of scenarios
        self.num_scen = len (self.query_type)
     
        self.iterations = len(self.query_type) * self.repetitions * len(self.clients_list)
        total_time = len(self.query_type) * self.repetitions * len(self.clients_list) * (int(self.setup_tool.get_limit()) + int(self.setup_tool.get_timeout()) + 10)

        duration = timedelta (seconds=total_time)
        self.start = datetime.now()
        self.end = self.start + duration

        self.write_to_log('\t>> Scenario run time\n\t\t>> Estimated: ' + str(duration) + '\n' + 
                         '\t\t>> Starting scenario at: ' + str(self.start) + '\n')
                       
        print '\n>> Estimated run time: ', duration
        print '>> Starting scenario at: ', self.start
        print '>> Estimation to finish this scenario: ', self.end
        
#------------------------------------------------------------------------------ 
    def start(self):
        """ executes the tool in each scenario and register the results """
        self.write_to_log('>> Session started at ' + str(datetime.now()) + '\n')
        print '>> Session started at ', datetime.now()
        
        self.check_connection()
         
        scen = 1
        for scenario in self.setup_tool.get_scenario_list():
            self.write_to_log('>> Running scenario ' + str(scen) + '\n')
            self.setup(scenario)
            self.validate()
            self.test_estimation_time()
            self.run(scenario)
            scen += 1
            
        print '>> Session finished at ', datetime.now()            

#------------------------------------------------------------------------------ 
    def check_connection(self):
        """ Check the connections between Server and Master, Client and Master """
        self.write_to_log('>> Checking connection...\n')
        
        self.s.sendto('ping', (self.setup_tool.get_client_ip_ctrl(), CLIENTPORT))
        self.s.sendto('ping', (self.setup_tool.get_server_ip_ctrl(), SERVERPORT))
        
        # wait 2 seconds for the answer before considering remote machine off-line.
        t = Timer(2, self.offline)
        t.start()
        
        server_status = False
        client_status = False        
        
        try:
            while 1:
                buf, addr = self.s.recvfrom(1024)
                if buf == 'server pong':
                    t.cancel()
                    self.write_to_log('\t>> Server is alive.\n')
                    server_status = True
                elif buf == 'client pong':
                    t.cancel()
                    self.write_to_log('\t>> Client is alive.\n')
                    client_status = True  
                else:
                    if buf.find('ERROR') >= 0:
                        self.parse_error(buf)

                if server_status and client_status:
                    break
                                    
        except KeyboardInterrupt:
            self.write_to_log('>> Ctrl+c pressed! Exiting...\n')
            print '\t>> Exiting...'
            exit()
        
#------------------------------------------------------------------------------ 
    def setup(self, scenario):        
        """ Establishes connections and gets the necessary data to run the tests"""
        self.write_to_log('\t>> Setup phase...')
        
        self.s.sendto('setup', (self.setup_tool.get_client_ip_ctrl(), CLIENTPORT))
        self.s.sendto('setup', (self.setup_tool.get_server_ip_ctrl(), SERVERPORT))
                       
        server_status = False
        client_status = False
        
        self.num_of_records = self.setup_tool.parse_unity(scenario)
        
        if self.setup_tool.get_software() == 'bind' or self.setup_tool.get_software() == 'nsd':
            print '\nquery files\t\t|\tzone files'
        elif self.setup_tool.get_software() == 'pdns' or self.setup_tool.get_software() == 'mydns':
            print '\nquery files\t\t|\tMySQL'
            
        try:
            while 1:
                buf, addr = self.s.recvfrom(4096)
                if buf == 'server 100 OK':
                    self.send_server_setup()
                elif buf == 'client 100 OK':
                    self.send_client_setup()                    
                elif buf == 'server 400 Bad Request':
                    self.write_to_log('>> Message to server was corrupted. Sending again...')
                    self.send_server_setup()
                elif buf == 'client 400 Bad Request':
                    self.write_to_log('>> Message to client was corrupted. Sending again...')
                    self.send_client_setup()
                elif buf == 'server 200 OK':
                    server_status = True
                elif buf == 'client 200 OK':
                    client_status = True           
                elif buf.startswith('q'):
                    self.anime.double_hashtag_bar(int(buf.split(';')[1]), 1)
                elif buf.startswith('z'):
                    self.anime.double_hashtag_bar(int(buf.split(';')[1]), 2)
                else:
                    if buf.find('ERROR') >= 0:
                        self.parse_error(buf)

                if server_status and client_status:
                    break                    
        except KeyboardInterrupt:
            self.write_to_log('>> Ctrl+c pressed! Exiting...\n')
            print '\t>> Exiting...'
            exit()
        self.write_to_log('done!\n')


#------------------------------------------------------------------------------ 
    def send_server_setup (self):
        """ Get data of scenario related to Server """    
        default = str(self.setup_tool.get_software() + ';' + self.setup_tool.get_processes() + ';' + 
                      self.setup_tool.get_processes_users() + ';' + str(self.num_of_records) + ';' + 
                      str(self.setup_tool.get_num_of_zones()) + ';' + self.setup_tool.get_domain_name() + ';' + 
                      self.setup_tool.get_server_ip_qry() + ';' + str(self.setup_tool.get_num_of_naptr()) + ';' + 
                      self.setup_tool.get_limit() + ';' + str(self.setup_tool.get_num_of_cpu()) + ';' + 
                      str(self.setup_tool.update_enabled()) + ';' + str(self.setup_tool.get_update_rate()) + ';')
                      
        if self.setup_tool.get_software() == 'bind' or self.setup_tool.get_software() == 'nsd':
            software_specifics = str(self.setup_tool.get_server_pass() + ';' + self.setup_tool.get_create_zones() + ';' + 
                                     self.setup_tool.get_restart_software())
        elif self.setup_tool.get_software() == 'pdns' or self.setup_tool.get_software() == 'mydns':
            software_specifics = str(self.setup_tool.get_mysql_database() + ';' + self.setup_tool.get_mysql_user() + ';' + 
                                  self.setup_tool.get_mysql_user_pass() + ';' + self.setup_tool.get_create_database())
        
        self.s.sendto(default + software_specifics, (self.setup_tool.get_server_ip_ctrl(), SERVERPORT))

#------------------------------------------------------------------------------ 
    def send_client_setup(self):
        """ Get data of scenario related to Client """      
        self.s.sendto(str(self.num_of_records) + ';' + 
                      str(self.setup_tool.get_num_of_zones()) + ';' + 
                      self.setup_tool.get_domain_name() + ';' + 
                      self.setup_tool.get_server_ip_qry() + ';' + 
                      self.setup_tool.get_limit() + ';' + 
                      self.setup_tool.get_create_q_files() + ';' + 
                      str(self.setup_tool.get_num_of_cpu()) + ';' + 
                      self.setup_tool.get_num_dnsperf_processes(), (self.setup_tool.get_client_ip_ctrl(), CLIENTPORT))
                      
#------------------------------------------------------------------------------ 
    def offline (self):
        """ Reports that Client or Server is not connected """
        self.s.sendto('ERROR!! Client or Server is offline.', ('127.0.0.1', PORT))
        
#------------------------------------------------------------------------------ 
    def validate(self):
        """ Verify if the connections and other procedures to run the test at Client and Server are ready """
        self.write_to_log('\t>> Validating process, process users, server connectivity, query files and zone files...')
               
        self.s.sendto('validate', (self.setup_tool.get_client_ip_ctrl(), CLIENTPORT))
        self.s.sendto('validate', (self.setup_tool.get_server_ip_ctrl(), SERVERPORT))
        
        server_status = False
        client_status = False
        
        try:
            while 1:
                buf, addr = self.s.recvfrom(2048)
                if buf == 'client 200 OK':                 
                    client_status = True
                    self.write_to_log('\tclient OK')
                elif buf.startswith('server 200 OK'):
                    server_status = True
                    tmp = buf.split(';')
                    tmp.pop(0)
                    self.mem = tmp
                    self.write_to_log('\tserver OK')                    
                else:
                    if buf.find('ERROR') >= 0:
                        self.parse_error(buf)
                        
                if server_status and client_status:
                    self.write_to_log('\n')
                    break                              
        except KeyboardInterrupt:
            self.write_to_log('>> Ctrl+c pressed! Exiting...\n')
            print '\t>> Exiting...'
            exit()       
        
##------------------------------------------------------------------------------
    def run(self, scenario):
        """ Executes the tests in each scenario """                                                                                 
        print '>> Starting queries...'
              
        for q in self.query_type:
            self.insert_header(scenario, q)
            for clients in self.clients_list:
                self.write_to_log('\t>> Clients: ' + str(clients) + '\n')
                for j in range(self.repetitions):                                      
                    self.write_to_log('\t\t>>  Repetition ' + str(j + 1) + '/' + str(self.repetitions) + '\n')
                    self.control_test(clients, q)                                   
                self.write_to_file(scenario, q)
        self.control_tear_down() 
        
        self.write_to_log('\t>> Scenario successfully completed at ' + str(datetime.now()) + '\n')
        print '>> Scenario successfully completed!'
                        
##------------------------------------------------------------------------------ 
    def write_to_log(self, string):
        """ Write information about some process about client at file 'enum-bench-tool-master.log'"""
        fLog = open(self.paths['LOG_FOLDER_PATH'] + 'enum-bench-tool-master.log', 'a')
        fLog.write(string)
        fLog.close()        

##------------------------------------------------------------------------------ 
    def control_test(self, clients, q):
        """ Control the tests rate """
        self.s.sendto(str(clients) + ' ' + 
                      q, (self.setup_tool.get_client_ip_ctrl(), CLIENTPORT))
        self.s.sendto('-', (self.setup_tool.get_server_ip_ctrl(), SERVERPORT))

        server_status = False
        client_status = False
        
        self.write_to_log('\t\t\t>> teste running...')
        
        try:
            while 1:                    
                buf, addr = self.s.recvfrom(2048)
                if buf == 'server 200 OK': 
                    server_status = True
                    self.write_to_log('\tserver ok!')
                elif buf == 'client 200 OK': 
                    client_status = True
                    self.write_to_log('\tclient ok!')             
                else:
                    if buf.find('ERROR') >= 0:
                        self.parse_error(buf)

                if server_status and client_status:
                    timeout_count_down = int(self.setup_tool.get_timeout())
                    self.write_to_log('\ttimeout...\n')
                    while (timeout_count_down > 0):
                        time.sleep (1.0)
                        timeout_count_down -= 1
                    break                                                
        except KeyboardInterrupt:
            print '\t>> Exiting...'
            exit ()        
            
##------------------------------------------------------------------------------ 
    def write_to_file(self, scenario, q):
        """ Writes the results from Client and Server at file """
        server_status = False
        client_status = False
        
        f_stats = open(self.setup_tool.get_save_dir() + self.setup_tool.get_session_name() + '/' + 
                       scenario + '/' + q[4:] + '.dat', 'a')
        
        self.write_to_log('\t\t>> Writing to file...')
        self.s.sendto('send-result', (self.setup_tool.get_client_ip_ctrl(), CLIENTPORT))
        self.s.sendto('send-result', (self.setup_tool.get_server_ip_ctrl(), SERVERPORT))
        try:
            while 1:
                buf, addr = self.s.recvfrom(2048)
                if buf.startswith('server 200 OK'): 
                    server_status = True
                    server_result = buf.split(';')[1]
                    self.write_to_log('\tserver ok!')
                elif buf.startswith('client 200 OK'): 
                    client_status = True
                    self.write_to_log('\tclient ok!')             
                    client_result = buf.split(';')[1]
                    
                if server_status and client_status:
                    self.write_to_log('\n')
                    f_stats.write(client_result + server_result + '\n')
                    f_stats.close()
                    break
        
        except KeyboardInterrupt:
            print '\t>> Exiting...'
            exit()        
            
#------------------------------------------------------------------------------ 
    def control_tear_down(self):
        """ Send to client and server the instruction to run the function 'tear_down' """
        server_status = False
        client_status = False
        
        self.write_to_log('\n\t>> Teardown session...')
        self.s.sendto('tear-down', (self.setup_tool.get_client_ip_ctrl(), CLIENTPORT))        
        self.s.sendto('tear-down', (self.setup_tool.get_server_ip_ctrl(), SERVERPORT))    
        
        try:
            while 1:
                buf, addr = self.s.recvfrom(2048)
                if buf == 'server 200 OK': 
                    server_status = True
                    self.write_to_log('\tserver ok!')                    
                elif buf == 'client 200 OK': 
                    client_status = True
                    self.write_to_log('\tclient ok!')       

                if server_status and client_status:
                    self.write_to_log('\n')
                    break
        except KeyboardInterrupt:
            print '\t>> Exiting...'
            exit()

#------------------------------------------------------------------------------
    def parse_error(self, buf): 
        """ Reports an error at log file and abort the operations at Client and Server"""
        self.write_to_log('>> ' + buf + '\n')
        print '>> ' + buf
        self.s.sendto('abort', (self.setup_tool.get_client_ip_ctrl(), CLIENTPORT))
        self.s.sendto('abort', (self.setup_tool.get_server_ip_ctrl(), SERVERPORT))
        print '>> Session aborted!'
        exit()

#------------------------------------------------------------------------------ 
    def insert_header(self, scenario, q):
        """ Insert a header with all process and unities involved"""
        f_stats = open(self.setup_tool.get_save_dir() + self.setup_tool.get_session_name() + '/' + 
                            scenario + '/' + q[4:] + '.dat', 'w')
        
        f_stats.write('# session:\t' + self.setup_tool.get_session_name() + '\n' + 
                      '# scenario:\t' + scenario + '\n' + 
                      '# records:\t' + q[4:] + '\n')
        for u in self.mem:
            f_stats.write('# ' + u + '\n')
            
        title = '#Clients\tCompleted\tLost\tthroughput\tLatency\t\t\t\tdnsperf\tnetwork\tnet_max'
        for process in self.setup_tool.get_processes().split():
            title += '\t' + process
            
        unity = '#\t\t(%)\t(%)\t(qps)\tmean(s)\tstd\t\tcpu(%)\t(Mbps)\t(Mbps)'
        for process in self.setup_tool.get_processes().split():
            unity += '\tcpu(%)'
             
        f_stats.write(title + '\n' + 
                      unity + '\n')
        f_stats.close()        

