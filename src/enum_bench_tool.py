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

import argparse
from client import Client
from master import Master
from server import Server
from bench_results_parser import BenchResultsParser


class EnumBenchTool (object):
    
    def __init__(self):
        
       
        self.parse_options()
        
        if self.mode == 'client':
            client = Client()
            client.standby()
        elif self.mode == 'master':
            master = Master()           
            master.start()
        elif self.mode == 'server':
            server = Server()
            server.standby()
        else:
            BenchResultsParser()
              
#------------------------------------------------------------------------------ 
    def parse_options(self):

        parser = argparse.ArgumentParser(description='...')               
        parser.add_argument ('-m', dest='mode', choices=('master', 'server', 'client', 'result-parser'), help='Tool mode.')
        
        args = parser.parse_args()
        self.mode = args.mode        
           
#------------------------------------------------------------------------------ 
if __name__ == "__main__":
    myBench = EnumBenchTool()                      
        
