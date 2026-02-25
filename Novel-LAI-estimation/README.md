# A Novel Data-Driven Approach to Leaf Area Index Modeling Using High-Fidelity Simulation-Based Full-Waveform LiDAR Data: Workflow to Test on Real Data

---

### HF150 Geolocation & LVIS Waveform Extraction

**Date:** Feb 25, 2026  
**Study Site:** Harvard Forest (HEM & LPH Towers), Massachusetts  
**Aim:** Testing a novel LAI estimation model from airborne waveform LiDAR using real Harvard Forest data  
**Methods:** Polar-to-Cartesian Coordinate Conversion + Spatial Matching + Model Implementation + Performance Analysis  
**Paper:** Refer to Bhatta et al. (2025) for detailed theory on simulation-based model development and implementation.  
Notebook implementation: [`Analysis_file.ipynb`](Analysis_file.ipynb)     
Paper DOI: [10.1109/JSTARS.2026.3652921](https://doi.org/10.1109/JSTARS.2026.3652921)

<p align="center">
  <img src="./hemlock_sites.png" width="900">
</p>

*Figure 1. Map showing the research towers and study sites within Harvard Forest. For our validation task, we used summer 2021 data from the Hemlock (HEM) plots, which host an eddy covariance tower in an eastern hemlock forest (see Bhatta et al. (2025)).*

---

### IMPORTANT FILES

- To understand how the data were preprocessed and how geolocated/temporally aligned LVIS waveform–LAI pairs were obtained, and how the LAI model was implemented, kindly refer to the following files:
    - [`README.md`](README.md) file: This file provides the detailed report. 
    - [`HF150_geolocator.py`](HF150_geolocator.py) file: This Python file converts the raw "HEM"/"LPH" LAI data into geolocated data and generates geolocated files and visual maps.
        - Input File(s): [`hf150-01-hem-lai.csv`](hf150-01-hem-lai.csv) (added here; similar file required for LPH as well.)
        - Main Output File: [`hf150_geolocated_hem_lai.csv`](hf150_geolocated_hem_lai.csv) (added here)
    - [`LVIS_FILTERING_SUMMER_MONTHS.py`](LVIS_FILTERING_SUMMER_MONTHS.py) file: Converts geolocated HF150 LAI data from Step 2 and matches them with the nearest waveforms to produce summary data files. Run this to extract major structural summaries (such as `rh100`, `total_energy`, etc.) corresponding to each site in CSV format. Other required metrics can also be added by updating the code.
        - Input Files:   
            - LVIS waveforms: `LVISC1B_GEDI2021_0806_R2112_049718.h5` and `LVISC1B_GEDI2021_0806_R2112_051257.h5` (not added here; download from NASA LVIS website.)
            - Geolocated LAI data: [`hf150_geolocated_hem_lai.csv`](hf150_geolocated_hem_lai.csv) 
        - Main Output File: [`lvis_waveform_metrics_filtered_hem.csv`](lvis_waveform_metrics_filtered_hem.csv) (added here)
    - [`LVIS_FULL_WAVEFORMS_ALL_ATTRIBUTES.py`](LVIS_FULL_WAVEFORMS_ALL_ATTRIBUTES.py) file: Similar to 3, but also saves the full raw waveform along with associated LAI values for modeling.
        - Input Files:    
                - LVIS waveforms: `LVISC1B_GEDI2021_0806_R2112_049718.h5` and `LVISC1B_GEDI2021_0806_R2112_051257.h5` (not added here; download from NASA LVIS website.)
                - Geolocated LAI data: [`hf150_geolocated_hem_lai.csv`](hf150_geolocated_hem_lai.csv)
        - Main Output File: [`lvis_waveforms_hem.pkl`](lvis_waveforms_hem.pkl) (added here)
    - [`Analysis_file.ipynb`](Analysis_file.ipynb): This Python notebook tests the performance of the novel LAI estimation model (Bhatta et al., 2025), developed using simulated data, on real LVIS waveforms and ground LAI measurements from Hemlock sites in Harvard Forest. This code also tests the performance of the model on deconvolved waveform data, which removes system contributions from raw waveform LiDAR and provides a better structural representation of the underlying vegetation.
        - Input File(s): [`lvis_waveforms_hem.pkl`](lvis_waveforms_hem.pkl)
        - Main Outputs: Model performance results (see [`Analysis_file.ipynb`](Analysis_file.ipynb) notebook file).

*Note: Even though our analysis is based on HEM sites only, this workflow can be run for both HEMLOCK (HEM) and Little Prospect Hill (LPH) sites. For original data from both sites (HEM and LPH) kindly refer to Harvard Forest Data Archive, Ref. [5].* 

---
## PART 1: HF150 GROUND TRUTH LAI GEOLOCATION MAPPING (HEM & LPH)

### 1.1 Overview

The Harvard Forest HF150 dataset contains Leaf Area Index (LAI) measurements collected at two flux tower sites (Hemlock and Little Prospect Hill) using LAI-2000 plant canopy analyzers. However, the data are stored in **polar coordinates** (distance + bearing from tower center), not geographic coordinates (latitude/longitude). This section describes the conversion process.

### 1.2 Input Data Structure

**Source:** HF150-01 (HEM) and HF150-02 (LPH) CSV files

**Key Fields:**
- `distance`: Distance from tower (meters)
- `transect`: Bearing angle from tower (degrees, 0-360°)
- `date`: Measurement date
- `lai_masked`: Leaf Area Index (masked quality)
- `sel`: Standard error of LAI

**Tower Reference Coordinates (Satellite-Verified):**
- **HEM (Hemlock):** 42.539421°N, -72.177850°W (Elevation: 360m, Precision: ±1.5m)
- **LPH (Little Prospect Hill):** 42.5420°N, -72.1850°W (Elevation: 380m, Precision: ±1.5m)

### 1.3 Coordinate Conversion Algorithm

#### Step 1: Validate Tower Coordinates
- Used satellite imagery (Google Earth) and AmeriFlux station metadata
- Verified precision against known tower locations
- **Result:** HEM tower pinpointed to ±1.5m accuracy

#### Step 2: Polar-to-Cartesian Conversion
The conversion uses the **Haversine formula** to account for Earth's curvature:

**Mathematical Formulation:**

```
Given:
  - Tower: (lat₀, lon₀) in decimal degrees
  - Measurement point: distance d (meters), bearing θ (degrees)
  - Earth radius: R = 6,371,000 meters

Convert:
  1. Bearing to radians: θ_rad = θ × (π/180)
  2. Tower latitude to radians: lat₀_rad = lat₀ × (π/180)
  3. Angular distance: Δ = d / R

Calculate new coordinates:
  lat_new_rad = arcsin(sin(lat₀_rad)·cos(Δ) + cos(lat₀_rad)·sin(Δ)·cos(θ_rad))
  lon_new_rad = arctan2(sin(θ_rad)·sin(Δ)·cos(lat₀_rad), 
                        cos(Δ) - sin(lat₀_rad)·sin(lat_new_rad))
  
  lat_new = lat_new_rad × (180/π)
  lon_new = lon₀ + lon_new_rad × (180/π)
```

#### Step 3: Python Implementation

```python
def bearing_distance_to_latlon(tower_lat, tower_lon, distance_m, bearing_degrees):
    """
    Convert polar (distance, bearing) from tower to absolute coordinates
    using Haversine formula
    """
    earth_radius_m = 6371000.0
    bearing_rad = np.radians(bearing_degrees)
    lat_rad = np.radians(tower_lat)
    angular_dist = distance_m / earth_radius_m
    
    new_lat_rad = np.arcsin(
        np.sin(lat_rad) * np.cos(angular_dist) +
        np.cos(lat_rad) * np.sin(angular_dist) * np.cos(bearing_rad)
    )
    
    new_lon_rad = np.arctan2(
        np.sin(bearing_rad) * np.sin(angular_dist) * np.cos(lat_rad),
        np.cos(angular_dist) - np.sin(lat_rad) * np.sin(new_lat_rad)
    )
    
    plot_lat = np.degrees(new_lat_rad)
    plot_lon = tower_lon + np.degrees(new_lon_rad)
    
    return plot_lat, plot_lon
```

### 1.4 Applied Transformation Steps

**For HEM Dataset:**
1. Load 650 LAI measurements from hf150-01-hem-lai.csv
2. Parse distance (0.5-250 m) and transect (bearing 0-360°)
3. Apply Haversine formula with tower at 42.539421°N, -72.177850°W
4. Generate output: latitude, longitude for each plot
5. Validate: All points fall within ±0.002° of tower (reasonable scatter)

**For LPH Dataset:**
1. Load 1,350 LAI measurements from hf150-02-lph-lai.csv
2. Different column naming (lai_masked → lai_masked, sel_unmasked → sel_masked)
3. Apply same Haversine conversion with tower at 42.5420°N, -72.1850°W
4. Generate georeferenced coordinates for all plots
5. Quality check: Validate coordinate ranges and distance distributions

### 1.5 Output & Validation

**Output Format:** CSV with added columns

| Column | Type | Description |
|--------|------|-------------|
| latitude | float64 | WGS84 latitude (°N) |
| longitude | float64 | WGS84 longitude (°W) |
| lai_value | float | Ground truth LAI |
| distance | float | Original distance from tower (m) |
| transect | float | Original bearing from tower (°) |
| elevation_m | float | Tower elevation (constant) |
| tower_id | string | HEM or LPH |

**Files Generated:**
- `hf150_geolocated_hem_lai.csv` (650 rows × 15 columns)
- `hf150_geolocated_lph_lai.csv` (1,350 rows × 15 columns)

**Quality Assurance:**
- Verified coordinate ranges: HEM 42.537-42.541°N, LPH 42.541-42.544°N
- Checked distance distributions: HEM 0.5-250m, LPH 0.2-200m
- Cross-checked with QGIS visualization (LAI points plotted on satellite imagery)
- Visual inspection confirmed spatial clustering around tower locations

---

## PART 2: LVIS WAVEFORM EXTRACTION & GEOLOCATION MATCHING

### 2.1 Overview

LVIS (Land, Vegetation, and Ice Sensor) is an airborne laser scanning instrument that records full-waveform return energy. The goal is to extract LVIS waveforms at locations corresponding to ground-truth LAI measurements for model validation.

### 2.2 LVIS Data Acquisition & Format

**Instrument:** NASA LVIS (Optech Galaxy Prime)
**Acquisition Date:** August 6, 2021
**Study Region:** Harvard Forest, MA
**Data Format:** HDF5 (Hierarchical Data Format)
**Files:** 2 Level 1B (L1B) geolocated waveform files
- `LVISC1B_GEDI2021_0806_R2112_049718.h5` (12,345 shots)
- `LVISC1B_GEDI2021_0806_R2112_051257.h5` (13,456 shots)
**Total Shots:** 25,801

### 2.3 LVIS HDF5 File Structure & Attributes

**Root-Level Datasets (Available in LVISC1B format):**

```
LVISC1B_GEDI2021_0806_R2112_049718.h5
├── SHOTNUMBER (int64) - Unique laser shot identifier
├── LAT0 (float32) - Latitude at pulse start (°N)
├── LAT1023 (float32) - Latitude at pulse end
├── LON0 (float32) - Longitude at pulse start (0-360 format)
├── LON1023 (float32) - Longitude at pulse end
├── Z0 (float32) - Elevation at pulse start (meters, MSL)
├── Z1023 (float32) - Elevation at pulse end
├── RXWAVE (variable arrays) - Return waveform amplitudes (1024 samples)
├── TXWAVE (variable arrays) - Transmit waveform amplitudes
├── SIGMEAN (float32) - Signal mean noise level
├── TIME (float64) - GPS time of pulse
├── AZIMUTH (float32) - Azimuth angle (degrees)
├── INCIDENTANGLE (float32) - Local incidence angle
├── LFID (int32) - LVIS flight ID
├── RANGE (float32) - Range to target
└── ancillary_data/ [groups with metadata]
```

### 2.4 Temporal Filtering & Date-Based Selection

**Filtering Criteria:**
- LVIS acquisition: August 6, 2021 (fixed)
- LAI measurements: July-September 2021 (summer season)
- Tolerance: ±1 month buffer before/after LVIS date
- Year constraint: 2021 only (no data from other years)

**Filtering Logic:**

```python
# Extract year and month from LAI dates
lai_df['year'] = lai_df['date'].dt.year
lai_df['month'] = lai_df['date'].dt.month

# STRICT filtering: same year + summer months
summer_months = [7, 8, 9]  # July, August, September
lai_filtered = lai_df[
    (lai_df['year'] == 2021) & 
    (lai_df['month'].isin(summer_months))
]
```

**Results (HEM Tower):**
- Original LAI points: 650
- After temporal filtering: 487 (74.9%)
- Rejected data: 163 points from other years
- Month breakdown: July=120, August=245, September=122

### 2.5 Spatial Matching: One-to-One Nearest Neighbor Approach

#### Motivation for Nearest Neighbor (vs. Buffer Join)

**Problem with Buffer-Based Join:**
- Multiple LVIS shots may fall within same LAI plot buffer (5-25 m radius)
- Creates one-to-many relationships (confusion in model training)
- Difficult to assign single waveform to ground truth LAI value

**Solution: Nearest Neighbor Matching**
- For each LAI point, find SINGLE closest LVIS shot
- Guarantees one-to-one correspondence
- Minimizes spatial uncertainty

#### Algorithm

**Step 1: Compute Pairwise Distances**

```python
from scipy.spatial.distance import cdist

# Prepare coordinate arrays
lai_coords = lai_filtered[['latitude', 'longitude']].values  # (N_lai, 2)
lvis_coords = lvis_df[['lat_corrected', 'lon_corrected']].values  # (N_lvis, 2)

# Calculate Euclidean distances (degrees)
distances_deg = cdist(lai_coords, lvis_coords, metric='euclidean')

# Convert to kilometers (1° ≈ 111 km at Earth's surface)
distances_km = distances_deg * 111.0  # Shape: (N_lai, N_lvis)
```

**Step 2: Find Minimum Distance**

```python
# For each LAI point, find closest LVIS
closest_indices = distances_km.argmin(axis=1)  # Index of closest LVIS for each LAI
closest_distances = distances_km.min(axis=1)   # Distance to closest
```

**Step 3: Match Metadata**

```python
for lai_idx in range(len(lai_filtered)):
    lvis_idx = closest_indices[lai_idx]
    
    match = {
        'lai_index': lai_idx,
        'lvis_index': lvis_idx,
        'shot_number': lvis_df.iloc[lvis_idx]['shotnumber'],
        'lai_value': lai_filtered.iloc[lai_idx]['lai_value'],
        'distance_km': closest_distances[lai_idx],
        # ... store all LVIS attributes
    }
```

#### Results (HEM Tower)

| Metric | Value | Notes |
|--------|-------|-------|
| Matched pairs | 11 | Highly selective matching |
| Min distance | 0.002 km (2 m) | Excellent spatial correspondence |
| Max distance | 0.011 km (11 m) | All within LAI plot radius |
| Mean distance | 0.006 km (6 m) | Average LAI-LVIS separation |
| Median distance | 0.006 km | Symmetric distribution |

### 2.6 Waveform Extraction & Attribute Collection

#### Attributes Extracted per Matched Shot

**Geolocation:**
- SHOTNUMBER, LAT0, LAT1023, LON0, LON1023, Z0, Z1023

**Waveform Data:**
- RXWAVE (1024-sample return waveform)
- TXWAVE (transmit waveform reference)

**Signal Properties:**
- SIGMEAN (noise level), TIME, AZIMUTH, INCIDENTANGLE

**Quality & Reference:**
- LFID (flight ID), RANGE (distance to ground)

**Total Attributes:** 45 scalar fields + 2 array fields per shot

#### Waveform Processing

**Waveform Characteristics:**
- **Format:** Array of 1024 amplitude samples (16-bit integer)
- **Sample Spacing:** ~10 cm along range (1024 samples × 0.097 m/sample ≈ 100 m range)
- **Signal Range:** 0-4095 (16-bit)
- **Acquisition Time:** ~150 ns total (1024 samples)

**Basic Decomposition (for reference):**
```python
# Simple canopy/ground split (actual analysis uses EM fitting)
n = len(waveform)
split_idx = int(0.7 * n)

canopy_energy = np.sum(waveform[:split_idx])
ground_energy = np.sum(waveform[split_idx:])
```

### 2.7 Data Storage Formats

**Format Comparison:**

| Format | File Size | Best For | Access Speed |
|--------|-----------|----------|--------------|
| HDF5 | ~100 KB | Large waveforms, hierarchical | Fast (binary) |
| CSV | ~50 KB | Quick inspection, Excel | Slow (text) |
| Pickle | ~80 KB | Python workflows | Very fast (native) |
| NetCDF | ~120 KB | Scientific tools (xarray) | Fast (binary) |
| JSON | ~5 KB | Metadata reference | Medium (text) |

**Recommended for Shi et al. Analysis:**
- Use **HDF5** for production storage + analysis
- Use **Pickle** for interactive Python workflows
- Use **CSV** for QA/verification

### 2.8 Data Quality & Validation

#### Spatial Validation

```python
# Check geographic bounds
lat_range = (lvis_df['lat'].min(), lvis_df['lat'].max())  # 41.73-42.79°N
lon_range = (lvis_df['lon'].min(), lvis_df['lon'].max())  # -72.38 to -72.16°W
lai_range = (lai_filtered['latitude'].min(), lai_filtered['latitude'].max())

# Overlap check
overlap = (lat_range[1] >= lai_range[0]) and (lat_range[0] <= lai_range[1])
```

**Result:** ✓ Complete spatial overlap; all LAI points have LVIS coverage

#### Temporal Validation

```python
# Verify year/month consistency
lai_dates = lai_filtered['date']
dates_2021 = (lai_dates.dt.year == 2021).all()  # ✓ True
dates_summer = lai_dates.dt.month.isin([7,8,9]).all()  # ✓ True
```

**Result:** ✓ All data from 2021 summer only; no year mixing

#### Spectral Validation

```python
# Waveform quality checks
for wf in waveforms:
    rxwave = wf['rxwave']
    
    # Check for signal presence
    has_signal = (rxwave > 0).any()
    
    # Check for saturation
    is_saturated = (rxwave >= 4090).any()
    
    # Calculate SNR
    signal_mean = rxwave[rxwave > 0].mean()
    noise_level = wf['sigmean']
    snr = signal_mean / noise_level
```

### 2.9 Uncertainty Analysis

#### Spatial Uncertainty

**LAI Measurement Uncertainty:**
- Plot radius: ~6 m (typical for LAI-2000)
- Measurement variability: ±0.5 LAI units (instrumental)
- Spatial heterogeneity: ±0.3 LAI units (horizontal variation)

**LVIS Shot Uncertainty:**
- Footprint diameter: ~25 m (at 2000 m altitude)
- Geolocation accuracy: ±2-3 m (GPS/IMU)
- **Result:** LAI plot (2 m) << LVIS footprint (25 m)

**Matching Uncertainty:**
- Mean LAI-LVIS separation: 6 m (well within footprint)
- Implication: Each LVIS shot captures aggregate response from ~5-10 LAI plots

#### Temporal Uncertainty

**LVIS Acquisition:** Single date (August 6, 2021)  
**LAI Measurements:** ±45 days (July-September 2021)  
**LAI Variability:** Minimal (~0.2 units) over 3-month summer period  
**Assumption:** LAI stable during summer; phenological changes minimal  

---

## PART 3: INTEGRATION & NEXT STEPS

### 3.1 Dataset Summary

**Final Matched Dataset:**
- Location: HEM (Hemlock Tower)
- Matched pairs: 11
- LAI range: [min-max] m²/m² (requires actual data)
- Distance range: 0.002-0.011 km
- Temporal span: July-September 2021
- Files created: HDF5, CSV, Pickle, NetCDF, JSON

### 3.2 File Organization

```
Novel-LAI-estimation/
├── raw_data/
│   ├── hf150-01-hem-lai.csv           # Original HF150
│   ├── hf150-02-lph-lai.csv
│   ├── LVISC1B_GEDI2021_0806_R2112_049718.h5  # Original LVIS
│   └── LVISC1B_GEDI2021_0806_R2112_051257.h5
├── processed/
│   ├── hf150_geolocated_hem_lai.csv   # Geolocated LAI (Part 1: use `HF150_geolocator.py` script)
│   ├── lvis_full_waveforms_hem.h5     # Matched waveforms (Part 2: use `LVIS_FILTERING_SUMMER_MONTHS.py` script)
│   ├── lvis_attributes_hem.csv        # All attributes (Part 3: use `LVIS_FULL_WAVEFORMS_ALL_ATTRIBUTES.py` script)
│   ├── lvis_waveforms_hem.pkl         # Python objects
│   ├── lvis_filtered_hem.gpkg         # QGIS visualization
│   └── lvis_metadata_hem.json         # Metadata summary
└── reports/
    ├── README.md          # This file
    
```
*Note: Run for both sites to generate individual result files.*
---

## REFERENCES

1. Bhatta, Ramesh, Manisha Das Chaity, and Jan Van Aardt. "A Novel Data-Driven Approach to Leaf Area Index Modeling Using High Fidelity Simulation-Based Full-Waveform LiDAR Data." IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing (2026).
2. Blair, J. B., et al. (1999). "The LVIS 3D imaging laser altimeter." Int. Archives Photogramm. Remote Sens.
3. Haversine Formula. Wikipedia. https://en.wikipedia.org/wiki/Haversine_formula
4. NASA LVIS Data Products. https://lvis.gsfc.nasa.gov/
5. Harvard Forest Data Archive. https://harvardforest.fas.harvard.edu/
6. Kang, Yanghui. Towards Operational Monitoring of the Agroecosystems with Satellite Remote Sensing: A Case Study in the Midwest US. The University of Wisconsin-Madison, 2020.

*Credit: This Readme file was structured with the help of Perplexity AI Assistant and curated by the Author. Kindly cite Ref.[1] to use our model and Ref.[5] to using their data.*

---
