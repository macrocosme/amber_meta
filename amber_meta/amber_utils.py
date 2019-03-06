from __future__ import division, print_function
import os

def pretty_print_command (command):
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

def parse_scenario_to_dictionary(scenario_file):
    '''Parse an amber scenario file to a python dictionary

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
