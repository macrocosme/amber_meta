from __future__ import division, print_function
import os
import argparse
import subprocess
from .amber_options import AmberOptions
from .amber_utils import (
    get_full_output_path_and_file,
    get_filterbank_header,
    get_nbatch,
    pretty_print_command,
    check_path_ends_with_slash,
    check_directory_exists,
    parse_scenario_to_dictionary
)
from .amber_results import read_amber_run_results

AMBER_SETUP_PATH = '/home/vohl/AMBER_setup/'

"""
.. module:: amber_run.rst
   :platform: Unix, Windows
   :synopsis: Module to run amber

.. moduleauthor:: D. Vohl <vohl@astron.nl>


"""


def create_amber_command(base_name='scenario_3_partitions',
                         input_file='/data1/output/snr_tests_liam/20190214/dm100.0_nfrb500_1536_sec_20190214-1542.fil',
                         scenario_file='/home/vohl/software/AMBER/scenario/3_dms_partitions/12500/scenario_3_partitions_step1_12500.sh',
                         config_path='/home/vohl/software/AMBER/install/scenario_3_partitions_step1_12500/',
                         rfim=True,
                         rfim_mode='time_domain_sigma_cut',
                         snr_mode='snr_mom_sigmacut',
                         input_data_mode='sigproc',
                         cpu_id=1,
                         snrmin=10,
                         output_dir='/data1/vohl/results/rfim/',
                         verbose=True,
                         root_name=None):
    """Launch amber.

    Creates an amber launch command to be run with subprocess.

    Args:
        base_name(string):
        input_file(string):
        scenario_file(string):
        config_path(string):
        rfim: boolean
        rfim_mode(string):
        snr_mode(string):
        input_data_mode(string):
        cpu_id(integer):
        snrmin(integer):
        output_dir(string):
        root_name(string):
    """

    if verbose:
        print("Scenario:", scenario_file)
        print()

    # Get scenario
    scenario_dict = parse_scenario_to_dictionary(scenario_file)

    # Format input to correspond to behaviour we want
    config_path = check_path_ends_with_slash(config_path)

    # COLLECT INFO FROM FILTERBANK
    header, header_size = get_filterbank_header(input_file, verbose=verbose)
    nbatch = get_nbatch(input_file, header, header_size, int(scenario_dict['SAMPLES']), verbose=verbose)

    # Get amber's INSTALL_ROOT variable state
    conf_dir_base = os.environ['INSTALL_ROOT']

    # Pin down amber's to cpu id 'cpu_id'
    command = ['taskset', '-c', str(cpu_id), 'amber']
    amber_options = AmberOptions(rfim=rfim,
                                 rfim_mode=rfim_mode,
                                 snr_mode=snr_mode,
                                 input_data_mode=input_data_mode,
                                 downsampling=(int(scenario_dict['downsampling'.upper()]) != 1))

    # Check that output directory exists. If not, create it.
    check_directory_exists(output_dir)

    for option in amber_options.options:
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
        elif option == 'downsampling_factor':
            command.append(scenario_dict['DOWNSAMPLING'])
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
                get_full_output_path_and_file(
                    output_dir,
                    base_name,
                    root_name=root_name,
                    cpu_id=cpu_id
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


def run_amber_from_yaml_root(input_file, root='subband', verbose=False, print_only=True):
    """Run amber starting from a yaml root scenario file.

    Launches a amber scenario where each step is run as independent sub-processes.

    Args:
        input_file(string): Input filename with .yaml or .yml extension
        root(string): (Name of root scenario in input yaml.)
        verbose(bool)
    """
    assert input_file.split('.')[-1] in ['yaml', 'yml']
    base = parse_scenario_to_dictionary(input_file)[root]

    root_name = input_file.split('.')[-2].split('/')[-1]
    if verbose:
        print('ROOT_NAME', root_name)

    if verbose:
        print(base)

    for cpu_id in range(base['n_cpu']):
        command = create_amber_command(
            base_name=base['base_name'],
            input_file=base['input_file'],
            scenario_file='%s%s%s' % (
                check_path_ends_with_slash(base['base_scenario_path']),
                check_path_ends_with_slash(base['base_name']),
                base['scenario_files'][cpu_id],
            ),
            config_path='%s%s' % (
                check_path_ends_with_slash(base['base_config_path']),
                check_path_ends_with_slash(base['config_repositories'][cpu_id]),
            ),
            rfim=base['rfim'],
            rfim_mode=base['rfim_mode'],
            snr_mode=base['snr_mode'],
            input_data_mode=base['input_data_mode'],
            cpu_id=cpu_id,
            snrmin=base['snrmin'],
            output_dir=base['output_dir'],
            root_name=root_name
        )

        if verbose:
            pretty_print_command(command)

        if not print_only:
            # Launch amber, and detach from the process so it runs by itself
            subprocess.Popen(command, preexec_fn=os.setpgrp)


def test_amber_run(input_file='/data1/output/snr_tests_liam/20190214/dm100.0_nfrb500_1536_sec_20190214-1542.fil',
                   n_cpu=3,
                   base_name='tuning_halfrate_3GPU_goodcentralfreq',
                   base_scenario_path='/home/vohl/software/AMBER/scenario/',
                   scenario_files=['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
                   snrmin=8,
                   base_config_path='/home/vohl/software/AMBER/configuration/',
                   config_repositories=[
                       'tuning_halfrate_3GPU_goodcentralfreq_step1',
                       'tuning_halfrate_3GPU_goodcentralfreq_step2',
                       'tuning_halfrate_3GPU_goodcentralfreq_step3'
                   ],
                   rfim=True,
                   rfim_mode='time_domain_sigma_cut',
                   snr_mode='snr_mom_sigmacut',
                   input_data_mode='sigproc',
                   verbose=True,
                   print_only=False):
    """Test amber.

    Creates three amber jobs.

    Args:
        amber_mode(string):
        input_file(string):
        n_cpu(integer):
        base_name(string):
        base_scenario_path(string):
        scenario_files: list(strings)
        snrmin(integer):
        base_config_path(string):
        config_repositories: list(strings)
        rfim: boolean
        rfim_mode(string):
        snr_mode(string):
        input_data_mode(string):
        verbose: boolean
        print_only: boolean
    """
    for cpu_id in range(n_cpu):
        command = create_amber_command(
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
            rfim=rfim,
            rfim_mode=rfim_mode,
            snr_mode=snr_mode,
            input_data_mode=input_data_mode,
            cpu_id=cpu_id,
            snrmin=snrmin
        )

        if verbose:
            pretty_print_command(command)

        if not print_only:
            # Launch amber, and detach from the process so it runs by itself
            subprocess.Popen(command, preexec_fn=os.setpgrp)


def get_amber_run_results_from_root_yaml(input_file, root='subband', verbose=False):
    """Run amber starting from a yaml root scenario file.

    Launches a amber scenario where each step is run as independent sub-processes.

    Args:
        input_file(string): Accepted format are .yaml and .yml
        root(string): Name of root scenario in input yaml.
        verbose(boolean):
    """
    assert input_file.split('.')[-1] in ['yaml', 'yml']
    base = parse_scenario_to_dictionary(input_file)[root]

    if verbose:
        print(base)

    return read_amber_run_results(base['output_dir'], verbose=verbose)


def tune_amber(scenario_file='/home/vohl/software/AMBER/scenario/tuning_halfrate_3GPU_goodcentralfreq/tuning_1.sh',
               config_path='/home/vohl/software/AMBER/configuration/tuning_halfrate_3GPU_goodcentralfreq_step1'):
    """Tune amber.

    Tune amber based on a scenario file. The output is save to config_path.

    Args:
        scenario_file(string):
        config_path(string):
    """
    # Format input to correspond to behaviour we want
    config_path = check_path_ends_with_slash(config_path)

    # Define command
    command = [AMBER_SETUP_PATH + 'amber.sh', 'tune', scenario_file, config_path]

    # Launch amber tuning, and detach from the process so it runs by itself
    subprocess.Popen(command, preexec_fn=os.setpgrp)
    # os.system([for c in command print (c),][0] + '&' )


def test_tune(base_scenario_path='/home/vohl/software/AMBER/scenario/tuning_halfrate_3GPU_goodcentralfreq/',
              base_name='tuning_halfrate_3GPU_goodcentralfreq',
              scenario_files=['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
              config_path='/home/vohl/software/AMBER/configuration/'):
    """Test tuning amber.

    Launch tune_amber for three scenarios.

    Args:
        base_scenario_path(string):
        base_name(string):
        scenario_files(list):
        config_path(string):
    """

    base_scenario_path = check_path_ends_with_slash(base_scenario_path)
    i = 1
    for file in scenario_files:
        input_file = base_scenario_path + 'tuning_' + str(i) + '.sh'
        output_dir = config_path + base_name + '_step' + str(i)

        print(i, input_file, output_dir)
        print()

        output_dir = check_directory_exists(output_dir)

        tune_amber(input_file, output_dir)
        i += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',
                        help="Print amber commands",
                        type=bool,
                        default=True)
    parser.add_argument('--print_only',
                        help="If True, only prints amber commands. If False, also launch the jobs.",
                        type=bool,
                        default=False)
    args = parser.parse_args()

    test_amber_run(verbose=args.verbose, print_only=args.print_only)
