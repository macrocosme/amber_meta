
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

    def __init__(self, rfim=False, rfim_mode='time_domain_sigma_cut')
        self.configurations = {}
        if rfim:
            self.configurations[rfim_mode] = self.rfim_config_files[rfim_mode]

    def get_rfim_confs_list_with_suffixes(rfim_mode):
        """Get list of configuration files for RFIm with trailing suffixes

        Parameter
        ---------
        rfim_mode : str
            Mode of operation for RFIm
        """
        new_confs = []
        for option in self.rfim_options:
            for value in self.configurations[rfim_mode][option]:
                new_confs.append(
                    "%s%s" % (
                        value,
                        confs.suffix
                     )
                 )
         return new_confs

    def get_rfim_confs_list_for_specific_threshold_with_suffixes(rfim_mode, threshold):
        """Get list of configuration files for RFIm and specific threshold

        Get list of configuration files for RFIm and specific threshold with trailing suffixes.

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
                    "%s%s%s%s" % (
                        value,
                        '_threshold_',
                        threshold,
                        confs.suffix
                     )
                 )
         return new_confs
