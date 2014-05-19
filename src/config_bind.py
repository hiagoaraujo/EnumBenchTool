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

from zone_files_generator import ZoneFilesGenerator

class ConfigBind (object):
    """ Do the bind configuration at object
    if the zones already exists , restart the software, else install and create the zones"""
    def __init__(self, setup, sock, addr):
        
        self.paths = setup.parse_file('../config/paths.dat')
        
        if setup.create_zones():
            self.create_bind_zone_files(setup, sock, addr)
            self.restart_bind(setup, sock, addr)
        else:
            sock.sendto('z;100', addr)  
            if setup.restart_software():
                self.restart_bind(setup, sock, addr)        
                
#------------------------------------------------------------------------------ 
    def create_bind_zone_files(self, setup, sock, addr):
        """ creates the zone files by using the operations at 'zone_file_generator' module """
        zone_gen = ZoneFilesGenerator()
        setup.refresh_folder(self.paths['BIND_FOLDER_PATH'])
         
        zone_gen.create_named_conf(self.paths['BIND_FOLDER_PATH'],
                                   self.paths['BIND_ZONES_FOLDER_PATH'])
        zone_gen.create_named_conf_options(self.paths['BIND_FOLDER_PATH'])
        zone_gen.create_named_conf_enum(setup, self.paths['BIND_FOLDER_PATH'],
                                        self.paths['BIND_ZONES_FOLDER_PATH'])
        zone_gen.create_db_files(setup, self.paths['BIND_FOLDER_PATH'], sock, addr) 

        #Copying files to /etc/bind/         
        call(['echo ' + setup.get_server_pass() + 
               ' | sudo -S rm -f /etc/bind/*' + setup.get_domain_name()], shell=True)
        call(['echo ' + setup.get_server_pass() + 
               ' | sudo -S cp -ru ' + self.paths['BIND_FOLDER_PATH'] + ' /etc/'], shell=True)
                
#------------------------------------------------------------------------------ 
    def restart_bind(self, setup, sock, addr):
        """ Generates a log file in order to verify restart process of the bind tool """
        output_file = open(self.paths['TEMP_FOLDER_PATH'] + 'bind-restart.log', 'w')
        call(['echo ' + setup.get_server_pass() + ' | sudo -S /etc/init.d/bind9 restart'], stdout=output_file, shell=True)
        output_file.close()
        if (self.bind_is_restarted(self.paths['TEMP_FOLDER_PATH'] + 'bind-restart.log')): pass
        else: sock.sendto('ERROR!! BIND was not restarted successfully!', addr)
                
#------------------------------------------------------------------------------ 
    def bind_is_restarted(self, file_name):
        """Verifies if the file was restarted correctly """
        f = open(file_name)
        next_line = False
        
        for line in f:
            if line.find('* Starting') >= 0:
                next_line = True
            if line.find('...done.') >= 0:
                if next_line:
                    return True
        return False
