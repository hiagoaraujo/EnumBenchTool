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

from zone_file_parser import ZoneFileParser
from zone_files_generator import ZoneFilesGenerator

class Zone2Sql(object):
    """ Creates the folders and files necessary to use the SQL database """
    def __init__(self, setup, sock, addr):
       
        print '>> Creating SQL import file...'
        generator = ZoneFilesGenerator()
        zone_parser = ZoneFileParser()
        
        self.paths = setup.parse_file('../config/paths.dat')
        setup.refresh_folder(self.paths['TEMP_FOLDER_PATH'])      
        
        generator.create_named_conf(setup, self.paths['TEMP_FOLDER_PATH'],
                                    self.paths['TEMP_FOLDER_PATH'])
        generator.create_named_conf_options(setup, self.paths['TEMP_FOLDER_PATH'])
        generator.create_named_conf_enum(setup, self.paths['TEMP_FOLDER_PATH'],
                                         self.paths['TEMP_FOLDER_PATH'])
        generator.create_db_files(setup, self.paths['TEMP_FOLDER_PATH'], sock, addr)
        
        zone_parser.parse(self.paths['TEMP_FOLDER_PATH'] + 'named.conf')
        
        setup.refresh_folder(self.paths['TEMP_FOLDER_PATH'])
        
        print '>> SQL file successfully created!'        

