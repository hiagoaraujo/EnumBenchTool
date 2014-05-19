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

from subprocess import call

class SetupTool(object):

    def __init__(self):
        # this class don't have initializing arguments
        pass

#------------------------------------------------------------------------------ 
    def get_server_setup_data(self, buf): 
        
        """ Create and write the network informations about the current computer in use
        in this case, the computer is the 'Server'
        The variable 'buf' is an amount of string concatenated which contains all the net informations separated by ';'"""
        try:
            f = open ('../config/server-setup.dat', 'w')             
            f.write ('// Setup configuration file\n' + 
                     'software\t' + buf.split(';')[0] + '\n' + 
                     'processes\t' + buf.split(';')[1] + '\n' + 
                     'processes_users\t' + buf.split(';')[2] + '\n' + 
                     'num_of_records\t' + buf.split(';')[3] + '\n' + 
                     'num_of_zones\t' + buf.split(';')[4] + '\n' +  
                     'domain_name\t' + buf.split(';')[5] + '\n' + 
                     'server_ip_qry\t' + buf.split(';')[6] + '\n' + 
                     'num_of_naptr\t' + buf.split(';')[7] + '\n' + 
                     'limit\t' + buf.split(';')[8] + '\n' + 
                     'num_of_cpu\t' + buf.split(';')[9] + '\n' + 
                     'update_enabled\t' + buf.split(';')[10] + '\n' + 
                     'update_rate\t' + buf.split(';')[11] + '\n')
            if buf.split(';')[0] == 'bind' or buf.split(';')[0] == 'nsd': 
                f.write('server_pass\t' + buf.split(';')[12] + '\n' + 
                        'create_zones\t' + buf.split(';')[13] + '\n' + 
                        'restart_software\t' + buf.split(';')[14] + '\n')
            elif buf.split(';')[0] == 'pdns' or buf.split(';')[0] == 'mydns':
                f.write('mysql_database\t' + buf.split(';')[12] + '\n' + 
                        'mysql_user\t' + buf.split(';')[13] + '\n' + 
                        'mysql_user_pass\t' + buf.split(';')[14] + '\n' + 
                        'create_database\t' + buf.split(';')[15] + '\n')
            f.close()     
            self.par_dict = self.parse_file('../config/server-setup.dat')               
            return 1
        except IndexError:
            return 0

#------------------------------------------------------------------------------
    def get_client_setup_data(self, buf):
        
        """ Create and write the network informations about the current computer in use
         in this case, the computer is the 'Client'     
         The variable 'buf' is an amount of string concatenated which contains all the net informations separated by ';' """
        
        try:
            f = open ('../config/client-setup.dat', 'w')             
            f.write ('// Setup configuration file\n' + 
                     'num_of_records\t' + buf.split(';')[0] + '\n' + 
                     'num_of_zones\t' + buf.split(';')[1] + '\n' + 
                     'domain_name\t' + buf.split(';')[2] + '\n' + 
                     'server_ip_qry\t' + buf.split(';')[3] + '\n' + 
                     'limit\t' + buf.split(';')[4] + '\n' + 
                     'create_q_files\t' + buf.split(';')[5] + '\n' + 
                     'num_of_cpu\t' + buf.split(';')[6] + '\n' + 
                     'num_dnsperf_processes\t' + buf.split(';')[7] + '\n')
            f.close()     
            self.par_dict = self.parse_file('../config/client-setup.dat')               
            return 1
        except IndexError:
            return 0
               
#------------------------------------------------------------------------------ 
    def get_setup_data(self, file_path):               
        self.par_dict = self.parse_file(file_path)  
        """Creates an attribute in the object that contains all the information provided by the function 'parse_file'"""
          
#------------------------------------------------------------------------------ 
    def parse_file(self, file_path):
        
        """ Analyzes if the file's path exists, if exists, open the file and reads the informations inside the file and puts them 
         in a dictionary which is represented by the variable 'par_dict' (parameter_dicionary)"""

        
        par_dict = {}
        b = ' '
         
        try:
            f_config = open (file_path)
        except IOError:
            print '\n>> PARSE ERROR!! "' + file_path + '" is not a valid file path!'
            exit ()

        for line in f_config:
            tmp = []
            value = ''
            #  ignoring comments and blank lines 
            if (line.startswith('#') or line.startswith('/') or line.startswith(' ')
                or line.startswith('*') or len(line) == 1):
                continue
            else:
                tmp = line.split()
                name = tmp[0]
                if len(tmp) > 2:
                    tmp.pop (0)
                    for v in tmp:
                        value += b + v
                    par_dict[name] = value
                else:
                    value = tmp[1]
                    par_dict[name] = value
            """ In order to include generic kinds of files this loop separates the first item to be an dictionary key and :
                 -concatenates the following items in the line to be the value of this key if there are more than one 
                 -set the second item on the list as the key value"""

        f_config.close ()

        return par_dict

#------------------------------------------------------------------------------ 

    def parse_unity(self, string):
        
        """ Parses if the string is a number or a number plus string like '200k', which indicates 200.000
        and convert it according to the following letter that represents the unity"""
        
        #Suffix
        if string.endswith('0') or string.endswith('1') or string.endswith('2') or string.endswith('3') or string.endswith('4') or string.endswith('5') or string.endswith('6') or string.endswith('7') or string.endswith('8') or string.endswith('9'):
            #numeric string found
            return int(string)
        #non-numeric string found
        elif string.endswith('k'):
            number = string[:string.find('k')] 
            return int(number) * pow(10, 3)
        elif string.endswith('K'):
            number = string[:string.find('K')] 
            return int(number) * pow(10, 3)
        elif string.endswith('M'):
            number = string[:string.find('M')]      
            return int(number) * pow(10, 6)
        elif string.endswith('G'):
            number = string[:string.find('G')] 
            return int(number) * pow(10, 9)
        elif string.find('ups') > 0:
            if string.find('kups') > 0:
                return int(string[:string.find('k')]) * pow(10, 3)
            else:
                return int(string[:string.find('u')])
        else:
            print '>> UnityParser: ERROR! Unity not available.'
    
#------------------------------------------------------------------------------ 
    def get_num_of_records(self):
        """  Converts the field 'num_of_records' at configuration file into a number """
        return self.parse_unity(self.par_dict['num_of_records'])
        
#------------------------------------------------------------------------------ 
    def get_num_of_zones(self):
        """ Converts the field 'num_of_zones' at configuration file into a number """
        return int(self.par_dict['num_of_zones'])
    
#------------------------------------------------------------------------------ 
    def get_num_of_naptr(self):
        """  Converts the field 'num_of_naptr' at configuration file into a number """
        return int(self.par_dict['num_of_naptr'])    
    
#------------------------------------------------------------------------------ 
    def get_zone_size(self):
        """ sets the zone size by dividing the amount of records by the number of zones"""
        return self.get_num_of_records() / self.get_num_of_zones()

#------------------------------------------------------------------------------ 
    def get_domain_name(self):
        """ Return the contents of the key 'domain_name' from the dictionary 'par_dict'"""
        return self.par_dict['domain_name']

#------------------------------------------------------------------------------ 
    def get_start_number(self):
        """ sets the first 'fqdn'  according to the amount of records when the server is  authoritarian 
        the figures '3' and '0' are symbolic because this number is going to be informed by the user at the interface"""
        return int('3' * (12 - len(str(self.get_num_of_records()))) + '0' * len(str(self.get_num_of_records())))

#------------------------------------------------------------------------------ 
    def get_start_number_for_non_autho(self):        
        """ sets the first 'fqdn'  according to the amount of records to test when the server is non - authoritarian  
         the figures '2' and '0' are symbolic because this number is going to be informed by the user at the interface"""
        return int('2' * (12 - len(str(self.get_num_of_records()))) + '0' * len(str(self.get_num_of_records())))
    
#------------------------------------------------------------------------------ 
    def get_zone_sufix(self):
        """ Put the 'fqdn' permanent numbers inside a list in reverse order than separates each item by dots
         excluding the numbers belonging to the sub_fqdn"""
        l = list((str(self.get_start_number())[:-(len(str(self.get_zone_size())) + 1)])[::-1])
        l.append(self.get_domain_name())                                                      
        return '.'.join(l)                                                                    

#------------------------------------------------------------------------------ 
    def get_sub_fqdn (self, j):
        """ Put the 'fqdn' last numbers, the amount is according to the zone size, inside a list in reverse order 
        # than separates each item by dots
         The sub_fqdn is used to identify the register inside the file"""
        l = list((str(self.get_start_number() + j)[-(len(str(self.get_zone_size()))):])[::-1])         
        return '.'.join(l)    

#------------------------------------------------------------------------------ 
    def get_user_sip_address (self, i, j, k):
        """Sets to the 'fqdn' number related an simulation of some information like email, website, etc. """
        return str(self.get_start_number() + j + i * pow(10, len(str(self.get_zone_size() - 1)))) + '_' + str(k + 1) + '@enum.ufu.br'

#------------------------------------------------------------------------------ 
    def get_fqdn(self, i, j):
        """ Generates the different "fqdn's" numbers of sub_fqdn, concatenates the domain name
         put it all in a list and separates each item by dots 
         When the server is authoritarian"""
        l = list(str(self.get_start_number() + j + i * pow(10, len(str(self.get_zone_size()))))[::-1])         
        l.append(self.get_domain_name())
        return '.'.join(l)

#------------------------------------------------------------------------------ 
    def get_fqdn_for_non_autho(self, i, j):
        """ Generates the different "fqdn's" numbers of sub_fqdn, concatenates the domain name
         put it all in a list and separates each item by dots
         When the server is non-authoritarian"""
        l = list(str(self.get_start_number_for_non_autho() + j + i * pow (10, len(str(self.get_zone_size()))))[::-1])         
        l.append(self.get_domain_name())
        return '.'.join(l)    
    
#------------------------------------------------------------------------------ 
    def get_server_pass(self):
        """Return the contents of the key 'server_pass' from the dictionary 'par_dict'"""
        return self.par_dict['server_pass']
    
#------------------------------------------------------------------------------ 
    def get_software(self):
        """ Return the contents of the key 'software' from the dictionary 'par_dict'"""
        return self.par_dict['software']

#------------------------------------------------------------------------------ 
    def get_processes(self):
        """ Return the contents of the key 'process' from the dictionary 'par_dict'"""
        return self.par_dict['processes']
        
#------------------------------------------------------------------------------ 
    def get_processes_users(self):
        """ Return the contents of the key 'process_user' from the dictionary 'par_dict'"""
        return self.par_dict['processes_users']

#------------------------------------------------------------------------------ 
    def get_num_of_cpu(self):
        """ Return the contents of the key 'num_of_cpu' from the dictionary 'par_dict'"""
        return int(self.par_dict['num_of_cpu'])
    
#------------------------------------------------------------------------------ 
    def get_server_ip_qry(self):
        """ Return the contents of the key 'server_ip_qry' from the dictionary 'par_dict'"""
        return self.par_dict['server_ip_qry']

#------------------------------------------------------------------------------ 
    def get_server_ip_ctrl(self):
        """ Return the contents of the key 'server_ip_ctrl' from the dictionary 'par_dict'"""
        return self.par_dict['server_ip_ctrl']
    
#------------------------------------------------------------------------------ 
    def get_client_ip_ctrl(self):
        """ Return the contents of the key 'client_ip_ctrl' from the dictionary 'par_dict'"""
        return self.par_dict['client_ip_ctrl']
           
#------------------------------------------------------------------------------ 
    def get_limit(self):
        """ Return the contents of the key 'limit' from the dictionary 'par_dict'"""
        return self.par_dict['limit']
    
#------------------------------------------------------------------------------ 
    def get_timeout(self):
        """ Return the contents of the key 'timeout' from the dictionary 'par_dict'"""
        return self.par_dict['timeout']    
        
#------------------------------------------------------------------------------ 
    def get_save_dir(self):
        """ Return the contents of the key 'save_dir' from the dictionary 'par_dict'"""
        return self.par_dict['save_dir']

#------------------------------------------------------------------------------ 
    def get_session_name(self):
        """ Return the contents of the key 'session_name' from the dictionary 'par_dict'"""
        return self.par_dict['session_name']
    
#------------------------------------------------------------------------------ 
    def get_scenario_list(self):
        """ Return the contents of the key 'scenario_list' from the dictionary 'par_dict'"""
        return self.par_dict['scenario_list'].split()

#------------------------------------------------------------------------------ 
    def get_clients_list(self):
        """ get from dicitonary 'par_dict' the client's parameters and put them in a list"""
        tmp = self.par_dict['clients'].split(',')
        clients_list = []
        for i in tmp:
            if i.find(':') > 0:
                start = int(i.split(':')[0])
                step = int(i.split(':')[1])
                end = int(i.split(':')[2])
                n_steps = ((end - start) / step) + 1
                for n in range(n_steps):
                    clients_list.append((n * step) + start)
            else:
                clients_list.append(int(i))
        return clients_list
                
#------------------------------------------------------------------------------ 
    def get_num_dnsperf_processes(self):
        """ Return the contents of the key 'num_dnsperf_processes' from the dictionary 'par_dict'"""
        return self.par_dict['num_dnsperf_processes']    

#------------------------------------------------------------------------------ 
    def get_repetitions(self):
        """ Return the contents of the key 'repetitions' from the dictionary 'par_dict'"""
        return self.par_dict['repetitions']

#------------------------------------------------------------------------------ 
    def get_query_type(self):
        """ Return the contents of the key 'query_type' from the dictionary 'par_dict'"""
        return self.par_dict['query_type']

#------------------------------------------------------------------------------ 
    def get_create_zones(self):
        """ Return the contents of the key 'create_zones' from the dictionary 'par_dict'"""
        return self.par_dict['create_zones']

#------------------------------------------------------------------------------ 
    def get_restart_software(self):
        """ Return the contents of the key 'restart_software' from the dictionary 'par_dict'"""
        return self.par_dict['restart_software']
    
#------------------------------------------------------------------------------ 
    def get_create_q_files(self):
        """ Return the contents of the key 'create_q_files' from the dictionary 'par_dict'"""
        return self.par_dict['create_q_files']  
  
#------------------------------------------------------------------------------ 
    def get_create_database(self):
        """ Return the contents of the key 'create_database' from the dictionary 'par_dict'"""
        return self.par_dict['create_database']        

#------------------------------------------------------------------------------ 
    def create_zones(self):
        """ Parse the parameters which operates files, zones and parts of the software to avoid waste of time and execution"""
        if self.par_dict['create_zones'] == 'yes':
            return True
        else:
            return False
        
#------------------------------------------------------------------------------ 
    def restart_software(self):
        """ Parse the parameters which operates files, zones and parts of the software to avoid waste of time and execution"""
        if self.par_dict['restart_software'] == 'yes':
            return True
        else:
            return False
        
#------------------------------------------------------------------------------ 
    def create_q_files(self):
        """ Parse the parameters which operates files, zones and parts of the software to avoid waste of time and execution"""
        if self.par_dict['create_q_files'] == 'yes':
            return True
        else:
            return False

#------------------------------------------------------------------------------ 
    def create_database(self):
        """ Parse the parameters which operates files, zones and parts of the software to avoid waste of time and execution"""
        if self.par_dict['create_database'] == 'yes':
            return True
        else: 
            return False  

#------------------------------------------------------------------------------
    def refresh_folder(self, folder_path):
        """ Update the content's folder by excluding and recreating it again with the modifications, if there's some"""
        call (['rm', '-rf', folder_path])
        call (['mkdir', '-p', folder_path])     

#------------------------------------------------------------------------------ 
    def create_folder(self, folder_path):
        """ Create a folder without taking care if it exists"""
        call (['mkdir', '-p', folder_path])
        
#------------------------------------------------------------------------------ 
    def delete_file(self, file_path):
        """ Delete file."""
        call (['rm', '-f', file_path])          
        
#------------------------------------------------------------------------------ 
    def copy(self, source, destination):
        """ Copy files from 'source' to 'destination' path"""
        call (['cp', source, destination])        

#------------------------------------------------------------------------------ 
    def tar(self, tar_name, source):
        """ create a tar archive with name 'tar_name'"""
        call(['tar', '-cf', tar_name, source])        
             
#------------------------------------------------------------------------------ 
    def get_session_list(self):
        """ Return the contents of the key 'session_list' from the dictionary 'par_dict'"""
        return self.par_dict['session_list'].split()
    
#------------------------------------------------------------------------------ 
    def get_plot_list(self):
        """ Return the contents of the key 'plot_list' from the dictionary 'par_dict'"""
        return self.par_dict['plot_list'].split()
    
#------------------------------------------------------------------------------ 
    def get_curves_list(self):
        """ Return the contents of the key 'curves_list' from the dictionary 'par_dict'"""
        return self.par_dict['curves_list'].split()
    
#------------------------------------------------------------------------------ 
    def get_curves_labels(self):
        """ Return the contents of the key 'curves_labels' from the dictionary 'par_dict'"""
        return self.par_dict['curves_labels'].split()
    
#------------------------------------------------------------------------------ 
    def get_curves_colors(self):
        """Return the contents of the key 'curves_colors' from the dictionary 'par_dict'"""
        return self.par_dict['curves_colors'].split()
         
#------------------------------------------------------------------------------ 
    def get_label_x_axis(self):
        """ Return the contents of the key 'label_x_axis' from the dictionary 'par_dict'"""
        return self.par_dict['label_x_axis']    

#------------------------------------------------------------------------------ 
    def throughput(self):
        """ Parse the parameters which operates files, zones and parts of the software to avoid waste of time and execution"""
        if self.par_dict['throughput'] == 'yes':
            return True
        else:
            return False
        
#------------------------------------------------------------------------------ 
    def get_throughput_label(self):
        """ Return the contents of the key 'throughput_label' from the dictionary 'par_dict'"""
        return self.par_dict['throughput_label']
    
#------------------------------------------------------------------------------ 
    def get_throughput_plot_name(self):
        """ Return the contents of the key 'throughput_plot_name' from the dictionary 'par_dict'"""
        return self.par_dict['throughput_plot_name']    
    
#------------------------------------------------------------------------------ 
    def latency_mean(self):
        """ Parse the parameters which operates files, zones and parts of the software to avoid waste of time and execution"""
        if self.par_dict['latency_mean'] == 'yes':
            return True
        else:
            return False

#------------------------------------------------------------------------------ 
    def get_latency_mean_label(self):
        """ Return the contents of the key 'latency_mean_label' from the dictionary 'par_dict'"""
        return self.par_dict['latency_mean_label']
    
#------------------------------------------------------------------------------ 
    def get_latency_mean_plot_name(self):
        """ Return the contents of the key 'latency_mean_plot_name' from the dictionary 'par_dict'"""
        return self.par_dict['latency_mean_plot_name']
            
#------------------------------------------------------------------------------ 
    def cpu_utilization(self):
        """ Parse the parameters which operates files, zones and parts of the software to avoid waste of time and execution"""
        if self.par_dict['cpu_utilization'] == 'yes':
            return True
        else:
            return False        

#------------------------------------------------------------------------------ 
    def get_cpu_utilization_label(self):
        """ Return the contents of the key 'cpu_utilization_label' from the dictionary 'par_dict'"""
        return self.par_dict['cpu_utilization_label']

#------------------------------------------------------------------------------ 
    def get_cpu_utilization_plot_name(self):
        """ Return the contents of the key 'cpu_utilization_plot_name' from the dictionary 'par_dict'"""
        return self.par_dict['cpu_utilization_plot_name']
    
#------------------------------------------------------------------------------ 
    def get_cpu_utilization_processes_list(self):
        """ Return the contents of the key 'cpu_utilization_processes' from the dictionary 'par_dict'"""
        return self.par_dict['cpu_utilization_processes'].split()    
        
#------------------------------------------------------------------------------ 
    def get_data_dir(self):
        """ Return the contents of the key 'data_dir' from the dictionary 'par_dict'"""
        return self.par_dict['data_dir']
    
#------------------------------------------------------------------------------ 
    def get_img_dir(self):
        """Return the contents of the key 'img_dir' from the dictionary 'par_dict'"""
        return self.par_dict['img_dir']
    
#------------------------------------------------------------------------------ 
    def get_gp_dir(self):
        """ Return the contents of the key 'gp_dir' from the dictionary 'par_dict'"""
        return self.par_dict['gp_dir']
    
#------------------------------------------------------------------------------ 
    def get_plot_format(self):
        """ Return the contents of the key 'plot_format' from the dictionary 'par_dict'"""
        return self.par_dict['plot_format']
    
#------------------------------------------------------------------------------ 
    def get_mysql_database(self):
        """ Return the contents of the key 'mysql_database' from the dictionary 'par_dict'"""
        return self.par_dict['mysql_database']
    
#------------------------------------------------------------------------------ 
    def get_mysql_user(self):
        """ Return the contents of the key 'mysql_user' from the dictionary 'par_dict'"""
        return self.par_dict['mysql_user']
    
#------------------------------------------------------------------------------ 
    def get_mysql_user_pass(self):
        """ Return the contents of the key 'mysql_user_pass' from the dictionary 'par_dict'"""
        return self.par_dict['mysql_user_pass']    
       
#------------------------------------------------------------------------------ 
    def update_enabled(self):
        """ Returns a boolean flag indicating if updates are enabled or not."""
        if self.par_dict['update_enabled'] == 'yes' or self.par_dict['update_enabled'] == 'True':
            return True
        else:
            return False

#------------------------------------------------------------------------------ 
    def get_update_rate(self):
        """ Return the contents of the key 'update_rate' from the dictionary 'par_dict'"""
        return self.parse_unity(self.par_dict['update_rate'])


#------------------------------------------------------------------------------ 
    def network(self):
        """ Parse the parameters which operates files, zones and parts of the software to avoid waste of time and execution"""
        if self.par_dict['network'] == 'yes':
            return True
        else:
            return False        

#------------------------------------------------------------------------------ 
    def get_network_label(self):
        """ Return the contents of the key 'network_label' from the dictionary 'par_dict'"""
        return self.par_dict['network_label']

#------------------------------------------------------------------------------ 
    def get_network_plot_name(self):
        """ Return the contents of the key 'network_plot_name' from the dictionary 'par_dict'"""
        return self.par_dict['network_plot_name']
