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

from setup_tool import SetupTool

class BenchResultsParser (object):
    
    def __init__ (self):
        
        self.setup = SetupTool()
        self.paths = self.setup.parse_file('../config/paths.dat')
        self.setup.get_setup_data('../config/result-parser-setup.dat')

        y_axis = []
        y_axis.append((self.setup.throughput(), self.setup.get_throughput_label(), self.setup.get_throughput_plot_name(), 4))
        y_axis.append((self.setup.latency_mean(), self.setup.get_latency_mean_label(), self.setup.get_latency_mean_plot_name(), 5))
        y_axis.append((self.setup.network(), self.setup.get_network_label(), self.setup.get_network_plot_name(), 8))
        
        n = 0
        for p in self.setup.get_cpu_utilization_processes_list():
            y_axis.append((self.setup.cpu_utilization(),
                           self.setup.get_cpu_utilization_label(),
                           self.setup.get_cpu_utilization_plot_name() + '-' + p,
                           7 + n))
            n += 2
        

        print '>> Starting plot process...'                
        for i in self.setup.get_session_list():
            for j in self.setup.get_plot_list():
                call(['mkdir', '-p', self.setup.get_img_dir() + i + '/' + j])
                call(['mkdir', '-p', self.setup.get_gp_dir() + i + '/' + j])
                if j.startswith('a') or j.startswith('n'):
                    for q in range(len(y_axis)):
                        if y_axis[q][0]:
                            f_gp = open(self.setup.get_gp_dir() + i + '/' + j + '/' + y_axis[q][2] + '.gp', 'w')
                            if self.setup.get_plot_format() == 'eps':
                                f_gp.write('set terminal postscript eps color enhanced\n')
                            else:
                                f_gp.write('set terminal ' + self.setup.get_plot_format() + '\n') 
                            f_gp.write('set encoding utf8\n' + 
                                       'set output "' + self.setup.get_img_dir() + i + '/' + j + '/' + y_axis[q][2] + '-' + i + '-' + j + '.' + self.setup.get_plot_format() + '"\n' + 
                                       'set grid\n' + 
                                       'set xtics auto\n' + 
                                       'set ytics auto\n' + 
                                       'set mxtics 5\n' + 
                                       'set mytics 5\n' + 
                                       'set xlabel "' + self.setup.get_label_x_axis() + '"\n' + 
                                       'set ylabel "' + y_axis[q][1] + '"\n' + 
                                       'set key bottom\n')
                            for k in self.setup.get_curves_list():
                                f_gp.write('set style line ' + str(self.setup.get_curves_list().index(k) + 1) + ' lt 1 lw 2 lc rgb "' + self.setup.get_curves_colors()[self.setup.get_curves_list().index(k)] + '"\n')
                            f_gp.write('plot ')
                            for k in self.setup.get_curves_list():
                                if k == self.setup.get_curves_list()[-1]:
                                    f_gp.write('"' + self.setup.get_data_dir() + i + '/' + k + '/' + j + '/stats.dat' + 
                                               '" u 1:' + str(y_axis[q][3]) + ' title "' + 
                                               self.setup.get_curves_labels()[self.setup.get_curves_list().index(k)] + 
                                               '" w lp ls ' + str(self.setup.get_curves_list().index(k) + 1))
                                else:
                                    f_gp.write('"' + self.setup.get_data_dir() + i + '/' + k + '/' + j + '/stats.dat' + 
                                               '" u 1:' + str(y_axis[q][3]) + ' title "' + 
                                               self.setup.get_curves_labels()[self.setup.get_curves_list().index(k)] + 
                                               '" w lp ls ' + str(self.setup.get_curves_list().index(k) + 1) + ', \\\n')
                            f_gp.close()
                            call(['gnuplot', self.setup.get_gp_dir() + i + '/' + j + '/' + y_axis[q][2] + '.gp'])
                else:
                    for q in range(len(y_axis)):
                        if y_axis[q][0]:
                            f_gp = open(self.setup.get_gp_dir() + i + '/' + j + '/' + y_axis[q][2] + '.gp', 'w')
                            if self.setup.get_plot_format() == 'eps':
                                f_gp.write('set terminal postscript eps color enhanced\n')
                            else:
                                f_gp.write('set terminal ' + self.setup.get_plot_format() + '\n') 
                            f_gp.write('set encoding utf8\n' + 
                                       'set output "' + self.setup.get_img_dir() + i + '/' + j + '/' + y_axis[q][2] + '-' + i + '-' + j + '.' + self.setup.get_plot_format() + '"\n' + 
                                       'set grid\n' + 
                                       'set xtic auto\n' + 
                                       'set ytic auto\n' + 
                                       'set mxtics 5\n' + 
                                       'set mytics 5\n' + 
                                       'set xlabel "' + self.setup.get_label_x_axis() + '"\n' + 
                                       'set ylabel "' + y_axis[q][1] + '"\n' + 
                                       'set key bottom\n')
                            for k in self.setup.get_curves_list():
                                f_gp.write('set style line ' + str(self.setup.get_curves_list().index(k) + 1) + ' lt 1 lw 2 lc rgb "' + self.setup.get_curves_colors()[self.setup.get_curves_list().index(k)] + '"\n')
                            f_gp.write('plot ')
                            for k in self.setup.get_curves_list():
                                if k == self.setup.get_curves_list()[-1]:
                                    f_gp.write('"' + self.setup.get_data_dir() + i + '/' + j + '/' + k + '/stats.dat' + 
                                               '" u 1:' + str(y_axis[q][3]) + ' title "' + 
                                               self.setup.get_curves_labels()[self.setup.get_curves_list().index(k)] + 
                                               '" w lp ls ' + str(self.setup.get_curves_list().index(k) + 1))
                                else:
                                    f_gp.write('"' + self.setup.get_data_dir() + i + '/' + j + '/' + k + '/stats.dat' + 
                                               '" u 1:' + str(y_axis[q][3]) + ' title "' + 
                                               self.setup.get_curves_labels()[self.setup.get_curves_list().index(k)] + 
                                               '" w lp ls ' + str(self.setup.get_curves_list().index(k) + 1) + ', \\\n')
                            f_gp.close()
                            call(['gnuplot', self.setup.get_gp_dir() + i + '/' + j + '/' + y_axis[q][2] + '.gp'])
        print '>> Plot process successfully completed.'
           
#------------------------------------------------------------------------------ 
if __name__ == "__main__":        
    myParser = BenchResultsParser ()
    
