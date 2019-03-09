"""
.. module:: amber_options
   :platform: Unix, Windows
   :synopsis: Module to run amber

.. moduleauthor:: D. Vohl <vohl@astron.nl>


"""

class AmberOptions:
    # Base options
    options_base = ['print', 'opencl_platform', 'opencl_device', 'device_name', 'sync', 'padding_file', 'zapped_channels', 'integration_steps', 'integration_file', 'compact_results', 'output', 'dms', 'dm_first', 'dm_step', 'threshold',] #'debug',

    # RFIm
    options_tdsc = ['rfim', 'time_domain_sigma_cut', 'time_domain_sigma_cut_steps', 'time_domain_sigma_cut_configuration']
    options_fdsc = ['rfim', 'frequency_domain_sigma_cut', 'time_domain_sigma_cut_steps', 'time_domain_sigma_cut_configuration'] # CHECK w/ Alessio
    options_rfim = {'time_domain_sigma_cut': options_tdsc, 'frequency_domain_sigma_cut': options_fdsc}

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
