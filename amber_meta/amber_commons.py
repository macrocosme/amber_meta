import os
import sys
from os import path, listdir, walk
from os.path import isfile, join
# from itertools import izip
import fileinput
import csv

from astropy.io import fits
import pyfits
import numpy as np

from pandas import read_csv

'''
Simple handy functionalities to manipulate and deal with data.

author: Dany Vohl, 2016.
'''

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

def find_replace(filename, text_to_search,text_to_replace):
    """ finds text_to_search in filename and replaces it with text_to_replace """
    i = 0
    for line in fileinput.input(filename, inplace=True):
        sys.stdout.write(line.replace(text_to_search, text_to_replace))

def get_Files(path):
    return [ f for f in listdir(path) if isfile(join(path,f)) ]

# def flip_CSV(file):
#     """ flips a CSV file within itself (similar to a transpose) """
#     a = izip(*csv.reader(open(file, "rb")))
#     csv.writer(open(file, "wb")).writerows(a)

def create_cube_from_files_in_current_folder(out_fname):
    """
    Create a cube from fits files in a folder.

    :param out_fname: output filename (should be .fits)
    :return: nothing.
    """

    #TODO: check that all files are in folder are fits; file ordering; image alignment; etc.

    assert ".fits" in out_fname, 'out_fname needs to contain ".fits"\n' \
                                 'Usage example: create_cube_from_files_in_current_folder("filename.fits")'
    files = list_files_in_current_path('.')
    image = fits.open(files[0])
    cube = np.ndarray(shape=(len(files), image[0].data.shape[0], image[0].data.shape[1]), dtype=float)
    i = 0
    for fname in files:
        image = fits.open(fname)
        cube[i] = image[0].data
        i += 1

    header = pyfits.getheader(files[0])
    pyfits.writeto(out_fname, cube, header, clobber=True)

def convert_time_string_to_seconds(timing):
    """
    Converts a string of the form HH:MM:SS or MM:SS to integer representing the number of seconds.
    :param timing:
    :return:
    """
    try:
        converted_time = int(timing.split(':')[0]) * 60 * 60 + \
                         int(timing.split(':')[1]) * 60 + \
                         int(timing.split(':')[2])
    except:
        converted_time = int(timing.split(':')[0]) * 60 + int(timing.split(':')[1])

    return converted_time

def check_path(path):
    """
    Check if path ends with a slash ('/'). Else, it adds it.
    :param path: path
    :return: functional path
    """
    if len(path) > 0 and path[-1] != '/':
        path = path + '/'

    if not os.path.exists(path):
        os.makedirs(path)

    return path

def read_text_file_with_pound_header(input_path, input_filename):
    def column_cleaning(frame):
        frame.columns = np.roll(frame.columns, len(frame.columns) - 1)
        return frame.dropna(how='all', axis=1)

    return column_cleaning(read_csv(check_path(input_path) + input_filename, sep='\s+'))

def index_to_lambda(value, header):
    return header['CDELT3']*value + header['CRVAL3']

def lambda_to_index(value, header):
    return int(round((value - header['CRVAL3'])/header['CDELT3']))
