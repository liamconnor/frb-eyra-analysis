"""
This needs to be tested further! Lots of changes 
made on Tuesday 11 June
"""

import os
import sys

import numpy as np

from frb_eyra_analysis import tools
from frb_eyra_analysis import reader

fnfil = sys.argv[1]

freq, dt, header = reader.read_fil_data(fnfil, start=0, stop=1)[1:]

try: 
	fntruth = sys.argv[2]
except:
	fntruth = fnfil.strip('.fil') + '.txt'

# Assume all three codes dedisperse to top of band
freq_ref_amber = np.float(freq[0])
freq_ref_heimdall = np.float(freq[0])
freq_ref_fredda = np.float(freq[0])
freq_ref_truth = np.float(np.genfromtxt(fntruth, skip_header=1, max_rows=10)[0,-1])
print(freq_ref_truth, freq_ref_amber)
fnout = fntruth.strip('.txt')

dm_min = 10.
dm_max = 3000.
nsamps_gulp = 1048576
boxcar_max = 256
dm_tol = 1.1

heim_args = (fnfil, dm_min, dm_max, nsamps_gulp, dm_tol, boxcar_max)
heimdall_pre_str = 'rm -rf /tmp/*.cand'
heimdall_str = 'time heimdall -v -f %s -dm %f %f -nsamps_gulp %d -dm_tol %f -boxcar_max %d -rfi_no_narrow -rfi_no_broad -output_dir /tmp/' % heim_args
heimdall_post_str = 'cat /tmp/*.cand > %s.cand' % fnout

amber_str = 'run_amber_args.py %s' % fnfil

fredda_cluster = '/home/arts/software/fredda/src/python/fredfof.py'
fredda_str = 'time cudafdmt -t 512 -d 4096 -x 8 -o %s.fredda %s' % (fnout, fnfil)
fredda_post_str = '%s %s.fredda;mv -f %s.fredda.fof %s.fredda' % (fredda_cluster, fnout, fnout, fnout)

print("\n==========Starting Amber==========")
os.system(amber_str)
print("\n==========Starting Heimdall==========")
os.system(heimdall_pre_str)
os.system(heimdall_str)
os.system(heimdall_post_str)
print("\n==========Starting Fredda==========")
os.system(fredda_str)
os.system(fredda_post_str)

tools.homogenise_triggers('%s.amber' % fnout, dt, fnout=fnout, max_rows=None,
                          freq_ref_in=freq_ref_amber, freq_ref_out=freq_ref_truth)

tools.homogenise_triggers('%s.cand' % fnout, dt, fnout=fnout, max_rows=None,
                          freq_ref_in=freq_ref_heimdall, freq_ref_out=freq_ref_truth)

tools.homogenise_triggers('%s.fredda' % fnout, dt, fnout=fnout, max_rows=None,
                          freq_ref_in=freq_ref_fredda, freq_ref_out=freq_ref_truth)

print('\nStarting thing\n')
blind_detection_args = (fntruth, fnout, fnout, fnout)
blind_detection_str = 'blind_detection.py %s --fn_cand_files %s_amber.out,%s_heimdall.out,%s_fredda.out --fnout %s.results' % blind_detection_args
os.system(blind_detection_str)
