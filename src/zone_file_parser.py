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

Authors: #@author: Saulo da Mata <damata.saulo@gmail.com>
       : #@author: Hiago Silva  <hiago_araujo@hotmail.com>

'''

from setup_tool import SetupTool
from subprocess import call

class ZoneFileParser (object):

    def __init__ (self):
        
        setup = SetupTool()
        self.paths = setup.parse_file('../config/paths.dat')
        
        # Refresh import.sql file
        setup.refresh_file(self.paths['PDNS_OUTPUT_FOLDER_PATH'] + 'import.sql')
         
        self.fSql = open (self.paths['PDNS_OUTPUT_FOLDER_PATH'] + 'import.sql', 'a') 
        self.domainCounter = 0
        
#------------------------------------------------------------------------------ 
    def parse (self, named_path):
        """ Analyses the each field and line at file "zone-files", separates the informations and put them
           at the "SQL" database"""
        print '\t>> Translating from zone-files to sql...'
        
        f_named = open (named_path)
        for line in f_named:
            if line.startswith ('include'):
                f1 = open (line.split ('"')[1])
                for l1 in f1:
                    if l1.startswith ('file'):
                        f2 = open (l1.split('"')[1])
                        for l2 in f2:
                            if l2.startswith ('$TTL'):
                                self.ttl = l2.split()[1]
                            elif l2.startswith ('$ORIGIN'):
                                tmp = l2.split()[1]
                                if self.has_end_dot (tmp): self.origin = tmp[:-1]
                                else: self.origin = tmp
                            elif (l2.find (' SOA ') > 0) and (l2.startswith ('@')):
                                self.parse_soa (l2)
                            elif (l2.find (' NS ') > 0) and (l2.startswith ('@')):
                                self.parse_ns (l2)
                            elif (l2.find (' PTR ') > 0):
                                self.parse_ptr (l2)
                            elif (l2.find (' A ') > 0):
                                self.parse_a (l2)
                            elif (l2.find (' AAAA ') > 0):
                                self.parse_aaaa (l2)
                            elif (l2.find (' NAPTR ') > 0):
                                self.parse_naptr (l2)                                
                                                                    
        self.fSql.close()
        

#------------------------------------------------------------------------------ 
    def has_end_dot (self, string):
        """parses if the current string  ends with dot"""
        if string.endswith ('.'): return True
        else: return False

#------------------------------------------------------------------------------ 
    def parse_soa (self, line):
        """ parses the line containing the "SOA" informations and then separate them if there are more than one.
         Write the informations at fSql database in a different organization mode"""
        self.domainCounter += 1
        tmp = line.split()
        content = tmp[3][:-1] + ' ' + tmp[4][:-1] + ' ' + tmp[5][1:] + ' ' + tmp[6] + ' ' + tmp[7] + ' ' + tmp[8] + ' ' + tmp[9][:-1]
        self.fSql.writelines ("insert into domains (name, type) values ('" + 
                               self.origin + "', 'NATIVE');\n" + 
                               "insert into records (domain_id, name, type, content, ttl, prio) values (" + 
                               str (self.domainCounter) + ", '" + self.origin + "', 'SOA', '" + content + "', " + self.ttl + ", 0);\n")

#------------------------------------------------------------------------------ 
    def parse_ns (self, line):
        """ parses the line containing the "NS" informations and then separate them if there are more than one.
        Write the informations at fSql database in a different organization mode"""
        tmp = line.split()[3]
        if self.has_end_dot (tmp): content = tmp[:-1]
        else: content = tmp
        self.fSql.write ("insert into records (domain_id, name, type, content, ttl, prio) values (" + 
                          str (self.domainCounter) + ", '" + self.origin + "', 'NS', '" + content + "', " + self.ttl + ", 0);\n")  
        
#------------------------------------------------------------------------------ 
    def parse_ptr (self, line):
        """ parses the line containing the "PTR" informations and then separate them if there are more than one.
         Write the informations at fSql database in a different organization mode"""
        tmp = line.split()
        if self.has_end_dot (tmp[0]): name = tmp[0][:-1]
        else: name = tmp[0] + '.' + self.origin
        if self.has_end_dot (tmp[3]): content = tmp[3][:-1]
        else: content = tmp[3]
        self.fSql.write ("insert into records (domain_id, name, type, content, ttl, prio) values (" + 
                          str (self.domainCounter) + ", '" + name + "', 'PTR', '" + content + "', " + self.ttl + ", 0);\n")
        
#------------------------------------------------------------------------------ 
    def parse_a (self, line):
        """ Parses the line containing the "A" informations and then separate them if there are more than one.
         Write the informations at fSql database in a different organization mode"""
        tmp = line.split()
        if tmp[0] == '@': name = self.origin
        else:
            if self.has_end_dot (tmp[0]): name = tmp[0][:-1]
            else: name = tmp[0] + '.' + self.origin
        if self.has_end_dot (tmp[3]): content = tmp[3][:-1]
        else: content = tmp[3]
        self.fSql.write ("insert into records (domain_id, name, type, content, ttl, prio) values (" + 
                          str (self.domainCounter) + ", '" + name + "', 'A', '" + content + "', " + self.ttl + ", 0);\n")    
            
#------------------------------------------------------------------------------ 
    def parse_aaaa (self, line):
        """ Parses the line containing the "AAAA" informations and then separate them if there are more than one.
         Write the informations at fSql database in a different organization mode"""
        tmp = line.split()
        if tmp[0] == '@': name = self.origin
        else:
            if self.has_end_dot (tmp[0]): name = tmp[0][:-1]
            else: name = tmp[0] + '.' + self.origin
        if self.has_end_dot (tmp[3]): content = tmp[3][:-1]
        else: content = tmp[3]
        self.fSql.write ("insert into records (domain_id, name, type, content, ttl, prio) values (" + 
                          str (self.domainCounter) + ", '" + name + "', 'AAAA', '" + content + "', " + self.ttl + ", 0);\n")
            
#------------------------------------------------------------------------------ 
    def parse_naptr (self, line):s
        """ Parses the line containing the "NAPTR" informations and then separate them if there are more than one.
         Write the informations at fSql database in a different organization mode"""
        tmp = line.split()
        if self.has_end_dot (tmp[0]): name = tmp[0][:-1]
        else: name = tmp[0] + '.' + self.origin
        content = tmp[2] + ' ' + tmp[3] + ' ' + tmp[4] + ' ' + tmp[5] + ' ' + tmp[6] + ' ' + tmp[7]
        self.fSql.write ("insert into records (domain_id, name, type, content, ttl, prio) values (" + 
                          str (self.domainCounter) + ", '" + name + "', 'NAPTR', '" + content + "', " + self.ttl + ", 0);\n")
        
        
