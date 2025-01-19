# Adding Noise to Simulated Waveform LiDAR Data

This article explains the proposed method to add realistic noise to the simulated waveform LiDAR data to make it more similar to real-world data. The method incorporates characteristics of actual LVIS (Laser Vegetation Imaging Sensor) data into simulated waveforms to make the data suitable for scientific research and algorithm testing.

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
**realdataBioscape_LVIS** in text files: 

    - `lvis_noise_values.txt` for noise values.
    - `lvis_peakHeight_values.txt` for peak heights.

These distributions serve as the foundation for generating realistic noise and signal behavior in the simulated data.

### 3. **Simulated Signal Peak Heights**

The simulated waveforms are examined to calculate their signal peak heights and determine the distribution of peak heights. This is done beacause the relationship between signal peaks and noise levels is essential for making sure that the simulated noise is representative of real conditions. To account for noise scaling, the simulated peak heights are compared to the LVIS data. This ensures that the simulated waveforms' noise level is proportional to the actual signal strength.

### 4. **Adding Realistic Noise to Simulated Waveforms**

This step is the most critical part the process. The simulated waveforms are added with noise in a way that closely resembles the noise properties obtained from actual LVIS data. The steps involved are:

#### 4.1. Scaling the Simulated Signal

To add noise to the simulated waveforms, we match (approx.) the **signal-to-noise ratio (SNR)** of the simulated data to that of the real data using the distributions of noise and peak heights as:

1. **Simulated Peak Height Distribution**:  
   We calculate the peak heights for each simulated waveform, resulting in a **simulated peak height distribution**. The peak height is calculated as the difference between the maximum and minimum intensity values in each waveform.

2. **Scaling Factor**:  
   The scaling factor for noise is calculated by comparing the **simulated peak height distribution** with the **real peak height distribution**. For each time bin in the simulated waveform, we randomly select a value from each of these distributions and calculate a scaling factor as the ratio of the simulated peak height to the real peak height:
   
   `Scaling Factor = Simulated Peak Height / Real Peak Height`

   This scaling factor ensures that the noise added to the simulated waveform reflects the signal strength characteristics observed in real data.

#### 4.2. Adding Noise to the Simulated Waveform

For each time bin in the simulated waveform, noise is added based on the real data’s noise distribution. The noise value is scaled using the previously calculated scaling factor to maintain the proper SNR:

1. **Noise Simulation**:  
   For each time bin, the noise is calculated as:

   `Noise_sim = (Simulated Peak Height / Real Peak Height) * Real Noise`

   where `Real Noise` is sampled randomly from the **real noise distribution**.

2. **Noisy Signal**:  
   The final noisy waveform is then calculated by adding the scaled noise to the simulated waveform:

   `Noisy Waveform = Simulated Waveform + N * Noise_sim`

   Here, `N` is a scaling factor that controls the overall noise level:

   - **`N = 1`** corresponds to the baseline SNR (matching the SNR of the real data).
   - **Higher values of `N`** result in a lower SNR, making the signal noisier.
   - **Lower values of `N`** result in a higher SNR, improving the signal quality.

#### 4.3. Varying the Noise Levels

By adjusting the value of `N`, we generate noisy waveforms with different SNRs. The noise levels are chosen based on the users requirements and are represented as multiples or fractions of the baseline SNR. For example:

- `N = 1` corresponds to the baseline SNR (real data SNR).
- `N = 0.5` corresponds to double the SNR, resulting in a cleaner signal.
- `N = 2` corresponds to half the noise, reducing the SNR.

Basically `N` is controlling the width of noise-distribution to be added to the simulated signal.

#### 4.4. Final Noisy Waveform

After applying the noise, the final noisy waveform is obtained and can be used for downstream analysis. By varying the noise level `N`, we can simulate different real-world noise conditions and test the robustness of algorithms designed to process these noisy waveforms.

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

---

**Note**: To improve the clarity and communication of the technique, Chatgpt AI model was used to produce and revise some of the explanations of procedures in this README file.
