# Waveform Lidar Data Analysis

This repository hosts tools and resources for analyzing full waveform lidar data, covering tasks such as data collection, cleaning, analysis, feature extraction, engineering, and modeling. Each directory focuses on a specific aspect of waveform lidar processing and includes all necessary resources, updated regularly as needed.

### Current Resources:
- **`Noise-addition-to-simdata`**: Tools for adding realistic noise to simulated full-waveform lidar data.
- **`Signal-deconvolution`**: Tools for correcting for the system response in full-waveform lidar data.
- **`Noise-sensitivity-in-deconvolution`**: Experiments to see how noise effects the deconvolution process.
- **`Lidar_scan_setting.ipynb`**: Python notebook file for determining parameters required for DIRSIG based waveform lidar simulation.
- **`wlidar_metrics_calculation.ipynb`**: Python notebook file for calculating full-waveform lidar metrics, including:

    #### Intensity-based metrics
    - `intensity_std` – Standard deviation of intensity values  
    - `intensity_mean` – Mean of intensity values  
    - `centroids1d` – Intensity-weighted centroid of the waveform  
    - `radii_of_gyration1d` – Intensity-weighted radius of gyration  

    #### Geometrical metrics
    - `Cx_geom` – Geometric centroid in the X-direction  
    - `Cy_geom` – Geometric centroid in the Y-direction  
    - `radii_of_gyration_geom` – Geometric radius of gyration  

    #### Height-related metrics
    - `RH25`, `RH50`, `RH75`, `RH100` – Relative heights at given percentiles  
    - `canopy_heights` – Absolute canopy height values  
    - `rough_values` – Surface roughness (Ra)  
    - `front_slope_angles` – Leading edge slope angles  
    - `number_of_peaks` – Count of distinct peaks in waveform  
    - `waveform_distances` – Distances between peaks  
    - `htmr_values` – Height-to-median ratio  
    - `vdr_values` – Vertical distribution ratio  
    - `RWE` – Total return energy  

    #### Slope-based metrics
    - `mean_start_slopes` – Mean leading-edge slopes  
    - `std_start_slopes` – Standard deviation of leading-edge slopes  
    - `ratio_start_slopes` – Ratio of first to last leading-edge slopes  
    - `ratio_end_slopes` – Ratio of first to last trailing-edge slopes  
    - `mean_end_slopes` – Mean trailing-edge slopes  
    - `std_end_slopes` – Standard deviation of trailing-edge slopes  
    - `veg_to_ground_slope_ratio` – Ratio of vegetation peaks to ground peaks  

    #### Statistical and distribution metrics
    - `kurtosis` – Measure of waveform peakedness  
    - `skewness` – Measure of waveform asymmetry  
    - `GC` – Gini coefficient (waveform energy distribution)  
    - `LE` – Lorentz entropy (waveform complexity)


Future updates will include additional modules for data processing and structure modeling.  
We welcome suggestions and contributions to improve the repository.  

**Contact**: [rb1005@rit.edu](mailto:rb1005@rit.edu) for potential collaborations.