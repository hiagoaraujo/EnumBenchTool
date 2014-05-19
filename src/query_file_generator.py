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

import random

class QueryFileGenerator(object):
    """ Generates configuration files at client """
    def __init__(self, setup, sock, addr):
        
        paths = setup.parse_file('../config/paths.dat')             
        setup.refresh_folder(paths['QUERY_FILES_FOLDER_PATH'])
        
        qry_autho_exist_list = []
        qry_autho_non_exist_list = []
        qry_non_autho_non_exist = []
        
        for p in range(int(setup.get_num_dnsperf_processes())):
            qry_autho_exist_list.append(open(paths['QUERY_FILES_FOLDER_PATH'] + 'qry-autho-exist-' + str(p) + '.dat', 'w'))
            qry_autho_non_exist_list.append(open(paths['QUERY_FILES_FOLDER_PATH'] + 'qry-autho-non-exist-' + str(p) + '.dat', 'w'))
            qry_non_autho_non_exist.append(open(paths['QUERY_FILES_FOLDER_PATH'] + 'qry-non-autho-non-exist-' + str(p) + '.dat', 'w'))


        """ Creates a connection between client and server through socket protocol
        # and return to master the string 'q;0' which refers the progress of execution and the end point 'addr'"""
        sock.sendto('q;0', addr)
        counter = 1
        step = 10
        
        # Generates random "fqdn" registers                    
        try:
            for i in range(setup.get_num_of_zones()):        
                for j in range(setup.get_zone_size()):
                    for f in qry_autho_exist_list:
                        k = random.randint(0, setup.get_zone_size())
                        f.write(setup.get_fqdn(i, k) + ' NAPTR\n')
                    for f in qry_autho_non_exist_list:
                        k = random.randint(0, setup.get_zone_size())
                        f.write(setup.get_fqdn(i, k + setup.get_zone_size()) + ' NAPTR\n')
                    for f in qry_non_autho_non_exist:
                        k = random.randint(0, setup.get_zone_size())
                        f.write(setup.get_fqdn_for_non_autho(i, k) + ' NAPTR\n')
                    
                    # At each step% completed the animation is updated
                    c = 100.0 * counter / (setup.get_num_of_records())
                    if c >= step:
                        step += 10
                        sock.sendto('q;' + str(int(c)), addr)
                    counter += 1
                                  
            sock.sendto('q;100', addr)
            for f in qry_autho_exist_list: f.close()
            for f in qry_autho_non_exist_list: f.close()
            for f in qry_non_autho_non_exist: f.close()
        except KeyboardInterrupt:
            print '\t\t>>Exiting...'
            exit(0)
                    
