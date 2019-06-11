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
freq_ref_amber = freq[0]
freq_ref_heimdall = freq[0]
freq_ref_fredda = freq[0]
print(freq.max())

dm_min = 10.
dm_max = 3000.
outdir = './'
fnout = fntruth.strip('.txt')

heim_args = (fnfil, dm_min, dm_max)
heimdall_str = 'heimdall -v -f %s -dm %f %f -rfi_no_narrow -rfi_no_broad -output_dir /tmp/' % heim_args
heimdall_post_str = 'cat /tmp/*.cand > %s.cand' % fnout

amber_str = 'run_amber_args.py %s' % fnfil

fredda_cluster = '/home/arts/software/fredda/src/python/fredfof.py'
fredda_str = 'cudafdmt -t 512 -d 16384 -x 6 -o %s.fredda %s' % (fnout, fnfil)
fredda_post_str = '%s %s.fredda;mv -f %s.fredda.fof %s.fredda' % (fredda_cluster, fnout, fnout, fnout)

print("\n==========Starting Amber==========")
#os.system(amber_str)
print("\n==========Starting Heimdall==========")
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
blind_detection_str = 'blind_detection.py %s --fn_cand_files %s.cand,%s.fredda --fnout %s.results' % blind_detection_args
print(blind_detection_str)
exit()
os.system(blind_detection_str)
