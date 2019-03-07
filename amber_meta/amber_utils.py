from __future__ import division, print_function
import os
import yaml

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

    with file('document.yaml', 'r') as f:
        scenario_dict = yaml.load(f)

    if scenario_name != None:
        # e.g. scenario_dict['subband'] for multilayer yaml scenario file
        return scenario_dict[scenario_name]
    else:
        return scenario_dict
