
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
        rfim_config_tdsc_files : list
            List of configuration file names for RFIm's time domain sigma cut
        rfim_config_fdsc_files : list
            List of configuration file names for RFIm's frequency domain sigma cut
        rfim_config_files : dict
            Options to choose between RFIm modes
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
    rfim_config_fdsc_files = ['fdsc', 'fdsc_steps']
    rfim_config_files = {
        'time_domain_sigma_cut': config_tdsc_files,
        'frequency_domain_sigma_cut': config_fdsc_files
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

    def get_rfim_confs_list(rfim_mode):
        """Get list of configuration files for RFIm

        Parameter
        ---------
        rfim_mode : str
            Mode of operation for RFIm
        """
        new_confs = []
        for option in self.rfim_options:
            for value in self.configurations[rfim_mode][option]:
                new_confs.append(value)
         return new_confs

    def get_rfim_confs_list_for_specific_threshold(rfim_mode, threshold):
        """Get list of configuration files for RFIm and specific threshold

        Parameter
        ---------
        rfim_mode : str
            Mode of operation for RFIm
        threshold : str
            Threshold value used in file
        """
        new_confs = []
        for option in self.rfim_options:
            for value in self.configurations[rfim_mode][option]:
                new_confs.append(
                    "%s%s%s" % (
                        value,
                        '_threshold_',
                        threshold
                     )
                 )
         return new_confs
