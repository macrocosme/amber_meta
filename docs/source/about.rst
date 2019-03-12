About
======

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

Example of root yaml file
-------------------------

.. code-block:: yaml
  # AMBER setup for bruteforce dedispersion
  bruteforce:
      input_file: 'path/to/filterbank.fil'
      n_cpu: 1
      base_name: 'scenario_base_name'
      base_scenario_path: 'scenario/' # Path where amber scenario files live
      scenario_files:  ['tuning.sh']
      snrmin: 8
      base_config_path: 'configuration/' # Path where amber configuration files live
      config_repositories: ['scenario_base_name']
      debug: False
      rfim: True
      rfim_mode: 'time_domain_sigma_cut'
      rfim_threshold: None
      snr_mode: 'snr_mom_sigmacut'
      input_data_mode: 'sigproc'
      output_dir: 'results/'
      verbose: True
      print_only: False
  # AMBER setup for subband dedispersion
  subband:
      input_file: 'path/to/filterbank.fil'
      n_cpu: 3
      base_name: 'scenario_base_name'
      base_scenario_path: 'scenario/'
      scenario_files:  [
          'tuning_1.sh',
          'tuning_2.sh',
          'tuning_3.sh'
        ]
      snrmin: 8
      base_config_path: 'configuration/'
      config_repositories: [
          'scenario_base_name_step1',
          'scenario_base_name_step2',
          'scenario_base_name_step3'
        ]
      debug: False
      rfim: True
      rfim_mode: 'time_domain_sigma_cut'
      rfim_threshold: None
      snr_mode: 'snr_mom_sigmacut'
      input_data_mode: 'sigproc'
      output_dir: 'results/'
      verbose: True
      print_only: False

License
-------

   This project is licensed under the terms of the GNU GPL v3+ license.
