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

class ZoneFilesGenerator(object):
    
    def __init__(self):
        pass

#------------------------------------------------------------------------------ 
    def create_named_conf(self, output_folder, path):
        """ creates configuration zone file """
        file_name = output_folder + 'named.conf'            
        f = open(file_name, 'w')                       
        f.write('include "' + path + 'named.conf.options";\n' + 
                 'include "' + path + 'named.conf.enum";'
                 )
        f.close()    
        
#------------------------------------------------------------------------------ 
    def create_named_conf_options(self, output_folder):
        """ creates  configuration file of zone options """
        file_name = output_folder + 'named.conf.options'
        f = open(file_name, 'w')           
        f.write('options {\n' + 
                '\trecursion no;\n' + 
                '\tadditional-from-auth no;\n' + 
                '\tadditional-from-cache no;\n' + 
                '\tauth-nxdomain no;    # conform to RFC1035\n' + 
                '\tlisten-on-v6 { any; };\n' + 
                '};'
                )
        f.close()    
               
    
#------------------------------------------------------------------------------ 
    def create_named_conf_enum (self, setup, output_folder, path):
        """ creates enum configuration file    """     
        file_name = output_folder + 'named.conf.enum'
        f = open(file_name, 'w')           
        for i in range (setup.get_num_of_zones()):
            f.write('zone "' + str(i) + '.' + setup.get_zone_sufix() + '" {\n' + 
                    'type master;\n' + 
                    'file "' + path + 'db.' + str(i) + '.' + setup.get_zone_sufix() + '";\n' + 
                    '};\n\n'
                    )
        f.close()    
       
#------------------------------------------------------------------------------ 
    def create_db_files (self, setup, output_folder, socket, addr):
        """ concatenates the zone parameters in a string to send it to be registered at a database"""
        zone_sufix = setup.get_zone_sufix()
              
        socket.sendto('z;0', addr)        
        counter = 1
        step = 10
        
        for i in range (setup.get_num_of_zones()):         
            file_name = output_folder + 'db.' + str(i) + '.' + zone_sufix
            f = open(file_name, 'w')           
            f.write('$TTL 86400\n' + 
                     '$ORIGIN ' + str(i) + '.' + zone_sufix + '.\n' + 
                     '@ IN SOA ns.' + str(i) + '.' + zone_sufix + '. root.' + 
                     setup.get_domain_name() + '. (' + 
                     '1 21600 3600 604800 3600)\n' + 
                     '@ IN NS ns.' + str(i) + '.' + zone_sufix + '.\n' + 
                     'ns IN A ' + setup.get_server_ip_qry() + '\n\n')
            for j in range(setup.get_zone_size()):
                for k in range(setup.get_num_of_naptr()):
                    f.write(setup.get_sub_fqdn(j) + ' NAPTR 0 0 "u" "sip+E2U" "!^.*$!sip:' + 
                            setup.get_user_sip_address(i, j, k) + '!" .\n')
            f.close()    
            q = 100.0 * counter / (setup.get_num_of_zones())
            if q >= step:
                step += 10
                socket.sendto('z;' + str(int(q)), addr)
            counter += 1         
        socket.sendto('z;100', addr)        

#------------------------------------------------------------------------------
    def create_nsd_conf(self, setup, output_folder, path):
        """ creates nsd configuration file  which contains informations about the server and zones"""
        file_name = output_folder + 'nsd.conf'
        f = open(file_name, 'w') 

        f.write('server:\n' + 
                '\tzonesdir: "' + path + '"\n' + 
                '\tserver-count: 5\n')
                  
        for i in range (setup.get_num_of_zones()):
            f.write('zone:\n' + 
                    '\tname: "' + str(i) + '.' + setup.get_zone_sufix() + '"\n' + 
                    '\tzonefile: "db.' + str(i) + '.' + setup.get_zone_sufix() + '"\n\n')

        f.close()    
