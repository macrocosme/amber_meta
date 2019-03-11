.. amber_meta documentation master file, created by
   sphinx-quickstart on Sat Mar  9 10:02:46 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for amber_meta
======================================

This repository integrates a few routines to launch `amber <http://github.com/AA-ALERT/AMBER_setup>`_ in a systematic manner.

Getting the code
----------------

.. code-block:: shell

    git clone https://github.com/macrocosme/amber_meta.git
    cd amber_meta/

Usage
-----

The most basic usage is via `python amber_run.py`, and parameters that will be prompted.

Else, more advanced usage involves functions not yet added to amber_runs's main. In an ipython session:

.. code-block:: python

    import amber_meta.amber_run as ar
    import amber_meta.amber_plot as ap

    # Run amber using root scenario yaml file
    '''
    The amber job(s) will run independently. The following steps currently
    involves that these jobs have terminated and their .trigger outputs
    be available.
    '''
    imput_file = 'yaml/root/root.yaml'
    ar.run_amber_from_yaml_root(
      input_file,
      root='subband',
      verbose=False,
      print_only=True
    ) # Print only will not launch the amber job. When False, the command will be run via subprocess.

    # Read amber output .trigger files (e.g. steps 1..N) pooled into a pandas dataframe
    df = ar.get_amber_run_results_from_root_yaml(
      input_file,
      root='subband',
      verbose=False
    )

    # Make pair plot from output
    pairplot(
      df,
      output_name='../pairplot.pdf'
    )

License
-------

   This project is licensed under the terms of the GNU GPL v3+ license.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   About
   amber_run
   amber_utils
   amber_options
   amber_configuration
   amber_results
   amber_plot
