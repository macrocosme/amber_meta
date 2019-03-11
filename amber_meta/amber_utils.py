from __future__ import division, print_function
import sys
from os import path, listdir, walk, makedirs
from os.path import isfile, join
import subprocess
import yaml
import fileinput
try:
    from filterbank import read_header as filterbank__read_header
    from sigproc import samples_per_file as sigproc__samples_per_file
except:
    pass
from .amber_configuration import AmberConfiguration

"""
.. module:: amber_utils
   :platform: Unix, Windows
   :synopsis: Module including utility functions

.. moduleauthor:: D. Vohl <vohl@astron.nl>


"""

def get_full_output_path_and_file(output_dir, base_name, root_name=None, cpu_id = 0):
    """Get full output path and file name

    Parameters
    ----------
    output_dir : str
    base_name : str
    root_name : str

    Returns
    -------
    path_and_file : str
    """
    return "%s%s%s%s" % (
        check_directory_exists(
            check_path_ends_with_slash(
                '%s%s' % (
                    check_path_ends_with_slash(output_dir),
                    root_name if root_name != None else base_name,
                )
            )
        ),
        root_name if root_name != None else base_name,
        '_step_',
        str(cpu_id + 1)
    )

def get_max_dm(scenario_dict):
    """Computes maximum dm.

    Parameters
    ----------
    scenario_dict : dict
        Scenario dictionary outputed by
        amber_utils.parse_scenario_to_dictionary()

    Returns
    -------
    max_dm : float
        Maximum DM
    """
    return scenario_dict['SUBBANDING_DM_FIRST'] + \
           scenario_dict['SUBBANDING_DM_STEP'] * scenario_dict['SUBBANDING_DMS']

def get_filterbank_header(input_file, verbose=False):
    """Get header and header_size from filterbank

    Parameters
    ----------
    input_file  : str

    Returns
    -------
    header : dict
        filterbank.read_header.header
    header_size : int
        filterbank.read_header.header_size
    """
    header, header_size = filterbank__read_header(input_file)
    if verbose:
        print ('header', header)
        print ('header_size', header_size)
        print ()
    return header, header_size

def get_nbatch(input_file, header, header_size, samples, verbose=False):
    """Get number of batches (nbatch) available in filterbank

    Parameters
    ----------
    input_file  : str
    header : dict
        filterbank.read_header.header
    header_size : int
        filterbank.read_header.header_size

    returns
    -------
    nbatch : int
    """
    if verbose:
        print ('NBATCH:', sigproc__samples_per_file(input_file, header, header_size)//samples)
        print ()

    nbatch = sigproc__samples_per_file(input_file, header, header_size)//samples
    return nbatch

def pretty_print_command (command):
    """Pretty print an amber command.

    Prints each element of the 'command' list as a string.

    Parameters
    ----------
    command : list
    """
    c = ''
    for v in command:
        c += '%s ' % (v)
    print ('Command:', c)
    print ()

def check_path_ends_with_slash(path):
    """Check if directory (string) ends with a slash.

    If directory does not end with a slash, add one at the end.

    Parameters
    ----------
    directory : str

    Returns
    -------
    directory : str
    """
    if path[-1] != '/':
        path = path + '/'
    return path

def check_directory_exists(directory):
    """Check if directory (string) ends with a slash.

    If directory does not end with a slash, add one at the end.

    Parameters
    ----------
    directory  : str

    Returns
    -------
    directory  : str
    """
    if not path.exists(directory):
        makedirs(directory)
    return directory

def list_files_with_paths_recursively(my_path):
    """Recursively list files in my_path

    Recursively list files in my_path and returns the list in
    the form of ['path/to/file/myfile.extension', '...']

    Parameters
    ----------
    my_path  : str
    """
    my_files = []
    for (dirpath, dirnames, filenames) in walk(my_path):
        if dirpath[-1] != '/':
            for f in filenames:
                my_files.append(dirpath + '/' + f)
    return my_files

def list_files_in_current_path(path):
    """Returns files in the current folder only

    Parameters
    ----------
    path  : str

    Returns
    -------
    files : list
    """
    return [ f for f in listdir(path) if isfile(join(path,f)) ]

def duplicate_config_file(config_path, base_filename, copy_filename):
    """Duplicate a configuration file using copu_filename as output nameself.

    Parameters
    ----------
    config_path : str
        Path to configuration files
    base_filename : str
        Filename of file to be copied
    copy_filename : str
        Filename of duplicate
    """
    base_file = "%s%s" % (
        check_path_ends_with_slash(config_path),
        base_filename
    )

    copy_file = "%s%s" % (
        check_path_ends_with_slash(config_path),
        copy_filename
    )
    subprocess.Popen(['cp', base_file, copy_file])

def find_replace(filename, text_to_search, text_to_replace, inplace=True):
    """Find text_to_search in filename and replace it with text_to_replace

    Parameters
    ----------
    filename : str
        Filename of input file to modify
    text_to_search : str
        Text string to be searched in intput file
    text_to_replace : str
        Text string to replace text_to_search with in intput file
    inplace : bool
        Default: True
    """
    i = 0
    for line in fileinput.input(filename, inplace=inplace):
        sys.stdout.write(line.replace(text_to_search, text_to_replace))

def create_rfim_configuration_thresholds(config_path,
                                         rfim_mode='time_domain_sigma_cut',
                                         original_threshold='2.50',
                                         new_threshold='1.00',
                                         duplicate=True):
    """Create a new RFIm configuration file for specified threshold

    Parameters
    ----------
    config_path : str
        Path to configuration files
    rfim_mode : str (optional)
        RFIm mode of operation. Default: 'time_domain_sigma_cut'
    original_threshold : str (optional)
        Threshold listed in base config file. Default: 2.50
    new_threshold : str (optional)
        New threshold. Default: 1.00
    duplicate : bool
        When True, make copies of the base configuration files adding the threshold in new filename
    """
    confs = AmberConfiguration(rfim=True, rfim_mode='time_domain_sigma_cut')

    for option in confs.rfim_options[rfim_mode]:
        copy_filename = "%s%s%s%s" % (
            confs.configurations[rfim_mode][option],
            '_threshold_',
            new_threshold,
            confs.suffix
        )

        if duplicate:
            duplicate_config_file(
                config_path,
                base_filename = "%s%s" % (
                    confs.configurations[rfim_mode][option],
                    confs.suffix
                ),
                copy_filename = copy_filename,
            )

        find_replace(
            filename = "%s%s" % (
                check_path_ends_with_slash(config_path),
                copy_filename
            ),
            text_to_search = original_threshold,
            text_to_replace = new_threshold
        )

def parse_scenario_to_dictionary(scenario_file):
    """Parse an amber scenario file to a python dictionary

    Accepted file extensions: [.yaml | .yml], and [.sh] as described in
    https://github.com/AA-ALERT/AMBER_setup/blob/development/examples/scenario.sh

    Parameters
    ----------
    scenario_file : str
        amber scenario file (including path)

    Returns
    -------
    scenario_dict : dict
        parsed dictionary
    """
    if scenario_file.split('.')[-1] == 'sh':
        scenario_dict = parse_sh_scenario_to_dictionary(scenario_file)
    elif scenario_file.split('.')[-1] in ['yaml', 'yml']:
        scenario_dict = parse_yaml_scenario_to_dictionary(scenario_file)
    else:
        scenario_dict = parse_sh_scenario_to_dictionary(scenario_file)

    return scenario_dict

def parse_sh_scenario_to_dictionary(scenario_file):
    """Parse an amber scenario file to a python dictionary

    File extension expected is '.sh' as described in
    https://github.com/AA-ALERT/AMBER_setup/blob/development/examples/scenario.sh

    Note that the extension is not required per se,
    but the file structure should follow a shell variable structure.

    Parameters
    ----------
    scenario_file : str
        amber scenario file (including path)

    Returns
    -------
    scenario_dict : dict
        parsed dictionary
    """
    scenario_dict = {}
    with open(scenario_file, 'r') as f:
        for line in f:
            if line[0] not in ['!', '#', '\n']:
                param, value = line.replace('\n', '').replace('"', '').split('=')
                scenario_dict[param] = value
    return scenario_dict

def parse_yaml_scenario_to_dictionary(scenario_file, scenario_name=None):
    """Parse an amber scenario file (yaml) to a python dictionary

    Parameters
    ----------
    scenario_file : str
        amber scenario file in yaml format (including path)

    Returns
    -------
    scenario_dict : dict
        parsed dictionary
    """
    scenario_dict = {}

    with file(scenario_file, 'r') as f:
        scenario_dict = yaml.load(f)

    if scenario_name != None:
        # e.g. scenario_dict['subband'] for multilayer yaml scenario file
        return scenario_dict[scenario_name]
    else:
        return scenario_dict
