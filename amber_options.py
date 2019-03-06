class AmberOptions:
    # Base options
    options_base = ['debug', 'print', 'opencl_platform', 'opencl_device', 'device_name', 'sync', 'padding_file', 'zapped_channels', 'integration_steps', 'integration_file', 'compact_results', 'output', 'dms', 'dm_first', 'dm_step', 'threshold',]

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

    # Sigproc
    options_sigproc = ['sigproc', 'stream', 'header', 'data', 'batches', 'channels', 'min_freq', 'channel_bandwidth', 'samples', 'sampling_time']

    # Gathering options into useful mixes (include downsampling)
    options_snr_standard_tdsc = options_base + options_rfim['time_domain_sigma_cut'] + options_SNR['snr_standard'] + options_downsampling + options_sigproc + options_subband_dedispersion
    options_snr_momad_tdsc = options_base + options_rfim['time_domain_sigma_cut'] + options_SNR['snr_momad'] + options_downsampling + options_sigproc + options_subband_dedispersion
    options_snr_mom_sigmacut_tdsc = options_base + options_rfim['time_domain_sigma_cut'] + options_SNR['snr_mom_sigmacut'] + options_sigproc + options_downsampling + options_subband_dedispersion
    # (no downsampling)
    options_snr_standard_tdsc_no_downsampling = options_base + options_rfim['time_domain_sigma_cut'] + options_SNR['snr_standard'] + options_sigproc +  options_subband_dedispersion
    options_snr_momad_tdsc_no_downsampling = options_base + options_rfim['time_domain_sigma_cut'] + options_SNR['snr_momad'] + options_sigproc + options_subband_dedispersion
    options_snr_mom_sigmacut_tdsc_no_downsampling = options_base + options_rfim['time_domain_sigma_cut'] + options_SNR['snr_mom_sigmacut'] + options_sigproc + options_subband_dedispersion

    # Meta
    options = {
        # with downsampling
        'snr_standard_tdsc': options_snr_standard_tdsc,
        'snr_momad_tdsc': options_snr_momad_tdsc,
        'snr_mom_sigmacut_tdsc': options_snr_mom_sigmacut_tdsc,
        # without downsampling
        'snr_standard_tdsc_no_downsampling': options_snr_standard_tdsc_no_downsampling,
        'snr_momad_tdsc_no_downsampling': options_snr_momad_tdsc_no_downsampling,
        'snr_mom_sigmacut_tdsc_no_downsampling': options_snr_mom_sigmacut_tdsc_no_downsampling,

    }
