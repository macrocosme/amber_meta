"""
.. module:: amber_options
   :platform: Unix, Windows
   :synopsis: Class representing amber's options

.. moduleauthor:: D. Vohl <vohl@astron.nl>


"""

class AmberOptions:
    """Class representing amber's command line options.

    The class can be instanciated using default values, or by passing
    parameters as input. All command options will be availble via
    self.options.

    >>> amber_options = AmberOptions(rfim=False, snr_mode='snr_mom_sigmacut', input_data_mode='sigproc', downsampling=False)
    >>> amber_options.options
    ['print',
     'opencl_platform',
     'opencl_device',
     'device_name',
     'sync',
     'padding_file',
     'zapped_channels',
     'integration_steps',
     'integration_file',
     'compact_results',
     'output',
     'dms',
     'dm_first',
     'dm_step',
     'threshold',
     'snr_mom_sigmacut',
     'max_std_file',
     'mom_stepone_file',
     'mom_steptwo_file',
     'sigproc',
     'stream',
     'header',
     'data',
     'batches',
     'channels',
     'min_freq',
     'channel_bandwidth',
     'samples',
     'sampling_time',
     'subband_dedispersion',
     'dedispersion_stepone_file',
     'dedispersion_steptwo_file',
     'subbands',
     'subbanding_dms',
     'subbanding_dm_first',
     'subbanding_dm_step']

    Parameters
    ----------
    rfim : bool (optional)
        Default: True
    rfim_mode : str (optional)
        RFIm mode of operation. Default: 'time_domain_sigma_cut'
    snr_mode : str (optional)
        SNR mode of operation. Default: 'snr_mom_sigmacut'
    input_data_mode : str (optional)
        Input data mode (sigproc's filterbank file or dada ringbuffer). Default: 'sigproc'
    downsampling : bool (optional)
        Enable downsampling. Default: False

    Attributes
    ----------
        options_base : list
            List of basic options
        options_tdsc : list
            List of options for RFIm's time domain sigma cut
        options_fdsc : list
            List of options for RFIm's frequency domain sigma cut
        options_rfim : dict
            Options to choose between RFIm modes
        options_snr_standard : list
            List of options for SNR standard
        options_snr_momad : list
            List of options for SNR median of medians maximum absolute deviation
        options_snr_mom_sigmacut : list
            List of options for SNR median of medians sigma cut
        options_SNR : dict
            Options to choose between SNR modes
        options_downsampling : list
            List of options for downsampling
        options_subband_dedispersion : list
            List of options for subband dedispersion
        options_sigproc : list
            List of options for sigproc data input
        options_dada : list
            List of options for dada ringbuffer input
        options_input_data : dict
            Options to choose between input data modes

    """
    # Base options
    options_base = ['print', 'opencl_platform', 'opencl_device', 'device_name', 'sync', 'padding_file', 'zapped_channels', 'integration_steps', 'integration_file', 'compact_results', 'output', 'dms', 'dm_first', 'dm_step', 'threshold',] #'debug',

    # RFIm
    options_tdsc = ['rfim', 'time_domain_sigma_cut', 'time_domain_sigma_cut_steps', 'time_domain_sigma_cut_configuration']
    options_fdsc = ['rfim', 'frequency_domain_sigma_cut', 'nr_bins', 'frequency_domain_sigma_cut_steps', 'frequency_domain_sigma_cut_configuration']
    options_both__tdsc_fdsc = options_tdsc + options_fdsc[1:]
    options_both__fdsc_tdsc = options_fdsc + options_tdsc[1:]
    options_rfim = {'time_domain_sigma_cut': options_tdsc, 'frequency_domain_sigma_cut': options_fdsc, 'both__tdsc_fdsc': options_both__tdsc_fdsc, 'both__fdsc_tdsc': options_both__fdsc_tdsc}

    # SNR
    options_snr_standard = ['snr_standard', 'snr_file']
    options_snr_momad = ['snr_momad', 'max_file', 'mom_stepone_file', 'mom_steptwo_file', 'momad_file']
    options_snr_mom_sigmacut = ['snr_mom_sigmacut', 'max_std_file', 'mom_stepone_file', 'mom_steptwo_file']
    options_SNR = {'snr_standard': options_snr_standard, 'snr_momad': options_snr_momad, 'snr_mom_sigmacut': options_snr_mom_sigmacut}

    # Downsampling
    options_downsampling = ['downsampling', 'downsampling_factor', 'downsampling_configuration']

    # Subband dedispersion
    options_subband_dedispersion = ['subband_dedispersion', 'dedispersion_stepone_file', 'dedispersion_steptwo_file', 'subbands', 'subbanding_dms', 'subbanding_dm_first', 'subbanding_dm_step']

    # Input data
    options_sigproc = ['sigproc', 'stream', 'header', 'data', 'batches', 'channels', 'min_freq', 'channel_bandwidth', 'samples', 'sampling_time']
    options_dada = ['dada', 'dada_key', 'beams', 'synthesized_beams', 'batches']
    options_input_data = {'sigproc': options_sigproc, 'dada': options_dada}

    def __init__(self, rfim=True, rfim_mode='time_domain_sigma_cut', snr_mode='snr_mom_sigmacut', input_data_mode='sigproc', downsampling=False):
        self.options = []
        self.options += self.options_base
        if rfim:
            self.options += self.options_rfim[rfim_mode]
        self.options += self.options_SNR[snr_mode]
        self.options += self.options_input_data[input_data_mode]
        if downsampling:
            self.options += self.options_downsampling
        self.options += self.options_subband_dedispersion
