#!/bin/bash

# Example tuning scenario

# System
## CPU core to pin the processes to
CPU_CORE="1"
## OpenCL platform ID
OPENCL_PLATFORM="0"
## OpenCL device ID
OPENCL_DEVICE="1"
## Name of OpenCL device, used for configuration files
DEVICE_NAME="ARTS_step2_81.92us_1370MHz"
## Size, in bytes, of the OpenCL device's cache line
DEVICE_PADDING="128"
## Number of OpenCL work-items running simultaneously
DEVICE_THREADS="32"

# Tuning
## Number of iterations for each kernel run
ITERATIONS="1"
## Minimum number of work-items
MIN_THREADS="8"
## Maximum number of work-items
MAX_THREADS="1024"
## Maximum number of variables
MAX_ITEMS="63"
#MAX_ITEMS="255"
## Maximum unrolling
MAX_UNROLL="1"
## Maximum number of work-items in OpenCL dimension 0; dedispersion specific
MAX_DIM0="1024"
## Maximum number of work-items in OpenCL dimension 1; dedispersion specific
MAX_DIM1="128"
## Maximum number of variables in OpenCL dimension 0; dedispersion specific
MAX_ITEMS_DIM0="64"
## Maximum number of variables in OpenCL dimension 1; dedispersion specific
MAX_ITEMS_DIM1="32"
## Switch to use the subbanding mode; dedispersion specific
SUBBANDING=true

## Switch to select the SNR Mode ["SNR", "MOMAD", "SNR_SC"]
SNR="SNR_SC"
# Scenario
## Number of channels
CHANNELS="1536"
## Frequency of the lowest channel, in MHz
MIN_FREQ="1219.700927734375"
## Bandwidth of a channel, in MHz
CHANNEL_BANDWIDTH="0.1953125"
## Number of samples per batch
SAMPLES="12500"
# Sampling time, in seconds
SAMPLING_TIME="0.00008192"
## Downsampling factor
DOWNSAMPLING=1
## Number of subbands
SUBBANDS="32"
## Number of DMs to dedisperse in step one; subbanding mode only
SUBBANDING_DMS="64"
## First DM in step one; subbanding mode only
SUBBANDING_DM_FIRST="409.6"
## DM step in step one; subbanding mode only
SUBBANDING_DM_STEP="6.4"
## Number of DMs to dedisperse in either the single step or subbanding step two
DMS="32"
## First DM in either the single step or subbanding step two
DM_FIRST="0.0"
## DM step in either the single step or subbanding step two
DM_STEP=".2"
## Number of input beams
BEAMS="12"
## Number of synthesized output beams
SYNTHESIZED_BEAMS="4"
## Sigma cut steps for the time domain sigma cut RFI mitigation
RFIM_TDSC_STEPS="3.25 3.25 3.25"
## Downsampling factors
INTEGRATION_STEPS="5 10 25 50 100 250 500 1000"
## Zapped channels
ZAPPED_CHANNELS=""
## Median of medians step; only for MOMAD mode
MEDIAN_STEP=5
## Sigma cut value for SNR_SC mode; this value is currently harcoded in AMBER
NSIGMA=3
## Sigma cut for the SNR computation in SNR_SC mode
SNR_SIGMA=3.00
