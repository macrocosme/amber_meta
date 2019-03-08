# amber_meta

This repository integrates a few routines to launch [amber](http://github.com/AA-ALERT/AMBER_setup) in a systematic manner.

## License

This project is Copyright (c) D. Vohl and licensed under
the terms of the GNU GPL v3+ license.

## Usage

The most basic usage is via `python amber_run.py`, and parameters that will be prompted. 

Else, more advanced usage involves function not yet added to amber_runs's main. In an ipython session: 

```python
import amber_run as ar
import amber_plot as ap

# Run amber using root scenario yaml file
'''
The amber job will run independently. The following steps currently 
involves that these jobs have terminated and their .trigger outputs 
be available.
'''
imput_file = '../yaml/root/root.yaml'
ar.run_amber_from_yaml_root(input_file, root='subband', verbose=False, print_only=True) # Print only will not launch the amber job. When False, the command will be run via subprocess.

# Read .trigger file to pandas' dataframe
df = ar.get_amber_run_results_from_root_yaml(input_file, root='subband', verbose=False)

# Make pair plot from output
pairplot(df, output_name='../pairplot.pdf')
```
