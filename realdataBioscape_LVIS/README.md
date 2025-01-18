# Noise Analysis for Waveform LiDAR Data

## Overview

This code performs a noise analysis on waveform LiDAR data, specifically using data from the LVIS (Laser Vegetation Imaging Sensor). The analysis includes:

1. **Frequency Distribution** for selecting a cut-off frequency.
2. **Low-pass Filtering** for denoising waveforms.
3. **Noise, Peak Height, and SNR Distributions** to evaluate signal quality.
4. **Saving Noise and Peak Height Distributions** for further use.

## Requirements

- `h5py` for reading LiDAR data from `.h5` files.
- `numpy` for numerical operations.
- `matplotlib` for plotting.
- `scipy` for FFT-based processing.

## Steps

### 1. Frequency Distribution for Cut-off Selection

The script extracts a set of waveforms and computes their FFT, plotting the magnitude of the shifted FFT. This helps identify the cut-off frequency for noise reduction.

### 2. Low-pass Filtering for Denoising

Using the cut-off frequency, the script applies a low-pass filter to remove high-frequency noise. The original and denoised waveforms are plotted for comparison.

### 3. Generating Distributions

The script calculates the following for a set of waveforms:

- **Peak Heights**: The difference between the maximum and minimum values of the filtered waveform.
- **Noise Values**: The difference between the original and denoised waveforms.
- **SNR (Signal-to-Noise Ratio)**: The ratio of peak height to the standard deviation of noise, calculated in dB.

### 4. Saving Distributions

The noise and peak height distributions are saved to text files for future use.

## Usage

1. **Data Input**: Place your `.h5` files in the directory and update the `file_names` variable.
2. **Cut-off Frequency**: The cut-off frequency can be adjusted in the code (`cut_off = 150`).
3. **Distribution Files**: The script can save the generated distributions to `.txt` files for later use in simulations.

## Example Output

- Magnitude of FFT for waveforms.
- Original and denoised waveforms.
- Histograms for noise values, peak heights, and SNR.

## Notes

- The code assumes the waveform data (`RXWAVE`) and the signal mean (`SIGMEAN`) are stored in `.h5` files.
- You can adjust the number of waveforms processed and the cut-off frequency based on your needs.
