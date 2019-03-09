from pandas import read_csv as pandas__read_csv
from .amber_utils import (
    get_Files,
    check_path_ends_with_slash
)

def get_header(filename, sep=' '):
    with open(filename, 'r') as f:
        return f.readline().split('\n')[0].split('# ')[1].split(sep)

def read_amber_run_results(run_output_dir, verbose=False, sep = ' '):
    # Get input file's header (amber format)
    header = get_header(
        "%s%s" % (
            check_path_ends_with_slash(run_output_dir),
            get_Files(run_output_dir)[0]
        ), sep)

    # Create empty dataframe
    df = pandas__read_csv(
        # path/to/file.trigger
        "%s%s" % (
            check_path_ends_with_slash(run_output_dir),
            get_Files(run_output_dir)[0]
        ),
        sep=sep,
        names=header,
        skiprows=1
    )

    # Go through output files
    for file in get_Files(run_output_dir)[1:]:
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
