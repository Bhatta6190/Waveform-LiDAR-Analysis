#!/usr/bin/env python3
"""
LVIS-LAI MATCHING WITH SUMMER SEASON FILTERING (JULY-SEPTEMBER 2021)

VERSION INFO:
- Filters LAI to EXACT YEAR (2021) only, since the LVIS data we are using was collected in Summer 2021.
- Allows SUMMER months: July, August, September (1 month buffer before & after)
- Does NOT use data from different years
- Strict year matching: year == 2021, month in [7, 8, 9]

Features:
1. Filter LVIS: August 6, 2021
2. Filter LAI: July-September 2021 ONLY (same year, summer season)
3. Select ONLY the CLOSEST waveform match for each LAI point
4. Create GeoPackage (.gpkg) files for QGIS visualization
5. Process both HEM and LPH simultaneously from 2 LVIS files
"""

## Import necessary Libraries

import h5py
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial.distance import cdist
from scipy.ndimage import gaussian_filter1d
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("LVIS-LAI MATCHING WITH SUMMER FILTERING (JULY-SEPTEMBER 2021)")
print("="*70)

##  A: LOAD BOTH LVIS FILES (DOWNLOAD THIS DATA FROM NASA LVIS WEBSITE)

print("\n[1] Loading LVIS data from both H5 files...")

lvis_files = [
    'LVISC1B_GEDI2021_0806_R2112_049718.h5',
    'LVISC1B_GEDI2021_0806_R2112_051257.h5'
]

all_lvis_data = {}
all_lvis_df_list = []

for lvis_file in lvis_files:
    print(f"\n  Loading: {lvis_file}")
    
    try:
        lvis_hdf = h5py.File(lvis_file, 'r')
        
        lvis_data = {}
        for key in lvis_hdf.keys():
            if key != 'ancillary_data':
                lvis_data[key] = np.array(lvis_hdf[key])
        
        # Create DataFrame with corrected coordinates
        lvis_df = pd.DataFrame({
            'shotnumber': lvis_data['SHOTNUMBER'],
            'lat': (np.array(lvis_data['LAT0']) + np.array(lvis_data['LAT1023'])) / 2.0,
            'lon_raw': (np.array(lvis_data['LON0']) + np.array(lvis_data['LON1023'])) / 2.0,
            'zt': np.maximum(np.array(lvis_data['Z0']), np.array(lvis_data['Z1023'])),
            'zg': np.minimum(np.array(lvis_data['Z0']), np.array(lvis_data['Z1023'])),
        })
        
        # Fix longitude: convert from 0-360 to -180 to 180
        lvis_df['lon'] = np.where(
            lvis_df['lon_raw'] > 180,
            lvis_df['lon_raw'] - 360,
            lvis_df['lon_raw']
        )
        
        # Add optional fields
        if 'SIGMEAN' in lvis_data:
            lvis_df['sigmean'] = lvis_data['SIGMEAN']
        if 'TIME' in lvis_data:
            lvis_df['time'] = lvis_data['TIME']
        if 'AZIMUTH' in lvis_data:
            lvis_df['azimuth'] = lvis_data['AZIMUTH']
        
        # Add file identifier
        lvis_df['source_file'] = lvis_file
        
        all_lvis_df_list.append(lvis_df)
        all_lvis_data[lvis_file] = lvis_data
        
        print(f"    ✓ Loaded {len(lvis_df)} shots")
        print(f"      LVIS Acquisition Date: August 6, 2021")
        
        lvis_hdf.close()
    
    except Exception as e:
        print(f"    ✗ Error: {e}")

# Combine all LVIS data
lvis_df_all = pd.concat(all_lvis_df_list, ignore_index=True)
print(f"\n  ✓ Total LVIS shots from both files: {len(lvis_df_all)}")


##  B: LOAD LAI DATA AND FILTER BY YEAR + SUMMER MONTHS

print("\n[2] Loading LAI data and filtering to summer months (July-September 2021)...")

lai_hem = pd.read_csv('hf150_geolocated_hem_lai.csv')
lai_lph = pd.read_csv('hf150_geolocated_lph_lai.csv')

print(f"\n  Original data:")
print(f"    HEM LAI points: {len(lai_hem)}")
print(f"    LPH LAI points: {len(lai_lph)}")
print(f"    HEM date range: {lai_hem['date'].min()} to {lai_hem['date'].max()}")
print(f"    LPH date range: {lai_lph['date'].min()} to {lai_lph['date'].max()}")

# Convert dates to datetime
lai_hem['date'] = pd.to_datetime(lai_hem['date'])
lai_lph['date'] = pd.to_datetime(lai_lph['date'])

# Extract year and month
lai_hem['year'] = lai_hem['date'].dt.year
lai_hem['month'] = lai_hem['date'].dt.month
lai_hem['doy'] = lai_hem['date'].dt.dayofyear

lai_lph['year'] = lai_lph['date'].dt.year
lai_lph['month'] = lai_lph['date'].dt.month
lai_lph['doy'] = lai_lph['date'].dt.dayofyear

# LVIS acquisition: August 6, 2021
lvis_year = 2021
lvis_month = 8
lvis_doy = 218

# SUMMER months: July (7), August (8), September (9)
# 1 month buffer before August: July
# 1 month buffer after August: September
summer_months = [7, 8, 9]
month_names = {7: 'July', 8: 'August', 9: 'September'}

print(f"\n  LVIS acquisition: Year {lvis_year}, Month {lvis_month} (August 6), DOY {lvis_doy}")
print(f"Filtering to: Summer season 2021 (July, August, September)")
print(f"1 month buffer BEFORE August: July")
print(f"LVIS month: August")
print(f"1 month buffer AFTER August: September")

# STRICT FILTERING: Year must match, Month must be in summer
# Does NOT restrict to just August - allows July and September too
lai_hem_filtered = lai_hem[(lai_hem['year'] == lvis_year) & (lai_hem['month'].isin(summer_months))].copy()
lai_lph_filtered = lai_lph[(lai_lph['year'] == lvis_year) & (lai_lph['month'].isin(summer_months))].copy()

print(f"\n  After date filtering (July-September 2021):")
print(f"HEM: {len(lai_hem_filtered)} points (from {len(lai_hem)})")

# Breakdown by month for HEM
for month in summer_months:
    count = len(lai_hem_filtered[lai_hem_filtered['month'] == month])
    print(f"      {month_names[month]}: {count} points")

print(f"\nLPH: {len(lai_lph_filtered)} points (from {len(lai_lph)})")

# Breakdown by month for LPH
for month in summer_months:
    count = len(lai_lph_filtered[lai_lph_filtered['month'] == month])
    print(f"{month_names[month]}: {count} points")

# Show breakdown of what was rejected
print(f"\nData rejected (different years):")

years_rejected_hem = set(lai_hem['year'].unique()) - {lvis_year}
years_rejected_lph = set(lai_lph['year'].unique()) - {lvis_year}

if years_rejected_hem:
    for year in sorted(years_rejected_hem):
        count = len(lai_hem[lai_hem['year'] == year])
        print(f"HEM Year {year}: {count} points rejected")
else:
    print(f"HEM: No other years in data ✓")

if years_rejected_lph:
    for year in sorted(years_rejected_lph):
        count = len(lai_lph[lai_lph['year'] == year])
        print(f"LPH Year {year}: {count} points rejected")
else:
    print(f"LPH: No other years in data ✓")

# Check if we have data
if len(lai_hem_filtered) == 0:
    print(f"\nWARNING: No HEM LAI data found for July-September 2021!")
    print(f"Available data is from different years or months. Check your data.")

if len(lai_lph_filtered) == 0:
    print(f"\nWARNING: No LPH LAI data found for July-September 2021!")
    print(f"Available data is from different years or months. Check your data.")


## C: CREATE QGIS VISUALIZATION - ALL LVIS WAVEFORMS (BEFORE FILTERING)

print("\n[3]Creating GeoPackage for all LVIS waveform locations...")

# Create GeoDataFrame from all LVIS
lvis_gdf = gpd.GeoDataFrame(
    lvis_df_all,
    geometry=gpd.points_from_xy(lvis_df_all['lon'], lvis_df_all['lat']),
    crs='EPSG:4326'
)

# Add some metadata
lvis_gdf['height_m'] = lvis_gdf['zt'] - lvis_gdf['zg']
lvis_gdf['shot_id'] = range(len(lvis_gdf))

# Save to GeoPackage
output_gpkg_all = 'lvis_waveforms_locations.gpkg'
lvis_gdf.to_file(output_gpkg_all, layer='LVIS_waveforms', driver='GPKG')
print(f"Saved: {output_gpkg_all}")
print(f"Contains {len(lvis_gdf)} LVIS shots from August 6, 2021")

## D: FIND CLOSEST LVIS FOR EACH LAI-Plot (ONE-TO-ONE MATCHING)

def find_closest_matches(lai_df, lvis_df, location_name='HEM'):
    """
    For EACH LAI point, find the SINGLE CLOSEST LVIS waveform.
    Returns one-to-one mapping.
    """
    
    print(f"\n[4-{location_name}] Finding CLOSEST LVIS waveform for each LAI point...")
    
    if len(lai_df) == 0:
        print(f"No data to process (filtered dataset is empty)")
        return pd.DataFrame()
    
    lai_coords = lai_df[['latitude', 'longitude']].values
    lvis_coords = lvis_df[['lat', 'lon']].values
    
    # Calculate pairwise distances
    distances = cdist(lai_coords, lvis_coords, metric='euclidean') * 111  # km
    
    # For EACH LAI, find CLOSEST LVIS
    closest_indices = distances.argmin(axis=1)
    closest_distances = distances.min(axis=1)
    
    print(f"Distance statistics (km):")
    print(f"Min: {closest_distances.min():.3f}")
    print(f"Max: {closest_distances.max():.3f}")
    print(f"Mean: {closest_distances.mean():.3f}")
    print(f"Median: {np.median(closest_distances):.3f}")
    
    # Create matched dataset - ONE LVIS per LAI
    matches = []
    
    for lai_idx in range(len(lai_df)):
        lvis_idx = closest_indices[lai_idx]
        dist_km = closest_distances[lai_idx]
        
        lai_row = lai_df.iloc[lai_idx]
        lvis_row = lvis_df.iloc[lvis_idx]
        
        matches.append({
            'lai_index': lai_idx,
            'lvis_index': lvis_idx,
            'shot_number': int(lvis_row['shotnumber']),
            'lai_value': lai_row['lai_value'],
            'lai_date': lai_row['date'],
            'lai_year': lai_row['year'],
            'lai_month': lai_row['month'],
            'lai_month_name': month_names.get(lai_row['month'], 'Unknown'),
            'lai_doy': lai_row['doy'],
            'distance_km': dist_km,
            'lvis_lat': lvis_row['lat'],
            'lvis_lon': lvis_row['lon'],
            'lvis_zt': lvis_row['zt'],
            'lvis_zg': lvis_row['zg'],
            'lvis_height': lvis_row['zt'] - lvis_row['zg'],
            'source_file': lvis_row['source_file'],
        })
    
    matches_df = pd.DataFrame(matches)
    print(f"Matched {len(matches_df)} LAI-to-LVIS pairs (1-to-1)")
    print(f"All from 2021 summer season (Jul-Aug-Sep)")
    
    return matches_df


# Get matches for HEM and LPH
matches_hem = find_closest_matches(lai_hem_filtered, lvis_df_all, 'HEM')
matches_lph = find_closest_matches(lai_lph_filtered, lvis_df_all, 'LPH')

## E: CREATE QGIS VISUALIZATION - FILTERED LVIS (AFTER MATCHING)

print("\n[5]Creating filtered GeoPackages for QGIS visualization...")

if len(matches_hem) > 0:
    # HEM filtered
    hem_matched_gdf = gpd.GeoDataFrame(
        matches_hem,
        geometry=gpd.points_from_xy(matches_hem['lvis_lon'], matches_hem['lvis_lat']),
        crs='EPSG:4326'
    )
    
    hem_output_gpkg = 'lvis_filtered_hem.gpkg'
    hem_matched_gdf.to_file(hem_output_gpkg, layer='LVIS_HEM_filtered', driver='GPKG')
    print(f"Saved: {hem_output_gpkg}")
    print(f"Records: {len(hem_matched_gdf)}")
else:
    print(f"HEM: No data to save (no matches found)")
    hem_output_gpkg = None
    hem_matched_gdf = None

if len(matches_lph) > 0:
    # LPH filtered
    lph_matched_gdf = gpd.GeoDataFrame(
        matches_lph,
        geometry=gpd.points_from_xy(matches_lph['lvis_lon'], matches_lph['lvis_lat']),
        crs='EPSG:4326'
    )
    
    lph_output_gpkg = 'lvis_filtered_lph.gpkg'
    lph_matched_gdf.to_file(lph_output_gpkg, layer='LVIS_LPH_filtered', driver='GPKG')
    print(f"Saved: {lph_output_gpkg}")
    print(f"Records: {len(lph_matched_gdf)}")
else:
    print(f"LPH: No data to save (no matches found)")
    lph_output_gpkg = None
    lph_matched_gdf = None


## F: EXTRACT WAVEFORMS FOR CLOSEST MATCHES ONLY

def decompose_waveform(rxwave, sigmean=None):
    """Decompose waveform into canopy and ground components"""
    
    if rxwave is None or len(rxwave) == 0:
        return None
    
    rxwave = np.asarray(rxwave, dtype=float)
    
    # Denoise
    if sigmean is not None and sigmean > 0:
        threshold = 3 * sigmean
        rxwave_clean = np.where(rxwave > threshold, rxwave, 0)
    else:
        threshold = np.mean(rxwave[rxwave > 0]) if np.sum(rxwave > 0) > 0 else np.mean(rxwave)
        rxwave_clean = np.where(rxwave > threshold/2, rxwave, 0)
    
    # Smooth
    if len(rxwave_clean[rxwave_clean > 0]) > 3:
        rxwave_smooth = gaussian_filter1d(rxwave_clean, sigma=1.0)
    else:
        rxwave_smooth = rxwave_clean
    
    # Split into canopy (top 70%) and ground (bottom 30%)
    n = len(rxwave_smooth)
    split_idx = int(0.7 * n)
    
    canopy_energy = np.sum(rxwave_smooth[:split_idx])
    ground_energy = np.sum(rxwave_smooth[split_idx:])
    total_energy = np.sum(rxwave_smooth)
    
    metrics = {
        'rv0_canopy': canopy_energy,
        'rg_ground': ground_energy,
        'total_energy': total_energy,
        'waveform_length': n,
        'peak_amplitude': np.max(rxwave_smooth),
        'mean_amplitude': np.mean(rxwave_smooth[rxwave_smooth > 0]) if np.sum(rxwave_smooth > 0) > 0 else 0,
    }
    
    return metrics


def calculate_waveform_rh_metrics(rxwave):
    """Calculate relative height (RH) percentiles"""
    
    if rxwave is None or len(rxwave) == 0:
        return None
    
    rxwave = np.asarray(rxwave, dtype=float)
    cumsum = np.cumsum(rxwave)
    total = cumsum[-1]
    
    if total <= 0:
        return None
    
    rh_metrics = {}
    for percentile in [25, 50, 75, 100]:
        threshold = (percentile / 100.0) * total
        idx = np.searchsorted(cumsum, threshold)
        rh_metrics[f'rh{percentile}'] = min(idx / len(rxwave), 1.0)
    
    return rh_metrics


def extract_waveforms_for_matches(matches_df, all_lvis_data, location_name):
    """Extract waveforms only for closest-matched shots"""
    
    print(f"\n[6-{location_name}] Extracting waveforms for closest matches only...")
    
    if len(matches_df) == 0:
        print(f"No matches to process")
        return pd.DataFrame()
    
    waveform_metrics = []
    
    for idx, row in matches_df.iterrows():
        source_file = row['source_file']
        lvis_idx = int(row['lvis_index'])
        
        # Get the waveform data
        if source_file in all_lvis_data:
            lvis_data = all_lvis_data[source_file]
            
            if 'RXWAVE' in lvis_data:
                try:
                    rxwave = lvis_data['RXWAVE'][lvis_idx]
                    
                    # Decompose
                    decomp = decompose_waveform(rxwave, sigmean=lvis_data.get('SIGMEAN', [None])[lvis_idx] if 'SIGMEAN' in lvis_data else None)
                    
                    # RH metrics
                    rh = calculate_waveform_rh_metrics(rxwave)
                    
                    if decomp is not None and rh is not None:
                        metrics = {
                            'shot_number': row['shot_number'],
                            'lai_value': row['lai_value'],
                            'lai_date': str(row['lai_date']),
                            'lai_year': row['lai_year'],
                            'lai_month': row['lai_month'],
                            'lai_month_name': row['lai_month_name'],
                            'distance_km': row['distance_km'],
                            'lvis_height': row['lvis_height'],
                        }
                        metrics.update(decomp)
                        metrics.update(rh)
                        waveform_metrics.append(metrics)
                
                except Exception as e:
                    print(f"    Error extracting waveform for shot {row['shot_number']}: {e}")
    
    waveform_df = pd.DataFrame(waveform_metrics)
    print(f"Extracted {len(waveform_df)} waveforms")
    
    return waveform_df


# Extract for HEM and LPH
waveform_hem = extract_waveforms_for_matches(matches_hem, all_lvis_data, 'HEM')
waveform_lph = extract_waveforms_for_matches(matches_lph, all_lvis_data, 'LPH')

## G: SAVE FINAL FILTERED WAVEFORM METRICS

print("\n[7] Saving final filtered waveform metrics...")

if len(waveform_hem) > 0:
    hem_output_csv = 'lvis_waveform_metrics_filtered_hem.csv'
    waveform_hem.to_csv(hem_output_csv, index=False)
    print(f"Saved: {hem_output_csv}")
else:
    print(f"HEM: No waveforms to save")
    hem_output_csv = None

if len(waveform_lph) > 0:
    lph_output_csv = 'lvis_waveform_metrics_filtered_lph.csv'
    waveform_lph.to_csv(lph_output_csv, index=False)
    print(f"Saved: {lph_output_csv}")
else:
    print(f"LPH: No waveforms to save")
    lph_output_csv = None

## H: FINAL SUMMARY AND STATISTICS

print("\n" + "="*70)
print("FINAL SUMMARY - SUMMER 2021 (JULY-SEPTEMBER WITH BUFFERS)")
print("="*70)
print(f"\nTEMPORAL FILTERING APPLIED:")
print(f"YEAR: 2021 only")
print(f"MONTHS: July, August, September (1 month buffer before & after)")
print(f"July (buffer before LVIS): ")
print(f"August (LVIS month): ")
print(f"September (buffer after LVIS): ")
print(f"All other years REJECTED")
print(f"\nHEMLOCK (HEM):")
print(f"Original LAI points: {len(lai_hem)}")
print(f"LAI points in summer 2021: {len(lai_hem_filtered)}")
if len(lai_hem_filtered) > 0:
    print(f"  Matched LVIS waveforms (1-to-1): {len(matches_hem)}")
    print(f"  Waveforms extracted: {len(waveform_hem)}")
    if len(waveform_hem) > 0:
        print(f"  LAI range: {waveform_hem['lai_value'].min():.2f} - {waveform_hem['lai_value'].max():.2f}")
        print(f"  Distance range: {waveform_hem['distance_km'].min():.3f} - {waveform_hem['distance_km'].max():.3f} km")
        print(f"  Mean distance: {waveform_hem['distance_km'].mean():.3f} km")
        # Breakdown by month
        for month in summer_months:
            count = len(waveform_hem[waveform_hem['lai_month'] == month])
            print(f"    {month_names[month]}: {count} measurements")
        if len(waveform_hem) > 5:
            corr = waveform_hem[['lai_value', 'rh100']].corr().iloc[0, 1]
            print(f"  LAI vs RH100 correlation: {corr:.3f}")
else:
    print(f"No data for summer 2021")

print(f"\nLITTLE PROSPECT HILL (LPH):")
print(f"Original LAI points: {len(lai_lph)}")
print(f"LAI points in summer 2021: {len(lai_lph_filtered)}")
if len(lai_lph_filtered) > 0:
    print(f"  Matched LVIS waveforms (1-to-1): {len(matches_lph)}")
    print(f"  Waveforms extracted: {len(waveform_lph)}")
    if len(waveform_lph) > 0:
        print(f"  LAI range: {waveform_lph['lai_value'].min():.2f} - {waveform_lph['lai_value'].max():.2f}")
        print(f"  Distance range: {waveform_lph['distance_km'].min():.3f} - {waveform_lph['distance_km'].max():.3f} km")
        print(f"  Mean distance: {waveform_lph['distance_km'].mean():.3f} km")
        # Breakdown by month
        for month in summer_months:
            count = len(waveform_lph[waveform_lph['lai_month'] == month])
            print(f"{month_names[month]}: {count} measurements")
        if len(waveform_lph) > 5:
            corr = waveform_lph[['lai_value', 'rh100']].corr().iloc[0, 1]
            print(f"LAI vs RH100 correlation: {corr:.3f}")
else:
    print(f"No data for summer 2021")

print(f"\nOUTPUT FILES FOR QGIS:")
print(f"  1. {output_gpkg_all}")
print(f"     > All LVIS waveform locations (August 6, 2021)")

if hem_output_gpkg:
    print(f"  2. {hem_output_gpkg}")
    print(f"     > HEM: LVIS waveforms matched to summer 2021 LAI")
else:
    print(f"  2. No HEM output (no summer 2021 data)")

if lph_output_gpkg:
    print(f"  3. {lph_output_gpkg}")
    print(f"     > LPH: LVIS waveforms matched to summer 2021 LAI")
else:
    print(f"  3. No LPH output (no summer 2021 data)")

print(f"\nOUTPUT FILES FOR ANALYSIS:")
if hem_output_csv:
    print(f"  1. {hem_output_csv}")
else:
    print(f"  1. No HEM output")

if lph_output_csv:
    print(f"  2. {lph_output_csv}")
else:
    print(f"  2. No LPH output")

print(f"\nIMPORTANT NOTE:")
print(f"  > YEAR: Included 2021 only (no other years)")
print(f"  > MONTHS: July, August, September (with 1 month buffers)")
print(f"  > All matches are from SAME year + summer season")
print(f"  > Maximum temporal flexibility while keeping year consistent")

print(f"\n" + "="*70)
print("**FILTERING AND EXTRACTION COMPLETE!**")
print("="*70)
