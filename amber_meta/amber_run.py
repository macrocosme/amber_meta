from __future__ import division, print_function
import os
import argparse
import subprocess
from filterbank import read_header as filterbank__read_header
from sigproc import samples_per_file as sigproc__samples_per_file
from amber_options import AmberOptions
from amber_utils import (
    pretty_print_command,
    check_path_ends_with_slash,
    check_directory_exists,
    parse_scenario_to_dictionary
)

AMBER_SETUP_PATH = '/home/vohl/AMBER_setup/'

def create_amber_command(amber_mode='snr_mom_sigmacut_tdsc',
                 base_name='scenario_3_partitions',
                 input_file='/data1/output/snr_tests_liam/20190214/dm100.0_nfrb500_1536_sec_20190214-1542.fil',
                 scenario_file='/home/vohl/software/AMBER/scenario/3_dms_partitions/12500/scenario_3_partitions_step1_12500.sh',
                 config_path='/home/vohl/software/AMBER/install/scenario_3_partitions_step1_12500/',
                 cpu_id=1,
                 snrmin=10,
                 output_dir='/home/vohl/data/',
                 verbose=True):
    '''Launch amber.

    Creates an amber launch command to be run with subprocess.

    Parameters
    ----------
        amber_mode: ['snr_mom_sigmacut_tdsc']
        base_name: string
        input_file: string
        scenario_file: string
        config_path: string
        cpu_id: integer
        snrmin: integer
        output_dir: string

    Returns
    -------
        nothing.
    '''

    # print ("Scenario:", scenario_file)
    # Get scenario
    scenario_dict = parse_scenario_to_dictionary(scenario_file)

    # Format input to correspond to behaviour we want
    config_path = check_path_ends_with_slash(config_path)

    # COLLECT INFO FROM FILTERBANK
    header, header_size = filterbank__read_header(input_file)
    nbatch = sigproc__samples_per_file(input_file, header, header_size)//1000

    # Get amber's INSTALL_ROOT variable state
    conf_dir_base = os.environ['INSTALL_ROOT']

    # Pin down amber's to cpu id 'cpu_id'
    command = ['taskset', '-c', str(cpu_id),
                    'amber']

    try:
        scenario_dict['downsampling']
    except:
        amber_mode += '_no_downsampling'
    amber_options = AmberOptions()
    for option in amber_options.options[amber_mode]:
        # First add the option with a dash (e.g. -opencl_platform)
        command.append('-' + option)

        # Then try to fill the input, if applicable
        if '_file' in option:
            command.append(config_path + option.split('_file')[0] + '.conf')
        elif option == 'time_domain_sigma_cut_steps':
            command.append(config_path + 'tdsc_steps.conf')
        elif option == 'time_domain_sigma_cut_configuration':
            command.append(config_path + 'tdsc.conf')
        elif option == 'downsampling_configuration':
            command.append(config_path + 'downsampling.conf')
        elif option == 'integration_steps':
            command.append(config_path + 'integration_steps.conf')
        elif option == 'zapped_channels':
            command.append(config_path + 'zapped_channels.conf')
        elif option == 'threshold':
	        command.append(str(snrmin))
        elif option == 'data':
            command.append(input_file)
        elif option == 'output':
            command.append(
                check_path_ends_with_slash(
                    check_directory_exists(
                        "%s%s%s%s" % (
                            output_dir,
                            base_name,
                            '_step_',
                            str(cpu_id+1)
                        )
                    )
                )
            )
        elif option == 'header':
            command.append(str(header_size))
        elif option == 'batches':
            command.append(str(nbatch))
        else:
            try:
                command.append(scenario_dict[option.upper()])
            except KeyError:
                # This option doesn't require any input
                pass

    return command

def test_amber_run(amber_mode='snr_mom_sigmacut_tdsc',
                   input_file='/data1/output/snr_tests_liam/20190214/dm100.0_nfrb500_1536_sec_20190214-1542.fil',
                   n_cpu=3,
                   base_name='tuning_halfrate_3GPU_goodcentralfreq',
                   base_scenario_path='/home/vohl/software/AMBER/scenario/',
                   scenario_files = ['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
                   snrmin=8,
                   base_config_path='/home/vohl/software/AMBER/configuration/',
                   config_repositories=[
                        'tuning_halfrate_3GPU_goodcentralfreq_step1',
                        'tuning_halfrate_3GPU_goodcentralfreq_step2',
                        'tuning_halfrate_3GPU_goodcentralfreq_step3'],
                   verbose=True,
                   print_only=False):
    '''Test amber.

    Creates three amber jobs.

    Parameters
    ----------
        amber_mode: string
        input_file: string
        n_cpu: integer
        base_name: string
        base_scenario_path: string
        scenario_files: list(strings)
        snrmin: integer
        base_config_path: string
        config_repositories: list(strings)

    Returns
    -------
        nothing.
    '''
    for cpu_id in range(n_cpu):
        command = create_amber_command (
            amber_mode='snr_mom_sigmacut_tdsc',
            base_name=base_name,
            input_file=input_file,
            scenario_file='%s%s%s' % (
               check_path_ends_with_slash(base_scenario_path),
               check_path_ends_with_slash(base_name),
               scenario_files[cpu_id],
            ),
            config_path='%s%s' % (
                check_path_ends_with_slash(base_config_path),
                check_path_ends_with_slash(config_repositories[cpu_id]),
            ),
            cpu_id=cpu_id,
            snrmin=snrmin
        )

        if verbose:
            pretty_print_command(command)

        if not print_only:
            # Launch amber, and detach from the process so it runs by itself
            subprocess.Popen(command, preexec_fn=os.setpgrp)

def tune_amber(scenario_file='/home/vohl/software/AMBER/scenario/tuning_halfrate_3GPU_goodcentralfreq/tuning_1.sh',
               config_path='/home/vohl/software/AMBER/configuration/tuning_halfrate_3GPU_goodcentralfreq_step1'):
    '''Tune amber.

    Tune amber based on a scenario file. The output is save to config_path.

    Parameters
    ----------
        scenario_file: string
        config_path: string

    Returns
    -------
        nothing.
    '''
    # Format input to correspond to behaviour we want
    config_path = check_path_ends_with_slash(config_path)

    # Define command
    command = [AMBER_SETUP_PATH + 'amber.sh', 'tune', scenario_file, config_path]

    # Launch amber tuning, and detach from the process so it runs by itself
    subprocess.Popen(command, preexec_fn=os.setpgrp)
    # os.system([for c in command print (c),][0] + '&' )

def test_tune(base_scenario_path='/home/vohl/software/AMBER/scenario/tuning_halfrate_3GPU_goodcentralfreq/',
              base_name='tuning_halfrate_3GPU_goodcentralfreq',
              scenario_files = ['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
              config_path='/home/vohl/software/AMBER/configuration/'):
    '''Test tuning amber.

    Launch tune_amber for three scenarios.

    Parameters
    ----------
        base_scenario_path: string
        base_name: string
        scenario_files: list(strings)
        config_path: string

    Returns
    -------
        nothing.
    '''

    base_scenario_path=check_path_ends_with_slash(base_scenario_path)
    i = 1
    for file in scenario_files:
        input_file = base_scenario_path+'tuning_'+str(i)+'.sh'
        output_dir = config_path+base_name+'_step'+str(i)

        print (i, input_file, output_dir)
        print ()

        output_dir = check_directory_exists(output_dir)

        tune_amber(input_file, output_dir)
        i+=1

def check_defaults(**kwargs):
    '''Check for default values to be present. If not, set default values.

    [Long description, optional]

    Parameters
    ----------
        **kwargs: key word arguments

    Returns
    -------
        kwargs: key word arguments
    '''
    if kwargs['some_key'] == None:
        kwargs['some_key'] = ''

    return kwargs

if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--input_dir', help="Repository of input files")
    #
    # args = parser.parse_args()
    # kwargs = check_defaults(**vars(args))

    test_amber_run(verbose=True, print_only=False)
