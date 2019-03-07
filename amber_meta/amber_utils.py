from __future__ import division, print_function
import os
import yaml
from filterbank import read_header as filterbank__read_header
from sigproc import samples_per_file as sigproc__samples_per_file
from os import path, listdir, walk
from os.path import isfile, join

def get_max_dm(scenario_dict):
    '''Check if directory (string) ends with a slash.

    If directory does not end with a slash, add one at the end.

    Parameters
    ----------
        directory: string

    Returns
    -------
        directory: string
    '''
    return scenario_dict['SUBBANDING_DM_FIRST'] + \
           scenario_dict['SUBBANDING_DM_STEP'] * scenario_dict['SUBBANDING_DMS']

def get_filterbank_header(input_file):
    '''Get header and header_size from filterbank

    Parameters
    ----------
        input_file: string

    Returns
    -------
        header: filterbank.read_header.header (dict)
        header_size: filterbank.read_header.header_size (int)
    '''
    header, header_size = filterbank__read_header(input_file)
    return header, header_size

def get_nbatch(input_file, header, header_size):
    '''Get number of batches (nbatch) available in filterbank

    Parameters
    ----------
        input_file: string
        header: filterbank.read_header.header (dict)
        header_size: filterbank.read_header.header_size (int)

    Returns
    -------
        nbatch: int
    '''
    nbatch = sigproc__samples_per_file(input_file, header, header_size)//1000
    return nbatch

def pretty_print_command (command):
    '''Pretty print an amber command.

    Prints each element of the 'command' list as a string.

    Parameters
    ----------
        command: list

    Returns
    -------
        Nothing
    '''
    c = ''
    for v in command:
        c += '%s ' % (v)
    print ('Command:', c)
    print ()

def check_path_ends_with_slash(path):
    '''Check if directory (string) ends with a slash.

    If directory does not end with a slash, add one at the end.

    Parameters
    ----------
        directory: string

    Returns
    -------
        directory: string
    '''
    if path[-1] != '/':
        path = path + '/'
    return path

def check_directory_exists(directory):
    '''Check if directory (string) ends with a slash.

    If directory does not end with a slash, add one at the end.

    Parameters
    ----------
        directory: string

    Returns
    -------
        directory: string
    '''
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def list_files_with_paths_recursively(my_path):
    """ Recursively list files in my_path and returns the list in the form of ['path/to/file/myfile.extension', '...'] """
    my_files = []
    for (dirpath, dirnames, filenames) in walk(my_path):
        if dirpath[-1] != '/':
            for f in filenames:
                my_files.append(dirpath + '/' + f)
    return my_files

def list_files_in_current_path(path):
    """ Returns files in the current folder only """
    return [ f for f in listdir(path) if isfile(join(path,f)) ]

def get_Files(path):
    return [ f for f in listdir(path) if isfile(join(path,f)) ]

def parse_scenario_to_dictionary(scenario_file):
    '''Parse an amber scenario file to a python dictionary

    Accepted file extensions: [.yaml | .yml], and [.sh] as described in
    https://github.com/AA-ALERT/AMBER_setup/blob/development/examples/scenario.sh

    Parameters
    ----------
        scenario_file: amber scenario file (including path)

    Returns
    -------
        scenario_dict: parsed dictionary
    '''
    if scenario_file.split('.')[-1] == 'sh':
        scenario_dict = parse_sh_scenario_to_dictionary(scenario_file)
    elif scenario_file.split('.')[-1] in ['yaml', 'yml']:
        scenario_dict = parse_yaml_scenario_to_dictionary(scenario_file)
    else:
        scenario_dict = parse_sh_scenario_to_dictionary(scenario_file)

    return scenario_dict

def parse_sh_scenario_to_dictionary(scenario_file):
    '''Parse an amber scenario file to a python dictionary

    File extension expected is '.sh' as described in
    https://github.com/AA-ALERT/AMBER_setup/blob/development/examples/scenario.sh

    Note that the extension is not required per se,
    but the file structure should follow a shell variable structure.

    Parameters
    ----------
        scenario_file: amber scenario file (including path)

    Returns
    -------
        scenario_dict: parsed dictionary
    '''
    scenario_dict = {}
    with open(scenario_file, 'r') as f:
        for line in f:
            if line[0] not in ['!', '#', '\n']:
                param, value = line.replace('\n', '').replace('"', '').split('=')
                scenario_dict[param] = value
    return scenario_dict

def parse_yaml_scenario_to_dictionary(scenario_file, scenario_name=None):
    '''Parse an amber scenario file (yaml) to a python dictionary

    Parameters
    ----------
        scenario_file: amber scenario file in yaml format (including path)

    Returns
    -------
        scenario_dict: parsed dictionary
    '''
    scenario_dict = {}

    with file(scenario_file, 'r') as f:
        scenario_dict = yaml.load(f)

    if scenario_name != None:
        # e.g. scenario_dict['subband'] for multilayer yaml scenario file
        return scenario_dict[scenario_name]
    else:
        return scenario_dict
