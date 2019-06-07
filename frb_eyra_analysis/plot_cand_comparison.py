import sys 

import optparse
import numpy as np 

from frb_eyra_analysis import tools
from frb_eyra_analysis import plotter

if __name__=='__main__':

    SNRTools = tools.SNR_Tools()

    parser = optparse.OptionParser(prog="tools.py", \
                        version="", \
                        usage="%prog fn1 fn2 [OPTIONS]", \
                        description="Compare to single-pulse trigger files")
    parser.add_option('--sig_thresh', dest='sig_thresh', type='float', \
                        help="Only process events above >sig_thresh S/N" \
                                "(Default: 5.0)", default=5.0)
    parser.add_option('--save_data', dest='save_data', type='str',
                        help="save each trigger's data. 0=don't save. \
                        hdf5 = save to hdf5. npy=save to npy. concat to \
                        save all triggers into one file",
                        default='hdf5')
    parser.add_option('--mk_plot', dest='mk_plot', action='store_true', \
                        help="make plot if True (default False)", default=False)
    parser.add_option('--dm_min', dest='dm_min', type='float',
                        help="", 
                        default=0.0)
    parser.add_option('--dm_max', dest='dm_max', type='float',
                        help="", 
                        default=np.inf)
    parser.add_option('--t_max', dest='t_max', type='float',
                        help="Only process first t_max seconds", 
                        default=np.inf)
    parser.add_option('--t_window', dest='t_window', type='float',
                        help="", 
                        default=0.1)
    parser.add_option('--outdir', dest='outdir', type='str',
                        help="directory to write data to", 
                        default='./data/')
    parser.add_option('--title', dest='title', type='str',
                        help="directory to write data to", 
                        default='file1 vs. file2')
    parser.add_option('--figname', dest='figname', type='str',
                        help="directory to write data to", 
                        default='comparison.pdf')
    parser.add_option('--algo1', dest='algo1', type='str',
                        help="name of first algo", 
                        default='algorithm1')
    parser.add_option('--algo2', dest='algo2', type='str',
                        help="name of second algo", 
                        default='algorithm2')
    parser.add_option('--truthfile', dest='truthfile', type='str',
                        help="truth file", 
                        default=None)
    parser.add_option('--tab', dest='tab', type=int, \
                        help="TAB to process (0 for IAB) (default: 0)", default=0)
    parser.add_option('--plot_both', dest='plot_both', action='store_true', \
                        help="make plot with both fn1 vs. fn2 and fn2 vs. fn1", default=False)
    parser.add_option('--freq_ref_1', dest='freq_ref_1', type=float, \
                        help="Reference frequency of fn1", default=1400.)
    parser.add_option('--freq_ref_2', dest='freq_ref_2', type=float, \
                        help="Reference frequency of fn2", default=1400.)


    options, args = parser.parse_args()
    fn_1 = args[0]
    fn_2 = args[1]

    try:
        par_1a, par_2a, par_match_arra, ind_misseda, ind_matcheda = SNRTools.compare_snr(fn_1, fn_2, 
                                        dm_min=options.dm_min, 
                                        dm_max=options.dm_max, save_data=False,
                                        sig_thresh=options.sig_thresh, 
                                        t_window=options.t_window, 
                                        max_rows=None, t_max=options.t_max,
                                                                                         tab=options.tab, freq_ref_1=options.freq_ref_1, freq_ref_2=options.freq_ref_2)
        if options.plot_both is True:
            par_1b, par_2b, par_match_arrb, ind_missedb, ind_matchedb = SNRTools.compare_snr(fn_2, fn_1, 
                                        dm_min=options.dm_min, 
                                        dm_max=options.dm_max, save_data=False,
                                        sig_thresh=options.sig_thresh, 
                                        t_window=options.t_window, 
                                        max_rows=None, t_max=options.t_max, 
                                                                                             tab=options.tab, freq_ref_1=options.freq_ref_2, freq_ref_2=options.freq_ref_1)                                       

    except TypeError:
        print("No matches, exiting")
        exit()
        
    print('\nFound %d common trigger(s)' % par_match_arra.shape[1])

    snr_1 = par_match_arra[0, :, 0]
    snr_2 = par_match_arra[0, :, 1]

    print('\nFile 1 has %f times higher S/N than file 2\n' % np.mean(snr_1/snr_2))

    mk_plot = True

    if options.mk_plot is True:

        import plotter 
        plotter.plot_comparison(par_1a, par_2a, par_match_arra, ind_misseda, 
                                figname=options.figname,
                                algo1=options.algo1, algo2=options.algo2)

        if options.plot_both is True:
            plotter.plot_comparison(par_1b, par_2b, par_match_arrb, ind_missedb, 
                                figname=options.figname, 
                                algo1=options.algo2, algo2=options.algo1)

        if options.truthfile is not None:
            par_1, par_1_truth, par_match_1, ind_misseda, ind_matched1 = \
                                        SNRTools.compare_snr(fn_1, options.truthfile, 
                                        dm_min=options.dm_min, 
                                        dm_max=options.dm_max, save_data=False,
                                        sig_thresh=options.sig_thresh, 
                                        t_window=options.t_window, 
                                                             max_rows=None, t_max=options.t_max, 
                                                             tab=options.tab)

            par_2, par_2_truth, par_match_2, ind_missedb, ind_matched2 = \
                                        SNRTools.compare_snr(fn_2, options.truthfile, 
                                        dm_min=options.dm_min, 
                                        dm_max=options.dm_max, save_data=False,
                                        sig_thresh=options.sig_thresh, 
                                        t_window=options.t_window, 
                                                             max_rows=None, t_max=options.t_max, 
                                                             tab=options.tab)                                       
 
            plotter.plot_against_truth(par_match_1, par_match_2)

            print("Comparing both against the truth file")
            
            
#        SNRTools.plot_comparison(par_1, par_2, par_match_arr, ind_missed, figname=figname)

