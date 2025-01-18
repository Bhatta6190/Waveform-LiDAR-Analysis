# Noise Analysis for Waveform LiDAR Data

## Overview

This code aims to generate **noise** and **signal peak distributions** using real LVIS (Laser Vegetation Imaging Sensor) data. These distributions will be used for adding noise to the simulated noise-free data based on the peak height of the simulated waveforms. The distribution are generated through smoothing waveforms and then calculating the difference between the noisy and smooth waveforms to generate the noise distribution. Similarly the noise-free waveforms are used to determine the **peak height distribution**. The overall steps include:

1. **Smoothing the waveforms** to create a noise-free approximation.
2. **Generating the noise distribution** by subtracting the smooth waveform from the noisy waveform.
3. **Determining the peak height distribution** from the smooth waveform, subtracting min from max intensity level.
4. **Saving the distributions** and saving them for future use in noise addition.

## Requirements

- `h5py` for reading LiDAR data from `.h5` files.
- `numpy` for numerical operations.
- `matplotlib` for plotting.
- `scipy` for FFT-based processing.

## Steps

### 1. Frequency Distribution for Cut-off Selection

The script first extracts a set of waveforms and computes their FFT, plotting the magnitude of the shifted FFT. This helps identify the **cut-off frequency** for noise filtering.

### 2. Smoothing and Low-pass Filtering

The noisy waveform is smoothed by applying a low-pass filter. The resulting filtered waveform is considered a noise-free approximation. The code then subtracts the filtered (smoothed) waveform from the original waveform to calculate the **noise** distribution.

### 3. Generating Noise and Signal Peak Distributions

- **Noise Distribution**: The noise is calculated by finding the difference between the original noisy waveform and the smoothed waveform. This difference represents the noise present in the signal.
- **Peak Height Distribution**: The peak height is determined from the smoothed waveform, which is treated as the signal with minimal noise.

### 4. Saving Distributions

The generated **noise** and **peak height** distributions are saved to `.txt` files for future use, such as adding noise to simulated waveforms or further analysis.

## Usage

1. **Data Input**: Place your `.h5` files in the directory and update the `file_names` variable with the paths to your files.
2. **Cut-off Frequency**: Adjust the cut-off frequency in the code (`cut_off = 150`) based on your noise characteristics.
3. **Distribution Files**: The script generates noise and peak height distributions, which can be saved to text files (`lvis_noise_values.txt`, `lvis_peakHeight_values.txt`).

## Notes

- The waveform data (`RXWAVE`) and signal mean (`SIGMEAN`) should be present in the `.h5` files.
- You can adjust the number of waveforms processed and the cut-off frequency based on your specific needs.
- The generated noise and peak height distributions can be used for noise simulation in waveform LiDAR data.

## Dataset
 
The dataset used in this analysis are LVIS 1B data producs (A sample of which is included in the zip file). For more information on dataset users are
referred: https://nsidc.org/data/lvisf1b/versions/1. The specific data used here is from NASA BioScape Campaign 2023: https://www.bioscape.io/data.