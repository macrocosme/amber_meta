from __future__ import division, print_function
import os
import argparse
import subprocess
from .amber_options import AmberOptions
from .amber_configuration import AmberConfiguration
from .amber_utils import (
    get_root_name,
    get_full_output_path_and_file,
    get_scenario_file_from_root_yaml_base_dict,
    get_filterbank_header,
    get_nbatch,
    pretty_print_command,
    check_path_ends_with_slash,
    check_directory_exists,
    parse_scenario_to_dictionary,
    create_rfim_configuration_thresholds
)
from .amber_results import (
    read_amber_run_results,
    run_arts_analysis_triggers,
    run_arts_analysis_tools_against_ground_truth
)

AMBER_SETUP_PATH = '/home/vohl/AMBER_setup/'

"""
.. module:: amber_run.rst
   :platform: Unix, Windows
   :synopsis: Module to run amber

.. moduleauthor:: D. Vohl <vohl@astron.nl>


"""


def create_amber_command(base_name='scenario_3_partitions',
                         input_file='data/filterbank/file.fil',
                         scenario_file='$SOURCE_ROOT/scenario/3_dms_partitions/scenario_3_partitions_step1.sh',
                         config_path='$SOURCE_ROOT/install/scenario_3_partitions_step1/',
                         rfim=True,
                         rfim_mode='time_domain_sigma_cut',
                         rfim_threshold=None,
                         snr_mode='snr_mom_sigmacut',
                         input_data_mode='sigproc',
                         cpu_id=1,
                         snrmin=10,
                         output_dir='$OUTPUT_ROOT/results/',
                         verbose=True,
                         root_name=None):
    """Launch amber.

    Creates an amber launch command to be run with subprocess.

    Parameters
    ----------
    base_name : str
        Base name.
    input_file : str
        Intput filterbank file.
    scenario_file : str
        Scenario file (including path)
    config_path : str
        Path of configuration files
    rfim : bool
        Use RFI mitigation or not.
    rfim_mode : str
        RFI mitigation mode. Choices: [time_domain_sigma_cut | frequency_domain_sigma_cut]
    rfim_threshold : str
        Override rfim threshold value. Default: None
    snr_mode : str
        SNR mode. Choices: [snr_standard | snr_momad | snr_mom_sigmacut]
    input_data_mode : str
        Input data mode. Choices: [sigproc | data]
    cpu_id : int
        CPU id for process and GPU.
    snrmin : int
        Minimum SNR for outlier detection.
    output_dir : str
        Output directory.
    verbose : bool
        Print extra information at runtime.
    root_name : str
        Root name used for output.
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

    downsampling = (int(scenario_dict['downsampling'.upper()]) != 1)

    # Pin down amber's to cpu id 'cpu_id'
    command = ['taskset', '-c', str(cpu_id), 'amber']
    amber_options = AmberOptions(rfim=rfim,
                                 rfim_mode=rfim_mode,
                                 snr_mode=snr_mode,
                                 input_data_mode=input_data_mode,
                                 downsampling=downsampling)

    amber_configs = AmberConfiguration(rfim=rfim,
                                       rfim_mode=rfim_mode,
                                       downsampling=downsampling)

    # Check that output directory exists. If not, create it.
    check_directory_exists(output_dir)

    for option in amber_options.options:
        # First add the option with a dash (e.g. -opencl_platform)
        command.append('-' + option)

        # Then try to fill the input, if applicable
        if '_file' in option:
            command.append(config_path + option.split('_file')[0] + '.conf')
        elif option == 'downsampling':
            pass # Do not pass any option (TODO: fix naming rule issue with downsampling_configuration)
        elif option in ['time_domain_sigma_cut_steps', 'time_domain_sigma_cut_configuration', 'frequency_domain_sigma_cut_steps', 'frequency_domain_sigma_cut_configuration']:
            command.append(
                "%s%s%s%s" % (
                    config_path,
                    amber_configs.configurations[rfim_mode][option],
                    "" if rfim_threshold in [None, 'None'] else "%s%s" % ('_threshold_', rfim_threshold),
                    amber_configs.suffix
                )
            )
        elif option in ['downsampling_configuration', 'integration_steps', 'zapped_channels']:
            command.append(
                "%s%s%s" % (
                    config_path,
                    amber_configs.configurations[option],
                    amber_configs.suffix
                )
            )
        elif option == 'downsampling_factor':
            command.append(scenario_dict['DOWNSAMPLING'])
        elif option == 'threshold':
            command.append(str(snrmin))
        elif option == 'data':
            command.append(input_file)
        elif option == 'output':
            command.append(
                get_full_output_path_and_file(
                    output_dir,
                    base_name,
                    root_name=root_name if rfim_threshold is None else "%s_threshold_%s" % (root_name, rfim_threshold),
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


def run_amber_from_yaml_root(input_yaml_file, root='subband', rfim_threshold=None, verbose=False, print_only=True, detach_completely=True):
    """Run amber starting from a yaml root scenario file.

    Launches a amber scenario where each step is run as independent sub-processes.

    Parameters
    ----------
    input_yaml_file : str
        Input filename with .yaml or .yml extension.
    root : str
        Name of root scenario in input yaml.
    verbose : bool
        Print extra information at runtime.
    print_only : bool
        Only print command, do not launch them.
    detach_completely : bool
        If True, launch all processes and detach from them. Else, wait on last cpu.
    """
    assert input_yaml_file.split('.')[-1] in ['yaml', 'yml']
    base = parse_scenario_to_dictionary(input_yaml_file)[root]

    root_name = get_root_name(input_yaml_file)

    if verbose:
        print('ROOT_NAME', root_name)

    if verbose:
        print(base)

    if rfim_threshold is None:
        if 'rfim_threshold' in base:
            if base['rfim_threshold'] != None:
                #check_file_exists(base[])
                # Should check if the file already exists...
                create_rfim_configuration_threshold_from_yaml_root(input_yaml_file,
                                                                   root=root,
                                                                   threshold=base['rfim_threshold'],
                                                                   verbose=verbose,
                                                                   print_only=print_only)
    else:
        create_rfim_configuration_threshold_from_yaml_root(input_yaml_file,
                                                           root=root,
                                                           threshold=rfim_threshold,
                                                           verbose=verbose,
                                                           print_only=print_only)

    for cpu_id in range(base['n_cpu']):
        command = create_amber_command(
            base_name=base['base_name'],
            input_file=base['input_file'],
            scenario_file=get_scenario_file_from_root_yaml_base_dict(base, cpu_id),
            config_path='%s%s' % (
                check_path_ends_with_slash(base['base_config_path']),
                check_path_ends_with_slash(base['config_repositories'][cpu_id]),
            ),
            rfim=base['rfim'],
            rfim_mode=base['rfim_mode'],
            rfim_threshold=base['rfim_threshold'] if rfim_threshold is None else rfim_threshold,
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
            if detach_completely:
                # Launch amber, and detach from the process so it runs by itself
                subprocess.Popen(command, preexec_fn=os.setpgrp)
            else:
                if cpu_id != base['n_cpu']-1:
                    subprocess.Popen(command, preexec_fn=os.setpgrp)
                else:
                    subprocess.call(command)

def run_amber_from_yaml_root_override_threshold(input_basename='yaml/root/root',
                                                root='subband',
                                                threshold='2.00',
                                                verbose=False,
                                                print_only=False):
    """Run amber from a yaml root file and override threshold for RFIm

    input_basename : str
        Default: 'yaml/root/root'
    root : str
        Default: 'subband',
    threshold : str
        Default: '2.00'
    verbose : bool
        Print extra information at runtime. Default: False.
    print_only : bool
        Only print command, do not launch them. Default: False.
    """
    run_amber_from_yaml_root(
        '%s_%s.yaml' % (
            input_basename,
            threshold
        ),
        root=root,
        verbose=verbose,
        print_only=print_only,
        detach_completely=True
    )

def run_amber_from_yaml_root_override_thresholds(input_basename='yaml/root/root',
                                                 root='subband',
                                                 thresholds = ['2.00', '2.50', '3.00', '3.50', '4.00', '4.50', '5.00'],
                                                 verbose=False,
                                                 print_only=False):
    """Run amber from a yaml root file and for multiple overriden threshold for RFIm

    input_basename : str
        Default: 'yaml/root/root'
    root : str
        Default: 'subband',
    thresholds : list
        Default: ['2.00', '2.50', '3.00', '3.50', '4.00', '4.50', '5.00']
    verbose : bool
        Print extra information at runtime. Default: False.
    print_only : bool
        Only print command, do not launch them. Default: False.
    """
    for threshold in thresholds:
        run_amber_from_yaml_root(
            '%s.yaml' % (
                input_basename
            ),
            rfim_threshold=threshold,
            root=root,
            verbose=verbose,
            print_only=print_only,
            detach_completely=False
        )

def create_rfim_configuration_threshold_from_yaml_root(input_yaml_file,
                                                        root='subband',
                                                        threshold = '2.50',
                                                        verbose=False,
                                                        print_only=False):
    """Create RFIm configuration file starting from with a yaml root

    Parameters
    ----------
    input_yaml_file : str
        Input root yaml file
    root : str
        Root value of the yaml file. Default: 'subband'
    threshold : list
        New threshold file to be generated. Default: '2.50',
    verbose : bool
        Print extra information at runtime. Default: False.
    print_only : bool
        Only print command, do not launch them. Default: False.
    """
    assert input_yaml_file.split('.')[-1] in ['yaml', 'yml']
    base = parse_scenario_to_dictionary(input_yaml_file)[root]

    root_name = get_root_name(input_yaml_file)

    for cpu_id in range(base['n_cpu']):
        create_rfim_configuration_thresholds(
            config_path='%s%s' % (
                check_path_ends_with_slash(base['base_config_path']),
                check_path_ends_with_slash(base['config_repositories'][cpu_id]),
            ),
            rfim_mode=base['rfim_mode'],
            original_threshold='2.50', # This is a bit dumb, but will work for now...
            new_threshold=threshold,
            duplicate=True,
            verbose=verbose,
            print_only=print_only
        )

def create_rfim_configuration_thresholds_from_yaml_root(input_yaml_file,
                                                        root='subband',
                                                        thresholds = ['2.00', '2.50', '3.00', '3.50', '4.00', '4.50', '5.00'],
                                                        verbose=False,
                                                        print_only=False):
    """Create RFIm configuration files starting from with a yaml root

    Parameters
    ----------
    input_yaml_file : str
        Input root yaml file
    root : str
        Root value of the yaml file. Default: 'subband'
    thresholds : list
        Thresholds files to be generated. Default: ['2.00', '2.50', '3.00', '3.50', '4.00', '4.50', '5.00'],
    verbose : bool
        Print extra information at runtime. Default: False.
    print_only : bool
        Only print command, do not launch them. Default: False.
    """
    for threshold in thresholds:
        create_rfim_configuration_threshold_from_yaml_root(input_yaml_file,
                                                           root=root,
                                                           threshold=threshold,
                                                           verbose=verbose,
                                                           print_only=print_only)

def make_plots_for_rfim_thresholds(input_basename='yaml/root/root',
                                   thresholds=['2.00', '2.50', '3.00', '3.50', '4.00', '4.50', '5.00'],
                                   triggers=True,
                                   tools=True,
                                   detach=True,
                                   verbose=True,
                                   invert_order=False,
                                   print_only=True):
    for threshold in thresholds:
        if triggers:
            run_arts_analysis_triggers(
                '%s.yaml' % input_basename,
                threshold=threshold,
                detach=detach,
                verbose=verbose,
                print_only=print_only
            )
        if tools:
            run_arts_analysis_tools_against_ground_truth(
                '%s.yaml' % input_basename,
                threshold=threshold,
                detach=detach,
                verbose=verbose,
                invert_order=invert_order,
                print_only=print_only
            )

def test_amber_run(input_file='data/dm100.0_nfrb500_1536_sec_20190214-1542.fil',
                   n_cpu=3,
                   base_name='tuning_halfrate_3GPU_goodcentralfreq',
                   base_scenario_path='/home/vohl/software/AMBER/scenario/',
                   scenario_files=['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
                   snrmin=8,
                   base_config_path='$SOURCE_ROOT/configuration/',
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

    Parameters
    ----------
    amber_mode : str
    input_file : str
    n_cpu : int
    base_name : str
    base_scenario_path : str
    scenario_files : list
    snrmin : int
    base_config_path : str
    config_repositories : list
    rfim : bool
    rfim_mode : str
    snr_mode : str
    input_data_mode : str
    verbose : bool
        Print extra information at runtime.
    print_only : bool
        Only print the command without launching it.
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


def get_amber_run_results_from_root_yaml(input_yaml_file, root='subband', verbose=False):
    """Run amber starting from a yaml root scenario file.

    Launches a amber scenario where each step is run as independent sub-processes.

    Parameters
    ----------
    input_yaml_file : str
        Accepted format are .yaml and .yml
    root : str
        Name of root scenario in input yaml.
    verbose : bool
        Print extra information at runtime.
    """
    assert input_yaml_file.split('.')[-1] in ['yaml', 'yml']
    base = parse_scenario_to_dictionary(input_yaml_file)[root]
    root_name = get_root_name(input_yaml_file)

    if verbose:
        print(base)

    full_output_dir = check_path_ends_with_slash(base['output_dir']) + root_name

    return read_amber_run_results(full_output_dir, verbose=verbose)


def tune_amber(scenario_file='/home/vohl/software/AMBER/scenario/tuning_step1.sh',
               config_path='/home/vohl/software/AMBER/configuration/tuning_step1',
               verbose=True,
               print_only=True):
    """Tune amber.

    Tune amber based on a scenario file. The output is save to config_path.

    Parameters
    ----------
    scenario_file : str
    config_path : str
    """
    # Format input to correspond to behaviour we want
    config_path = check_path_ends_with_slash(config_path)

    # Define command
    command = [AMBER_SETUP_PATH + 'amber.sh', 'tune', scenario_file, config_path]

    if verbose:
        pretty_print_command(command)

    if not print_only:
        # Launch amber tuning, and detach from the process so it runs by itself
        subprocess.Popen(command, preexec_fn=os.setpgrp)
        # os.system([for c in command print (c),][0] + '&' )


def test_tune(base_scenario_path='/home/vohl/software/AMBER/scenario/',
              base_name='tuning_halfrate_3GPU_goodcentralfreq',
              scenario_files=['tuning_1.sh', 'tuning_2.sh', 'tuning_3.sh'],
              config_path='/home/vohl/software/AMBER/configuration/',
              verbose=True,
              print_only=True):
    """Test tuning amber.

    Launch tune_amber for three scenarios.

    Parameters
    base_scenario_path : str
    base_name : str
    scenario_files : list
    config_path : str
    """

    base_scenario_path = check_path_ends_with_slash(base_scenario_path)
    i = 1
    for file in scenario_files:
        input_file = "%s%s%s%s%s" % (
            base_scenario_path,
            base_name,
            '/tuning_',
            i,
            '.sh'
        )
        output_dir = config_path + base_name + '_step' + str(i)

        output_dir = check_directory_exists(output_dir)

        tune_amber(input_file, output_dir, verbose=verbose, print_only=print_only)
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
