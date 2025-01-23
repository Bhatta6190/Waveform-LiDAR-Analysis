# Deconvolution of LiDAR Waveforms Using Richardson-Lucy and Gold Algorithms

This section focuses on deconvolution of waveform LiDAR data to recover the true backscattering profile by removing the system response contribution from the recorded waveform lidar data. The two key deconvolution algorithms used are **Richardson-Lucy** and **Gold** algorithms, both augmented with a **boosting** to enhance the deconvolution performance. The process iterates over several repetitions, applying boosting to improve the results. Below is an explanation of the methodology, mathematical models, and steps involved.

---

## Overview

In a typical LiDAR system, the recorded waveform \( P_t \) is a convolution of the true backscattering profile \( f_t \) and the system's response function \( R_t \), which represents the system's characteristics such as the laser pulse shape and detector response. The objective of the deconvolution process is to recover \( f_t \) from \( P_t \), thereby removing the influence of \( R_t \).

Mathematically, the relationship between the recorded waveform and the true backscattering profile is expressed as:

\[
P_t = f_t * R_t + n_t
\]

where:
- \( P_t \) is the observed LiDAR waveform ,
- \( f_t \) is the true backscattering profile ,
- \( R_t \) is the system response function ,
- \( * \) denotes the convolution operator,
- \( n_t \) represents noise in the recorded waveform.

The goal of deconvolution is to estimate \( f_t \) given \( P_t \) and \( R_t \).

---

## Deconvolution Algorithms

### 1. Richardson-Lucy (RL) Algorithm

The **Richardson-Lucy deconvolution** is an iterative algorithm based on the principle of maximum likelihood estimation. The key steps are as follows:

1. **Initialize** the deconvolved signal \( P_\delta(t) \) with a flat guess, typically an array of ones.
2. **Iterate** for a specified number of iterations:
    - Convolve the current estimate of the deconvolved signal \( P_\delta(t) \) with the system response \( R_t \).
    - Compute the ratio of the recorded waveform to the convolved signal: \( \frac{P_t}{R_t * P_\delta(t)} \).
    - Convolve this ratio with the flipped system response \( R_t \) to update the deconvolved signal.
3. **Boosting**: After each iteration, apply a boosting factor \( \beta \) to enhance the signal, adjusting the shape of the deconvolved waveform.
4. **Positivity constraint**: Enforce that the deconvolved signal cannot have negative values by taking the maximum of the current estimate and zero.
5. **Energy scaling**: Post-process the result by scaling the deconvolved signal to match the energy of the original recorded waveform.
6. **Cross-correlation**: Perform cross-correlation to estimate the shift between the recorded waveform and the deconvolved result, and apply a manual shift to align the two signals.

The Richardson-Lucy algorithm can be expressed iteratively as:

$$
P_\delta(t)^{(i+1)} = P_\delta(t)^i \cdot \left( \frac{P_t}{(R_t * P_\delta(t)^i)} * R_t^\text{flip} \right)
$$

where:
- $$ P_\delta(t)^i $$ is the estimate of the deconvolved signal at iteration $$ i $$,
- $$ * $$ denotes convolution,
- $$ R_t^\text{flip} $$ is the flipped system response.

---

### 2. Gold Algorithm (Toeplitz Matrix Method)

The **Gold deconvolution** algorithm involves constructing a Toeplitz matrix from the system response function and solving a linear system of equations. The process is as follows:

1. **Construct the Toeplitz matrix** \( H \) from the system response function \( R_t \). This matrix represents the convolution operation.
2. **Compute the observation vector** \( y' = H^T y \), where \( y \) is the observed waveform.
3. **Solve the linear system** \( H^T H P_\delta = y' \) to update the estimate of the deconvolved signal \( P_\delta \).
4. **Boosting**: Similar to the Richardson-Lucy algorithm, apply a boosting factor \( \beta \) after each repetition to modify the deconvolved signal.
5. **Positivity constraint**: Enforce positivity on the deconvolved signal after each iteration by taking the maximum of the current estimate and zero.
6. **Energy scaling**: Post-process the result by scaling the deconvolved signal to match the energy of the original recorded waveform.
7. **Cross-correlation**: Perform cross-correlation to estimate the shift between the recorded waveform and the deconvolved result, and apply a manual shift to align the two signals.

Mathematically, the Gold deconvolution can be written as:

\[
P_\delta = (H^T H)^{-1} H^T y
\]

where:
- \( P_\delta \) is the deconvolved signal,
- \( H \) is the Toeplitz matrix constructed from the system response,
- \( y \) is the observed waveform.

---

## Boosting and Repetitions

Both the Richardson-Lucy and Gold algorithms are enhanced with a **boosting factor** \( \beta \). Boosting involves raising the deconvolved signal to a power of \( \beta \), which amplifies the signal, especially in regions where the true profile has small variations. This helps refine the recovered signal after several iterations and repetitions.

Boosting is applied as follows:

\[
P_\delta \leftarrow P_\delta^\beta
\]

where \( \beta \) is the boosting coefficient and \( P_\delta \) is the deconvolved signal.

The process is repeated for a number of **iterations** to refine the deconvolution and for **repetitions** to allow for boosting to have a greater effect over multiple cycles.

---

## Cross-Correlation and Alignment

After the deconvolution process, the deconvolved signal may need to be aligned with the original recorded waveform. This is achieved through **cross-correlation**, which measures the similarity between the deconvolved signal and the recorded waveform. The shift corresponding to the maximum correlation is computed, and the deconvolved signal is manually shifted to correct for any misalignment.

The cross-correlation is computed as:

$$
\text{corr}(P_t, P_\delta) = \sum_{t} P_t(t) \cdot P_\delta(t)
$$

The shift is the index where the correlation is maximized, and the deconvolved signal is shifted accordingly.

---

## Conclusion

By applying the Richardson-Lucy and Gold deconvolution algorithms with boosting, the true backscattering profile can be recovered from the observed LiDAR waveform. The combination of iterative deconvolution, boosting, and alignment correction allows for more accurate recovery of the original signal, even in the presence of noise and system contributions.

These algorithms can be applied to various LiDAR datasets to study vegetation structure and other remote sensing applications where waveform data is available.

---

## References

-   M. Morháč,
    Deconvolution methods and their applications in the analysis of γ-ray spectra,
    Nuclear Instruments and Methods in Physics Research Section A: Accelerators, Spectrometers, Detectors and Associated Equipment,
    Volume 559, Issue 1,
    2006,
    Pages 119-123,
    ISSN 0168-9002,
    https://doi.org/10.1016/j.nima.2005.11.129.
    (https://www.sciencedirect.com/science/article/pii/S0168900205022527)

-   Clément Mallet, Frédéric Bretar,
    Full-waveform topographic lidar: State-of-the-art,
    ISPRS Journal of Photogrammetry and Remote Sensing,
    Volume 64, Issue 1,
    2009,
    Pages 1-16,
    ISSN 0924-2716,
    https://doi.org/10.1016/j.isprsjprs.2008.09.007.
    (https://www.sciencedirect.com/science/article/pii/S0924271608000993)