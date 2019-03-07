from pandas import read_csv as pandas__read_csv
from amber_utils import get_Files, check_path_ends_with_slash

def get_header(filename, sep=' '):
    with open(filename, 'r') as f:
        return f.readline().split('\n')[0].split('# ')[1].split(sep)

def read_amber_run_results(run_output_dir, verbose=False):
    sep = ' '
    dfs = []
    for file in get_Files(run_output_dir):
        if verbose:
            print (file)

        # Get input file's header (amber format)
        header = get_header(file, sep)

        # Read .trigger file to pandas' dataframe
        dfs.append(
            pandas__readcsv(
                # path/to/file.trigger
                "%s%s" % (
                    check_path_ends_with_slash(run_output_dir),
                    filename
                ),
                sep=sep,
                names=header,
                skiprows=1
            )
        )

    return dfs
