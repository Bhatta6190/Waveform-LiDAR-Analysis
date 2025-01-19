# Adding Noise to Simulated Waveform LiDAR Data

This article explains how to add realistic noise to the simulated waveform LiDAR data to make it more similar to real-world data. The method incorporates characteristics of actual LVIS (Laser Vegetation Imaging Sensor) data into simulated waveforms to make the data suitable for scientific research and algorithm testing.

---

## Purpose

The simulation of the waveform LiDAR data is frequently generated in ideal, noise-free conditions. However, due to environmental influences, sensor limitations, and system electronics, noise is always present in real-world data. To ensure that simulations are useful for developing robust algorithms, we employ noise that mimics the statistical and spectral characteristics of real data. This process is crucial for assessing how well algorithms perform, especially when there is a lot of noise, a lot of vegetation, or a weak signal.

---

## Process Overview

The noise-adding process involves multiple steps that combine simulated waveforms and real noise data from LVIS measurements. Below, the overall methodology is described, along with the reasoning behind each step.

### 1. **Simulated Waveforms**

The first step involves analyzing the simulated waveforms. These simulated waveforms represent the backscattered light intensity after a laser pulse interacts with a simulated environment. The sensor system is custom designed for the simulation and closely resembles with the real waveform lidar systems. We used "DIRSIG" tool which is an abbreviation for "Digital Imaging and Remote Sensing Image Generation", developed at "Digital Remote Sensing Laboratory (DIRS)" at Rochestor Institute of Technology. DIRSIG can be used to simulate multiple modality remote sensing systems like passive multi and hyperspectral systems and active LiDAR and RADAR systems. To learn more please visit: https://dirsig.cis.rit.edu/. 

The recorded waveform profiles contains:

- Time bins (representing distance or depth).
- Signal intensity (proportional to the number of photons detected).

The specific detail of simulated data is also included in the directory **16ns_profile**

### 2. **Analyzing Real-World Noise Characteristics**

Noise is a critical factor in real LiDAR data, and understanding its characteristics is essential to accurately simulate it. Using LVIS data, we analyzed and generated the noise distribution and signal peak height distribution. The resources for this task and their detailed explanation is available under directory
**realdataBioscape_LVIS**. These distributions serve as the foundation for generating realistic noise and signal behavior in the simulated data.

### 3. **Simulated Signal Peak Heights**

The simulated waveforms are examined to calculate their signal peak heights and determine the distribution of peak heights. This is done beacause
the relationship between signal peaks and noise levels is essential for making sure that the simulated noise is representative of real conditions.
To account for noise scaling, the simulated peak heights are compared to the LVIS data. This ensures that the simulated waveforms' noise level is 
proportional to the actual signal strength.

### 4. **Adding Realistic Noise to Simulated Waveforms**

This step is the most critical part the process. The simulated waveforms are added with noise in a way that closely resembles the noise properties obtained from actual LVIS data. The mathematical formulation of the process is provided below:

#### 4.1 **Noise Representation**
Let:
- \( P(t) \): Simulated clean waveform, where \( t \) represents the time bin.
- \( N(t) \): Noise added to each time bin \( t \), derived from real LVIS data.
- \( P_\text{noisy}(t) \): Final noisy waveform.

The noisy waveform is calculated as:
\[
P_\text{noisy}(t) = P(t) + \alpha \cdot N(t),
\]
where:
- \( \alpha \) is the noise scaling factor, which controls the Signal-to-Noise Ratio (SNR).

#### 4.2 **Scaling Factor Calculation**
The scaling factor \( \alpha \) is determined based on the peak height of the simulated waveform relative to the real noise. Let:
- \( P_\text{peak} \): Maximum signal intensity (peak height) of the simulated waveform.
- \( \sigma_N \): Standard deviation of the real noise.

The scaling factor is:
\[
\alpha = \frac{P_\text{peak}}{S_\text{target} \cdot \sigma_N},
\]
where \( S_\text{target} \) is the target SNR. By controlling \( S_\text{target} \), the user can simulate different noise levels (high SNR for less noise, low SNR for more noise).

#### 4.3 **Noise Distribution**
The noise \( N(t) \) is generated from a Gaussian distribution:
\[
N(t) \sim \mathcal{N}(0, \sigma_N^2),
\]
where \( \sigma_N \) is the standard deviation of the noise extracted from real LVIS data.

#### 4.4 **Final Noisy Waveform**
The final noisy waveform is obtained by adding scaled noise \( \alpha \cdot N(t) \) to the clean waveform \( P(t) \). This ensures that the noise closely resembles real-world characteristics and is proportional to the simulated signal intensity.

---

### 5. **Visualizing Noise-Added Waveforms**
After adding noise, the final step involves visualizing the noisy waveforms. This includes:
- Comparing clean and noisy waveforms to assess the impact of the noise.
- Plotting waveforms for different SNR levels to understand how noise affects signal detectability.

The visualization helps validate the realism of the added noise and provides insights into how algorithms might perform under varying noise conditions.

---

## Key Insights

1. **Realistic Noise Simulation**: By using actual LVIS noise and signal distributions, we ensure that the simulated waveforms closely resemble real-world data.
2. **Controlled SNR**: The ability to adjust the noise level makes this method versatile for different research scenarios, from idealized studies to testing in highly noisy conditions.
3. **Peak Height Scaling**: Matching the simulated signal peak heights with real data ensures that the noise is proportional and realistic, maintaining the integrity of the simulated waveforms.
4. **Validation Through Visualization**: Visualizing the waveforms before and after adding noise provides confidence in the accuracy of the noise simulation process.

---

## Importance of This Process

Adding realistic noise to simulated data is crucial for testing and validating LiDAR processing algorithms. Without noise, algorithms might perform unrealistically well, leading to overconfidence in their reliability. By incorporating noise:
- We simulate the challenges faced in real-world applications.
- Researchers can develop algorithms that are robust to noise and capable of extracting meaningful information from noisy waveforms.
- The simulated data becomes more representative of actual LiDAR systems, increasing its value for training, testing, and benchmarking purposes.

---

## Applications
- **Algorithm Development**: Testing deconvolution, peak detection, and classification algorithms under realistic noise conditions.
- **Remote Sensing Studies**: Simulating LiDAR data for various vegetation types, terrain, or environmental conditions.
- **System Design**: Evaluating the performance of LiDAR systems with different noise characteristics.

---

## Conclusion

This process bridges the gap between idealized simulations and real-world applications by adding realistic noise to simulated waveform LiDAR data. It provides researchers with a powerful tool for developing and testing algorithms in conditions that mimic actual LiDAR system outputs. The use of real LVIS data ensures that the noise characteristics are grounded in reality, making the simulated data suitable for practical use cases.
