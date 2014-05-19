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
import time
from subprocess import call

from zone_files_generator import ZoneFilesGenerator

class ConfigNsd (object):

    def __init__(self, setup, sock, addr):

        self.paths = setup.parse_file('../config/paths.dat')
        """ Do the nsd configuration at object
        ## if the zones already exists , restart the software, else install and create the zones"""
        if setup.create_zones():
            self.create_nsd_zone_files(setup, sock, addr)
            self.restart_nsd(setup, sock, addr)
        else:
            sock.sendto('z;100', addr)  
            if setup.restart_software():
                self.restart_nsd(setup, sock, addr)        
                
#------------------------------------------------------------------------------ 
    def create_nsd_zone_files(self, setup, sock, addr):
        """ creates the zone files by using the operations at "zone_file_generator" module"""
        zone_gen = ZoneFilesGenerator()
        setup.refresh_folder(self.paths['NSD_FOLDER_PATH'])
         
        zone_gen.create_nsd_conf(setup, self.paths['NSD_FOLDER_PATH'],
                                   self.paths['NSD_ZONES_FOLDER_PATH'])
        zone_gen.create_db_files(setup, self.paths['NSD_FOLDER_PATH'], sock, addr) 

        #Copying files to /etc/nsd/            
        call(['echo ' + setup.get_server_pass() + 
               ' | sudo -S rm -f /etc/nsd/*' + setup.get_domain_name()], shell=True)
        call(['echo ' + setup.get_server_pass() + 
               ' | sudo -S cp -ru ' + self.paths['NSD_FOLDER_PATH'] + ' /etc/'], shell=True)
                
#------------------------------------------------------------------------------ 
    def restart_nsd(self, setup, sock, addr):
        """ Generates a log file in order to verify restart process of the nsd tool """
        output_file = open(self.paths['TEMP_FOLDER_PATH'] + 'nsd-rebuild.log', 'w')
        call(['echo ' + setup.get_server_pass() + ' | sudo -S nsdc rebuild'], stdout=output_file, shell=True)
        output_file.close()
        if (self.nsd_is_rebuild(self.paths['TEMP_FOLDER_PATH'] + 'nsd-rebuild.log')): 
            call(['echo ' + setup.get_server_pass() + ' | sudo -S nsdc stop'], shell=True)
            call(['echo ' + setup.get_server_pass() + ' | sudo -S nsdc start'], shell=True)
            self.wait_for_process()
        else: 
            sock.sendto('ERROR!! NSD was not rebuild successfully!', addr)
                
#------------------------------------------------------------------------------ 
    def nsd_is_rebuild(self, file_name):
        """ Parses if the process was successfully concluded"""
        f = open(file_name)        
        for line in f:
            if line.find('done with no errors') >= 0:
                return True
        return False

#------------------------------------------------------------------------------ 
    def wait_for_process(self):
        """ implements a delay when the file length "pid.dat" equals to 8 """
        while (1):
            call("ps -C nsd > " + self.paths['TEMP_FOLDER_PATH'] + "pid.dat", shell=True)
            f = open(self.paths['TEMP_FOLDER_PATH'] + 'pid.dat').readlines()
            if len(f) == 8:
                return
            else:
                time.sleep(1)                
