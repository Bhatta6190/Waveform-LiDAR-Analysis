#!/usr/bin/env python3
"""
LVIS-LAI MATCHING WITH FULL WAVEFORM + COMPLETE ATTRIBUTES
"""
## Importing necessary libraries
import h5py
import pandas as pd
import numpy as np
import json
import pickle
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

try:
    import xarray as xr
    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False
    print("Warning: xarray not installed. NetCDF output will be skipped.")

print("="*70)
print("LVIS-LAI MATCHING WITH FULL WAVEFORM + COMPLETE ATTRIBUTES")
print("="*70)

## A: LOAD BOTH LVIS FILES

print("\n[1]Loading LVIS data from both H5 files...")

lvis_files = [
    'LVISC1B_GEDI2021_0806_R2112_049718.h5',
    'LVISC1B_GEDI2021_0806_R2112_051257.h5'
]

all_lvis_data = {}
all_lvis_df_list = []

for lvis_file in lvis_files:
    print(f"\nLoading: {lvis_file}")
    
    try:
        lvis_hdf = h5py.File(lvis_file, 'r')
        
        lvis_data = {}
        for key in lvis_hdf.keys():
            if key != 'ancillary_data':
                lvis_data[key] = np.array(lvis_hdf[key])
        
        # Create DataFrame with EXACT field names from HDF5
        lvis_df = pd.DataFrame({
            'SHOTNUMBER': lvis_data['SHOTNUMBER'],
            'LAT0': lvis_data['LAT0'],
            'LAT1023': lvis_data['LAT1023'],
            'LON0': lvis_data['LON0'],
            'LON1023': lvis_data['LON1023'],
            'Z0': lvis_data['Z0'],
            'Z1023': lvis_data['Z1023'],
            'SIGMEAN': lvis_data['SIGMEAN'],  # EXACT NAME
            'TIME': lvis_data['TIME'],
            'AZIMUTH': lvis_data['AZIMUTH'],  # EXACT NAME
            'INCIDENTANGLE': lvis_data['INCIDENTANGLE'],  # EXACT NAME
            'LFID': lvis_data['LFID'],  # EXACT NAME
            'RANGE': lvis_data['RANGE'],  # EXACT NAME
            'TXWAVE': list(lvis_data['TXWAVE']),
            'RXWAVE': list(lvis_data['RXWAVE']),
        })
        
        # Add computed fields
        lvis_df['lat'] = (lvis_df['LAT0'] + lvis_df['LAT1023']) / 2.0
        lvis_df['lon_raw'] = (lvis_df['LON0'] + lvis_df['LON1023']) / 2.0
        lvis_df['lon'] = np.where(
            lvis_df['lon_raw'] > 180,
            lvis_df['lon_raw'] - 360,
            lvis_df['lon_raw']
        )
        lvis_df['zt'] = np.maximum(lvis_df['Z0'], lvis_df['Z1023'])
        lvis_df['zg'] = np.minimum(lvis_df['Z0'], lvis_df['Z1023'])
        lvis_df['source_file'] = lvis_file
        
        all_lvis_df_list.append(lvis_df)
        all_lvis_data[lvis_file] = lvis_data
        
        print(f"Loaded {len(lvis_df)} shots")
        print(f"Fields: {[k for k in lvis_data.keys() if k != 'ancillary_data']}")
        
        lvis_hdf.close()
    
    except Exception as e:
        print(f"Error: {e}")

lvis_df_all = pd.concat(all_lvis_df_list, ignore_index=True)
print(f"\nTotal LVIS shots: {len(lvis_df_all)}")
print(f"Columns: {list(lvis_df_all.columns)}")


## B: LOAD LAI DATA AND FILTER

print("\n[2] Loading LAI data and filtering to summer 2021...")

lai_hem = pd.read_csv('hf150_geolocated_hem_lai.csv')
lai_lph = pd.read_csv('hf150_geolocated_lph_lai.csv')

lai_hem['date'] = pd.to_datetime(lai_hem['date'])
lai_lph['date'] = pd.to_datetime(lai_lph['date'])

lai_hem['year'] = lai_hem['date'].dt.year
lai_hem['month'] = lai_hem['date'].dt.month
lai_lph['year'] = lai_lph['date'].dt.year
lai_lph['month'] = lai_lph['date'].dt.month

summer_months = [7, 8, 9]
month_names = {7: 'July', 8: 'August', 9: 'September'}

lai_hem_filtered = lai_hem[(lai_hem['year'] == 2021) & (lai_hem['month'].isin(summer_months))].copy()
lai_lph_filtered = lai_lph[(lai_lph['year'] == 2021) & (lai_lph['month'].isin(summer_months))].copy()

print(f"HEM: {len(lai_hem_filtered)} points in summer 2021")
print(f"LPH: {len(lai_lph_filtered)} points in summer 2021")

## C: FIND CLOSEST LVIS FOR EACH LAI

def find_closest_matches_with_all_attributes(lai_df, lvis_df, all_lvis_data, location_name='HEM'):
    """Find closest LVIS for each LAI and store ALL attributes with EXACT names"""
    
    print(f"\n[3-{location_name}] Finding closest LVIS and extracting ALL attributes...")
    
    if len(lai_df) == 0:
        print(f"No data to process")
        return [], []
    
    lai_coords = lai_df[['latitude', 'longitude']].values
    lvis_coords = lvis_df[['lat', 'lon']].values
    
    distances = cdist(lai_coords, lvis_coords, metric='euclidean') * 111
    
    closest_indices = distances.argmin(axis=1)
    closest_distances = distances.min(axis=1)
    
    print(f"Distance statistics (km):")
    print(f"Min: {closest_distances.min():.3f}")
    print(f"Max: {closest_distances.max():.3f}")
    print(f"Mean: {closest_distances.mean():.3f}")
    print(f"Matches found: {len(closest_distances)}")
    
    matches = []
    waveforms_data = []
    
    for lai_idx in range(len(lai_df)):
        lvis_idx = closest_indices[lai_idx]
        dist_km = closest_distances[lai_idx]
        
        lai_row = lai_df.iloc[lai_idx]
        lvis_row = lvis_df.iloc[lvis_idx]
        
        # Basic match info
        match_info = {
            'lai_value': lai_row['lai_value'],
            'lai_date': lai_row['date'],
            'lai_month_name': month_names.get(lai_row['month'], 'Unknown'),
            'distance_km': dist_km,
        }
        
        # Add ALL LVIS attributes with EXACT field names
        for col in lvis_row.index:
            if col not in ['RXWAVE', 'TXWAVE']:
                match_info[f'lvis_{col}'] = lvis_row[col]
        
        # Store waveform separately (array data)
        waveform_info = {
            'shot_number': int(lvis_row['SHOTNUMBER']),
            'lai_value': lai_row['lai_value'],
            'distance_km': dist_km,
            'SIGMEAN': float(lvis_row['SIGMEAN']),  # Explicitly include SIGMEAN
            'AZIMUTH': float(lvis_row['AZIMUTH']),  # Explicitly include AZIMUTH
            'INCIDENTANGLE': float(lvis_row['INCIDENTANGLE']),  # Explicitly include
            'LFID': int(lvis_row['LFID']),
            'RANGE': float(lvis_row['RANGE']),
            'TIME': float(lvis_row['TIME']),
        }
        
        # Get full waveforms from original file
        source_file = lvis_row['source_file']
        if source_file in all_lvis_data:
            lvis_data = all_lvis_data[source_file]
            
            if 'RXWAVE' in lvis_data:
                try:
                    rxwave = lvis_data['RXWAVE'][lvis_idx]
                    waveform_info['rxwave'] = np.array(rxwave)
                    waveform_info['rxwave_length'] = len(rxwave)
                except:
                    waveform_info['rxwave'] = None
                    waveform_info['rxwave_length'] = 0
            
            if 'TXWAVE' in lvis_data:
                try:
                    txwave = lvis_data['TXWAVE'][lvis_idx]
                    waveform_info['txwave'] = np.array(txwave)
                    waveform_info['txwave_length'] = len(txwave)
                except:
                    waveform_info['txwave'] = None
                    waveform_info['txwave_length'] = 0
        
        matches.append(match_info)
        waveforms_data.append(waveform_info)
    
    matches_df = pd.DataFrame(matches)
    
    print(f"Matched {len(matches_df)} pairs with ALL attributes")
    print(f"LVIS fields extracted: {sum(1 for c in matches_df.columns if c.startswith('lvis_'))}")
    print(f"SIGMEAN in output: {'lvis_SIGMEAN' in matches_df.columns}")
    
    return matches_df, waveforms_data

# Get matches
matches_hem, waveforms_hem = find_closest_matches_with_all_attributes(
    lai_hem_filtered, lvis_df_all, all_lvis_data, 'HEM'
)
matches_lph, waveforms_lph = find_closest_matches_with_all_attributes(
    lai_lph_filtered, lvis_df_all, all_lvis_data, 'LPH'
)

## D: SAVE IN MULTIPLE FORMATS

def save_all_formats(location_name, matches_df, waveforms_data):
    """Save in HDF5, Pickle, and CSV formats"""
    
    print(f"\n[4-{location_name}] Saving in multiple formats...")
    
    if len(matches_df) == 0:
        print(f"No data to save")
        return {}
    
    # FORMAT 1: HDF5
    h5_file = f'lvis_full_waveforms_{location_name.lower()}.h5'
    
    with h5py.File(h5_file, 'w') as hf:
        for i, wf_data in enumerate(waveforms_data):
            shot_group = hf.create_group(f'shot_{i:04d}')
            
            # Store scalars
            shot_group.attrs['shot_number'] = wf_data['shot_number']
            shot_group.attrs['lai_value'] = wf_data['lai_value']
            shot_group.attrs['distance_km'] = wf_data['distance_km']
            shot_group.attrs['SIGMEAN'] = wf_data['SIGMEAN']
            shot_group.attrs['AZIMUTH'] = wf_data['AZIMUTH']
            shot_group.attrs['INCIDENTANGLE'] = wf_data['INCIDENTANGLE']
            shot_group.attrs['LFID'] = wf_data['LFID']
            shot_group.attrs['RANGE'] = wf_data['RANGE']
            shot_group.attrs['TIME'] = wf_data['TIME']
            shot_group.attrs['rxwave_length'] = wf_data['rxwave_length']
            shot_group.attrs['txwave_length'] = wf_data['txwave_length']
            
            # Store waveforms
            if wf_data['rxwave'] is not None:
                shot_group.create_dataset('rxwave', data=wf_data['rxwave'])
            if wf_data['txwave'] is not None:
                shot_group.create_dataset('txwave', data=wf_data['txwave'])
            
            # Store all LVIS attributes
            match_row = matches_df.iloc[i]
            for col in matches_df.columns:
                if col.startswith('lvis_') and col not in ['lvis_RXWAVE', 'lvis_TXWAVE']:
                    try:
                        shot_group.attrs[col] = match_row[col]
                    except:
                        shot_group.attrs[col] = str(match_row[col])
    
    print(f"Saved: {h5_file}")
    
    # FORMAT 2: CSV
    csv_file = f'lvis_attributes_{location_name.lower()}.csv'
    matches_df.to_csv(csv_file, index=False)
    print(f"Saved: {csv_file}")
    print(f"SIGMEAN field included: {'lvis_SIGMEAN' in matches_df.columns}")
    
    # FORMAT 3: Pickle
    pkl_file = f'lvis_waveforms_{location_name.lower()}.pkl'
    pkl_data = {
        'location': location_name,
        'matches': matches_df,
        'waveforms': waveforms_data,
    }
    with open(pkl_file, 'wb') as f:
        pickle.dump(pkl_data, f)
    print(f"Saved: {pkl_file}")
    
    # FORMAT 4: JSON metadata
    json_file = f'lvis_metadata_{location_name.lower()}.json'
    json_data = {
        'location': location_name,
        'total_shots': len(waveforms_data),
        'fields_included': ['SIGMEAN', 'AZIMUTH', 'INCIDENTANGLE', 'LFID', 'RANGE', 'TIME'],
        'shots': []
    }
    
    for i, wf_data in enumerate(waveforms_data):
        json_data['shots'].append({
            'shot_number': int(wf_data['shot_number']),
            'lai_value': float(wf_data['lai_value']),
            'distance_km': float(wf_data['distance_km']),
            'SIGMEAN': float(wf_data['SIGMEAN']),
            'AZIMUTH': float(wf_data['AZIMUTH']),
            'INCIDENTANGLE': float(wf_data['INCIDENTANGLE']),
            'rxwave_length': int(wf_data['rxwave_length']),
            'txwave_length': int(wf_data['txwave_length']),
        })
    
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"Saved: {json_file}")
    
    return {
        'h5': h5_file,
        'csv': csv_file,
        'pkl': pkl_file,
        'json': json_file,
    }

# Save
hem_files = save_all_formats('HEM', matches_hem, waveforms_hem)
lph_files = save_all_formats('LPH', matches_lph, waveforms_lph)

## E: FINAL SUMMARY

print("\n" + "="*70)
print("COMPLETE - ALL FIELDS PRESERVED WITH EXACT NAMES")
print("="*70)

print(f"\nHEMLOCK (HEM):")
print(f"Matched pairs: {len(matches_hem)}")
if len(matches_hem) > 0:
    print(f"Columns: {len(matches_hem.columns)}")
    print(f"Fields preserved: SIGMEAN, AZIMUTH, INCIDENTANGLE, LFID, RANGE")

print(f"\nLITTLE PROSPECT HILL (LPH):")
print(f"Matched pairs: {len(matches_lph)}")

print(f"\nOUTPUT FILES - HEM:")
for fmt, fname in hem_files.items():
    print(f"  • {fname}")

print(f"\nOUTPUT FILES - LPH:")
for fmt, fname in lph_files.items():
    print(f"  • {fname}")
print(f"\n" + "="*70)
