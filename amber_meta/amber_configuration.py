"""
.. module:: amber_configuration.rst
   :platform: Unix, Windows
   :synopsis: Class representing amber's configuration files

.. moduleauthor:: D. Vohl <vohl@astron.nl>


"""

class AmberConfiguration:
    """Class representing amber's configuration files.
    The class can be instanciated using default values, or by passing
    parameters as input. All command options will be availble via
    self.options.

    Parameters
    ----------
    rfim : bool (optional)
        Default: True
    rfim_mode : str (optional)
        RFIm mode of operation. Default: 'time_domain_sigma_cut'

    Attributes
    ----------
        suffix : str
            Suffix of configuration files (.conf)
        configurations : dict
            Configuration built at initialisation
        rfim_config_tdsc_files : list
            List of configuration file names for RFIm's time domain sigma cut
        rfim_config_fdsc_files : list
            List of configuration file names for RFIm's frequency domain sigma cut
        rfim_config_files : dict
            Options to choose between RFIm modes
        downsampling_configuration : str
            'downsampling'
        integration_steps : str
            'integration_steps'
        zapped_channels : str
            'zapped_channels'
    """
    suffix = '.conf'

    # RFIm
    rfim_tdsc_options = ['time_domain_sigma_cut_steps', 'time_domain_sigma_cut_configuration']
    rfim_fdsc_options = ['frequency_domain_sigma_cut_steps', 'frequency_domain_sigma_cut_configuration']
    rfim_options = {
        'time_domain_sigma_cut': rfim_tdsc_options,
        'frequency_domain_sigma_cut': rfim_fdsc_options
    }
    rfim_config_tdsc_files = {
        'time_domain_sigma_cut_configuration': 'tdsc',
        'time_domain_sigma_cut_steps': 'tdsc_steps'
    }
    rfim_config_fdsc_files = {
        'frequency_domain_sigma_cut_configuration': 'fdsc',
        'frequency_domain_sigma_cut_steps': 'fdsc_steps'
    }
    rfim_config_files = {
        'time_domain_sigma_cut': rfim_config_tdsc_files,
        'frequency_domain_sigma_cut': rfim_config_fdsc_files,
        'both__tdsc_fdsc': (rfim_config_tdsc_files, rfim_config_fdsc_files),
        'both__fdsc_tdsc': (rfim_config_fdsc_files, rfim_config_tdsc_files)
    }

    # Downsampling
    downsampling_configuration = 'downsampling'
    integration_steps = 'integration_steps'
    zapped_channels = 'zapped_channels'

    def __init__(self,
                 rfim=False,
                 rfim_mode='time_domain_sigma_cut',
                 downsampling=False):
        self.configurations = {}
        if rfim:
            self.configurations[rfim_mode] = self.rfim_config_files[rfim_mode]
        if downsampling:
            self.configurations['downsampling_configuration'] = self.downsampling_configuration
        self.configurations['integration_steps'] = self.integration_steps
        self.configurations['zapped_channels'] = self.zapped_channels
