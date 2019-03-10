from pandas import read_csv as pandas__read_csv
from .amber_utils import (
    list_files_in_current_path,
    check_path_ends_with_slash
)

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
