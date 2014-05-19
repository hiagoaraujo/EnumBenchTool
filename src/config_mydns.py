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
import MySQLdb as mdb

class ConfigMydns(object):
    
    def __init__(self, setup, sock, addr):
        
        zone_sufix = setup.get_zone_sufix()
        domain_counter = 0                      
        sock.sendto('z;0', addr)        
        counter = 1
        step = 10        

        con = None
        """ Establishes connection with the database"""
        try:
            con = mdb.connect('localhost', setup.get_mysql_user(),
                              setup.get_mysql_user_pass(), setup.get_mysql_database());
            cur = con.cursor()
            
            cur.execute("TRUNCATE TABLE soa")
            cur.execute("TRUNCATE TABLE rr")
            ## Put the zones informations at the database
            for i in range (setup.get_num_of_zones()):
                domain_counter += 1
                cur.execute("INSERT INTO soa (origin, ns, mbox) VALUES ('" + 
                            str(i) + "." + zone_sufix + ".', 'ns." + str(i) + "." + zone_sufix + ".', 'root')")
                     
                for j in range(setup.get_zone_size()):
                    for k in range(setup.get_num_of_naptr()):
                        cur.execute("INSERT INTO rr (zone, name, type, data) VALUES (" + 
                                    str(domain_counter) + ", '" + setup.get_sub_fqdn(j) + "." + str(i) + "." + zone_sufix + 
                                    ".', 'NAPTR', '" + '0 0 "u" "sip+E2U" "!^.*$!sip:' + setup.get_user_sip_address(i, j, k) + '!" .' + "')")
                        
            # Monitoring and processing the development of the process             
                q = 100.0 * counter / (setup.get_num_of_zones())
                if q >= step:
                    step += 10
                    sock.sendto('z;' + str(int(q)), addr)
                counter += 1         
            sock.sendto('z;100', addr)
        except mdb.Error, e: 
            print "Error %d: %s" % (e.args[0], e.args[1])
            exit(1)   
        finally:    
            if con:    
                con.close()
