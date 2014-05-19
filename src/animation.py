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

import sys

#===============================================================================

class Animation(object):
##   This class is a simple graphical tool developed to help the programmer when it's running 
#    printing a 'progress bar' at the console
#    The mainly intention of the group who is developing this tool is to create a interface and this class will 
##    be replaced by a progress bar animated and colored 
    def __init__(self):


        ##Animation settings
        self.bar_size = 10
        self.bar_pos = 0
        
        self.value_1 = 0
        self.value_2 = 0
 
        self.dots_size = 3
        self.dot_pos = 0
        
        self.spin_size = 10
        self.spin_pos = 0
        self.spin_dir = 1
        
        self.time_prev = 0
              
#------------------------------------------------------------------------------ 

    def hashtag_bar(self, value, string='', level=1): 
        """ Bar progress animation"""
      
        spin_str = '#' * self.bar_pos + '-' * (self.bar_size - self.bar_pos)
        if value == 100 : 
            sys.stdout.write('\r' + level * '\t' + string + ' 0% ' + spin_str + 
                             ' ' + str(value) + '%\n')
            self.bar_pos = 0
        else: 
            sys.stdout.write('\r' + level * '\t' + string + ' 0% ' + spin_str + 
                             ' ' + str(value) + '%')
            self.bar_pos += 1
        sys.stdout.flush()


#------------------------------------------------------------------------------ 
    
    def double_hashtag_bar(self, value, bar_id):
        """ Double progress bar, it displays simultaneously progress of two process in execution"""
        if bar_id == 1:
            self.value_1 = value
            spin_str_1 = '#' * (self.value_1 / self.bar_size) + '-' * (self.bar_size - (self.value_1 / self.bar_size))
            spin_str_2 = '#' * (self.value_2 / self.bar_size) + '-' * (self.bar_size - (self.value_2 / self.bar_size))
            sys.stdout.write('\r0% ' + spin_str_1 + ' ' + str(self.value_1) + '%\t|\t' + 
                             '0% ' + spin_str_2 + ' ' + str(self.value_2) + '%')
            sys.stdout.flush()
        if bar_id == 2:
            self.value_2 = value
            spin_str_1 = '#' * (self.value_1 / self.bar_size) + '-' * (self.bar_size - (self.value_1 / self.bar_size))
            spin_str_2 = '#' * (self.value_2 / self.bar_size) + '-' * (self.bar_size - (self.value_2 / self.bar_size))
            sys.stdout.write('\r0% ' + spin_str_1 + ' ' + str(self.value_1) + '%\t|\t' + 
                             '0% ' + spin_str_2 + ' ' + str(self.value_2) + '%')
            sys.stdout.flush()
            
#------------------------------------------------------------------------------ 
    def spin (self, string):
        """"Indicates that the process is running by displaying a bar '|' moving"""
                
        spin_str = '.' * self.spin_pos + '|' + '.' * (self.spin_size - self.spin_pos - 1)
        sys.stdout.write('\r' + string + ' ' + spin_str + '  ')
        sys.stdout.flush()

        self.spin_pos += self.spin_dir
        if self.spin_pos < 0:
            self.spin_dir = 1
            self.spin_pos = 1
        elif self.spin_pos >= self.spin_size:
            self.spin_pos -= 2
            self.spin_dir = -1

#------------------------------------------------------------------------------ 
    def count_down_timer (self, string, time):
       """Display a countdown timer """
       if len(str(time)) < len(str(self.timePrev)):                    ## When the time is smaller than the expected time 
           sys.stdout.write('\r' + string + ' ' + str(time) + 's ')
           sys.stdout.flush()
       else:
           sys.stdout.write('\r' + string + ' ' + str(time) + 's')     # When the time is bigger than the expected time, so the 
           sys.stdout.flush()                                          ### expected time gets the value of the variable 'time'
       self.timePrev = time

#===============================================================================
