from pandas import read_csv as pandas__read_csv
from .amber_utils import (
    list_files_in_current_path,
    check_path_ends_with_slash,
    check_directory_exists,
    parse_scenario_to_dictionary,
    get_root_name,
    get_max_dm,
    get_scenario_file_from_root_yaml_base_dict,
    pretty_print_command,
    get_full_output_path_and_file,
    get_list_as_str
)
import subprocess
import os
import time

"""
.. module:: amber_results
   :platform: Unix, Windows
   :synopsis: Module to load amber's results

.. moduleauthor:: D. Vohl <vohl@astron.nl>


"""

def get_header(filename, sep=' '):
    """Get filterbank's header.

    Parameters
    ----------
    filename  : str
        filterbank file to read
    sep  : str
        Separator
    Returns
    -------
    header : dict
        Filterbank's header
    """
    with open(filename, 'r') as f:
        return f.readline().split('\n')[0].split('# ')[1].split(sep)

def read_amber_run_results(run_output_dir, verbose=False, sep = ' '):
    """Read amber results from a run.

    Parameters
    ----------
    run_output_dir : str
        Path to output .trigger files
    verbose : bool
        Print developement information
    sep  : str
        Separator
    Returns
    -------
    df : Pandas.DataFrame
        All results in one dataframe.
    """
    # Get input file's header (amber format)
    header = get_header(
        "%s%s" % (
            check_path_ends_with_slash(run_output_dir),
            list_files_in_current_path(run_output_dir)[0]
        ), sep)

    # Create empty dataframe
    df = pandas__read_csv(
        # path/to/file.trigger
        "%s%s" % (
            check_path_ends_with_slash(run_output_dir),
            list_files_in_current_path(run_output_dir)[0]
        ),
        sep=sep,
        names=header,
        skiprows=1
    )

    # Go through output files
    for file in list_files_in_current_path(run_output_dir)[1:]:
        if '.trigger' in file:
            if verbose:
                print (file)

            # Append .trigger files to pandas' dataframe
            df.append(
                pandas__read_csv(
                    # path/to/file.trigger
                    "%s%s" % (
                        check_path_ends_with_slash(run_output_dir),
                        file
                    ),
                    sep=sep,
                    names=header,
                    skiprows=1
                ),
                ignore_index=True
            )

    return df

def run_arts_analysis_triggers(input_yaml_file,
                               root='subband',
                               min_cpu_id=0,
                               max_cpu_id=2,
                               detach=True,
                               verbose=False,
                               print_only=False):

    assert input_yaml_file.split('.')[-1] in ['yaml', 'yml']
    base = parse_scenario_to_dictionary(input_yaml_file)[root]
    root_name = get_root_name(input_yaml_file)

    # Get max dm
    scenario_file = get_scenario_file_from_root_yaml_base_dict(base, max_cpu_id)
    max_dm = get_max_dm(
        parse_scenario_to_dictionary(
            scenario_file
        )
    )

    # Get min dm
    scenario_dict = parse_scenario_to_dictionary(
        get_scenario_file_from_root_yaml_base_dict(base, min_cpu_id)
    )
    min_dm = scenario_dict['SUBBANDING_DM_FIRST']

    trigger_file = "%s%s%s%s%s" % (
        check_path_ends_with_slash(base['output_dir']),
        check_path_ends_with_slash(root_name),
        'combined/',
        root_name,
        '.trigger'
    )

    output_dir = get_full_output_path_and_file(
        base['output_dir'],
        base['base_name'],
        root_name=root_name
    )

    '''
    python $py_path/triggers.py $fil_file $trigger_file --rficlean --dm_min 5
            --dm_max 1500 --mk_plot --ndm 1 --ntime_plot 250
            --outdir $output_dir concat  --sig_thresh 8. --save_data 0
    '''
    command = ['python', '$ARTS_ANALYSIS_PATH/triggers.py',
               base['input_file'], trigger_file,
               '--rficlean', '--dm_min', min_dm, '--dm_max', max_dm,
               '--mk_plot', '--ndm', 1, '--ntime_plot', 250,
               '--outdir', output_dir, 'concat', '--sig_thresh', 8.,
               ' --save_data', 0]

    if verbose:
        pretty_print_command(command)

    if not print_only:
        if detach:
            os.system(get_list_as_str(command) + ' &')
        else:
            os.system(get_list_as_str(command))

def run_arts_analysis_tools_against_ground_truth(input_yaml_file,
                                                 truth_file=None,
                                                 root='subband',
                                                 max_cpu_id=2,
                                                 detach=True,
                                                 combine=True,
                                                 invert_order=False,
                                                 verbose=True,
                                                 print_only=False):
    assert input_yaml_file.split('.')[-1] in ['yaml', 'yml']
    base = parse_scenario_to_dictionary(input_yaml_file)[root]
    root_name = get_root_name(input_yaml_file)
    max_dm = get_max_dm(
        parse_scenario_to_dictionary(
            get_scenario_file_from_root_yaml_base_dict(base, max_cpu_id)
        )
    )

    figure_name = "%s%s" % (
        check_directory_exists(
            check_path_ends_with_slash(
                get_full_output_path_and_file(
                    base['output_dir'],
                    base['base_name'],
                    root_name=root_name
                )
            )
        ),
        "truth_vs_%s.pdf" % root_name if not invert_order else "%s_vs_truth.pdf" % root_name
    )

    # Make combined trigger file
    combined_repo = check_directory_exists(
        check_path_ends_with_slash(
            "%s%s%s" % (
                check_path_ends_with_slash(base['output_dir']),
                check_path_ends_with_slash(root_name),
                'combined/'
            )
        )
    )

    base_output_path = check_directory_exists(
        check_path_ends_with_slash(
            '%s%s' % (
                check_path_ends_with_slash(base['output_dir']),
                root_name,
            )
        )
    )

    comb_command = ['cat', base_output_path + '*.trigger', '>', combined_repo + root_name + '.trigger']

    if verbose:
        pretty_print_command(comb_command)
    if not print_only:
        os.system(get_list_as_str(comb_command))
        # Force some waiting in case file hasn't yet been created
        time.sleep(0.05)

    # Do the rest
    trigger_file = "%s%s%s%s%s" % (
        check_path_ends_with_slash(base['output_dir']),
        check_path_ends_with_slash(root_name),
        'combined/',
        root_name,
        '.trigger'
    )

    if truth_file is None:
        truth_file = "%s%s" % (
            base['input_file'].split('.fil')[0],
            '.txt'
        )

    # python $py_path/tools.py $fntrig $fncand --algo1 Amber$5 --algo2 Heimdall
    #   --mk_plot --dm_max 825. --figname $figname --title $title
    if not invert_order:
        command = ['python', '$ARTS_ANALYSIS_PATH/tools.py', trigger_file, truth_file,
                   '--algo1', root_name, '--algo2', 'Truth',
                   '--mk_plot', '--dm_max', max_dm,
                   '--figname', figure_name, '--title', "'Truth vs %s'" % root_name]
    else:
        command = ['python', '$ARTS_ANALYSIS_PATH/tools.py', truth_file, trigger_file,
                   '--algo1', 'Truth', '--algo2', root_name,
                   '--mk_plot', '--dm_max', max_dm,
                   '--figname', figure_name, '--title', "'%s vs Truth'" % root_name]

    if verbose:
        pretty_print_command(command)

    if not print_only:
        if detach:
            os.system(get_list_as_str(command) + ' &')
        else:
            os.system(get_list_as_str(command))
