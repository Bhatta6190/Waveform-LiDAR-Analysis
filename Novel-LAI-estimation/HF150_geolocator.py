#!/usr/bin/env python3
"""
HARVARD FOREST HF150 LAI GEOLOCATION CONVERTER WITH MAPPING

Purpose:
    Convert HF150 LAI data from polar coordinates (distance + bearing from tower)
    to absolute geographic coordinates (latitude/longitude) ready for spatial
    analysis with waveform lidar data. Additionally generates interactive maps
    showing all LAI measurement locations.

Features: Handles both HEM and LPH column naming conventions
    - HEM uses: lai_masked, sel
    - LPH uses: lai_masked, sel_masked (and lai_unmasked, sel_unmasked)
"""

## Import necessary libraries
import pandas as pd
import numpy as np
import sys
from pathlib import Path

## import optional visualization libraries
try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("Warning: folium not installed. Install with: pip install folium")

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not installed. Install with: pip install matplotlib")



## A: Input and output files/use same names as in HF150 dataset

INPUT_HEM_FILE = "hf150-01-hem-lai.csv"
INPUT_LPH_FILE = "hf150-02-lph-lai.csv"

OUTPUT_HEM_FILE = "hf150_geolocated_hem_lai.csv"
OUTPUT_LPH_FILE = "hf150_geolocated_lph_lai.csv"

OUTPUT_HEM_MAP_INTERACTIVE = "hf150_hem_map.html"
OUTPUT_LPH_MAP_INTERACTIVE = "hf150_lph_map.html"
OUTPUT_HEM_MAP_STATIC = "hf150_hem_plot.png"
OUTPUT_LPH_MAP_STATIC = "hf150_lph_plot.png"

## B: Tower reference coordinated: need them to convert into lat/lon coordinates

TOWER_COORDINATES = {
    'HEM': {
        'name': 'Hemlock Tower (US-Ha2)',
        'latitude': 42.539415,
        'longitude':-72.177848,
        'elevation': 360.0,
        'precision_m': 1.5,
        'source': 'Satellite + AmeriFlux'
    },
    'LPH': {
        'name': 'Little Prospect Hill Tower',
        'latitude': 42.5420,
        'longitude': -72.1850,
        'elevation': 380.0,
        'precision_m': 1.5,
        'source': 'HF414 PhenoCam LPH Tower'
    }
}

## These are two different towers and walk-up tower is not in use currently. Check HF data archive for more details/
# Hemlock Walk-up tower (old): 42.5394269, -72.1779735
# Hemlock tower (current): 42.539415, -72.177848

## C: Conversion function

def bearing_distance_to_latlon(tower_lat, tower_lon, distance_m, bearing_degrees):
    """
    Convert a measurement location (distance + bearing from a tower)
    to absolute geographic coordinates (latitude, longitude).
    """
    
    earth_radius_m = 6371000.0   # Approx
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


def add_geolocation_to_hf150(hf150_df, tower_id, tower_info):
    """Add latitude and longitude columns to HF150 data."""
    
    geolocated_df = hf150_df.copy()
    
    required_cols = ['distance', 'transect']
    missing_cols = [col for col in required_cols if col not in geolocated_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    lats = np.zeros(len(geolocated_df))
    lons = np.zeros(len(geolocated_df))
    
    for idx, row in geolocated_df.iterrows():
        lat, lon = bearing_distance_to_latlon(
            tower_lat=tower_info['latitude'],
            tower_lon=tower_info['longitude'],
            distance_m=row['distance'],
            bearing_degrees=row['transect']
        )
        lats[idx] = lat
        lons[idx] = lon
    
    geolocated_df['latitude'] = lats
    geolocated_df['longitude'] = lons
    geolocated_df['elevation_m'] = tower_info['elevation']
    geolocated_df['tower_id'] = tower_id
    
    return geolocated_df


def normalize_lai_columns(df, tower_id):
    """
    Normalize LAI column names to handle both HEM and LPH formats.
    
    HEM format: lai_masked, sel
    LPH format: lai_masked, sel_masked (and lai_unmasked, sel_unmasked)
    
    Output: Standardized columns 'lai_value' and 'lai_error'
    """
    
    df_normalized = df.copy()
    
    # Identify which columns are present
    if 'sel_masked' in df_normalized.columns:
        # LPH format: use masked versions
        df_normalized['lai_value'] = df_normalized['lai_masked']
        df_normalized['lai_error'] = df_normalized['sel_masked']
        print(f"Detected LPH format (using lai_masked, sel_masked)")
    elif 'sel' in df_normalized.columns:
        # HEM format: use direct columns
        df_normalized['lai_value'] = df_normalized['lai_masked']
        df_normalized['lai_error'] = df_normalized['sel']
        print(f"Detected HEM format (using lai_masked, sel)")
    else:
        raise ValueError("Cannot find LAI columns (expected 'sel' or 'sel_masked')")
    
    return df_normalized


def quality_check_geolocated_data(df, tower_id):
    """Perform quality checks on geolocated HF150 data."""
    
    print(f"\nQuality checks for {tower_id}:")
    
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"Missing values detected:")
        for col, count in missing[missing > 0].items():
            print(f"{col}: {count} rows")
    else:
        print(f"No missing values")
    
    lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
    lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
    
    print(f"Latitude:  {lat_min:.6f}° to {lat_max:.6f}°N")
    print(f"Longitude: {lon_min:.6f}° to {lon_max:.6f}°W")
    
    if 42.53 < lat_min and lat_max < 42.55 and -72.19 < lon_min and lon_max < -72.17:
        print(f"Coordinates within Harvard Forest bounds")
    else:
        print(f"Coordinates outside expected bounds!")
    
    lai_min, lai_max = df['lai_value'].min(), df['lai_value'].max()
    print(f"LAI range: {lai_min:.2f} to {lai_max:.2f}")
    
    if 2 < lai_min and lai_max < 8:
        print(f"LAI values within expected range")
    else:
        print(f"LAI values outside typical range!")
    
    print(f"Records: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")

## D. Mapping Function

def create_folium_map(df, tower_id, tower_info, output_file):
    """Create an interactive Folium map showing all LAI measurement locations."""
    
    if not FOLIUM_AVAILABLE:
        print(f"    ⚠️  Folium not available - skipping interactive map {output_file}")
        return
    
    print(f"    Creating interactive map: {output_file}")
    
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles='OpenStreetMap'
    )
    
    # Add tower marker
    folium.Marker(
        location=[tower_info['latitude'], tower_info['longitude']],
        popup=f"{tower_info['name']}<br>Elevation: {tower_info['elevation']} m",
        tooltip=f"Tower: {tower_id}",
        icon=folium.Icon(color='red', icon='tower', prefix='fa'),
        marker_color='red'
    ).add_to(m)
    
    # Add LAI measurement points with color-coding
    lai_values = df['lai_value'].values
    lai_min, lai_max = lai_values.min(), lai_values.max()
    
    for idx, row in df.iterrows():
        lai_normalized = (row['lai_value'] - lai_min) / (lai_max - lai_min + 1e-6)
        
        if lai_normalized < 0.33:
            color = 'green'
        elif lai_normalized < 0.66:
            color = 'blue'
        else:
            color = 'darkgreen'
        
        # Create popup with detailed information
        popup_text = f"""
        <b>LAI Measurement</b><br>
        Date: {row['date']}<br>
        LAI: {row['lai_value']:.2f} ± {row['lai_error']:.2f}<br>
        Lat: {row['latitude']:.6f}°<br>
        Lon: {row['longitude']:.6f}°<br>
        Distance from tower: {row['distance']:.1f} m<br>
        Bearing: {row['transect']:.1f}°
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"LAI: {row['lai_value']:.2f}",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Add a legend
    legend_html = f"""
    <div style="position: fixed; 
            bottom: 50px; right: 50px; width: 250px; height: 200px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:14px; padding: 10px">
    <p><b>{tower_info['name']}</b></p>
    <p><b>LAI Distribution:</b></p>
    <p><i class="fa fa-circle" style="color:green"></i> Low LAI ({lai_min:.2f}-{(lai_min+lai_max)/3:.2f})</p>
    <p><i class="fa fa-circle" style="color:blue"></i> Medium LAI ({(lai_min+lai_max)/3:.2f}-{2*(lai_min+lai_max)/3:.2f})</p>
    <p><i class="fa fa-circle" style="color:darkgreen"></i> High LAI ({2*(lai_min+lai_max)/3:.2f}-{lai_max:.2f})</p>
    <p><b>Records: {len(df)}</b></p>
    <p><b>Red marker:</b> Tower location</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    m.save(output_file)
    print(f"Interactive map saved: {output_file}")


def create_matplotlib_plot(df, tower_id, tower_info, output_file):
    """Create a static matplotlib plot showing all LAI measurement locations."""
    
    if not MATPLOTLIB_AVAILABLE:
        print(f"Matplotlib not available - skipping static plot {output_file}")
        return
    
    print(f"Creating static plot: {output_file}")
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    scatter = ax.scatter(
        df['longitude'], df['latitude'],
        c=df['lai_value'],
        cmap='RdYlGn',
        s=100,
        alpha=0.7,
        edgecolors='black',
        linewidth=1,
        vmin=df['lai_value'].min(),
        vmax=df['lai_value'].max()
    )
    
    ax.plot(
        tower_info['longitude'], tower_info['latitude'],
        'r*', markersize=20, label='Tower'
    )
    
    cbar = plt.colorbar(scatter, ax=ax, label='LAI (Leaf Area Index)')
    
    ax.set_xlabel('Longitude (°W)', fontsize=12)
    ax.set_ylabel('Latitude (°N)', fontsize=12)
    ax.set_title(f'{tower_info["name"]} - LAI Measurement Locations\n(n={len(df)} plots)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    stats_text = f"""Records: {len(df)}
LAI range: {df['lai_value'].min():.2f}-{df['lai_value'].max():.2f}
Mean LAI: {df['lai_value'].mean():.2f}
Date range: {df['date'].min()} to {df['date'].max()}"""
    
    ax.text(
        0.02, 0.98, stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f" Static plot saved: {output_file}")


## E: Main execution

def main():
    """Main execution function with mapping capabilities."""
    
    print("\n" + "=" * 80)
    print("HARVARD FOREST HF150 GEOLOCATION CONVERTER WITH MAPPING")
    print("=" * 80)
    
    # Step 1: Load input files
    print(f"\n[Step 1] Loading HF150 data files...")
    
    try:
        hf150_hem = None
        hf150_lph = None
        
        if Path(INPUT_HEM_FILE).exists():
            print(f"  Loading: {INPUT_HEM_FILE}")
            hf150_hem = pd.read_csv(INPUT_HEM_FILE)
            print(f"Loaded {len(hf150_hem)} rows from Hemlock tower")
        else:
            print(f"File not found: {INPUT_HEM_FILE}")
        
        if Path(INPUT_LPH_FILE).exists():
            print(f"  Loading: {INPUT_LPH_FILE}")
            hf150_lph = pd.read_csv(INPUT_LPH_FILE)
            print(f"Loaded {len(hf150_lph)} rows from LPH tower")
        else:
            print(f"File not found: {INPUT_LPH_FILE}")
        
        if hf150_hem is None and hf150_lph is None:
            print("\nx ERROR: Could not load any HF150 files!")
            return False
    
    except Exception as e:
        print(f"\nx ERROR loading files: {e}")
        return False
    
    # Step 2: Add geolocation
    print(f"\n[Step 2] Converting coordinates to geolocated data...")
    
    datasets_to_process = []
    
    if hf150_hem is not None:
        print(f"Processing Hemlock tower data...")
        hf150_hem_geolocated = add_geolocation_to_hf150(
            hf150_df=hf150_hem,
            tower_id='HEM',
            tower_info=TOWER_COORDINATES['HEM']
        )
        hf150_hem_geolocated = normalize_lai_columns(hf150_hem_geolocated, 'HEM')
        datasets_to_process.append(('HEM', hf150_hem_geolocated, OUTPUT_HEM_FILE, 
                                   OUTPUT_HEM_MAP_INTERACTIVE, OUTPUT_HEM_MAP_STATIC))
        print(f"Added latitude/longitude columns")
    
    if hf150_lph is not None:
        print(f"Processing Little Prospect Hill tower data...")
        hf150_lph_geolocated = add_geolocation_to_hf150(
            hf150_df=hf150_lph,
            tower_id='LPH',
            tower_info=TOWER_COORDINATES['LPH']
        )
        hf150_lph_geolocated = normalize_lai_columns(hf150_lph_geolocated, 'LPH')
        datasets_to_process.append(('LPH', hf150_lph_geolocated, OUTPUT_LPH_FILE,
                                   OUTPUT_LPH_MAP_INTERACTIVE, OUTPUT_LPH_MAP_STATIC))
        print(f"Added latitude/longitude columns")
    
    # Step 3: Organize columns and quality checks
    print(f"\n[Step 3] Organizing columns and performing quality checks...")
    
    for tower_id, geolocated_df, output_csv, output_map_html, output_map_png in datasets_to_process:
        
        # Select standard output columns
        available_cols = [col for col in geolocated_df.columns 
                         if col not in ['lai_unmasked', 'sel_unmasked']]
        final_df = geolocated_df[available_cols].copy()
        
        # Quality checks
        quality_check_geolocated_data(final_df, tower_id)
        
        # Step 4: Save output CSV
        print(f"\n  Saving {tower_id} data to: {output_csv}")
        final_df.to_csv(output_csv, index=False)
        print(f"CSV file saved: {output_csv}")
        print(f"{len(final_df)} records written")
        
        # Step 5: Generate maps
        print(f"\nGenerating maps for {tower_id}...")
        
        create_folium_map(final_df, tower_id, TOWER_COORDINATES[tower_id], output_map_html)
        create_matplotlib_plot(final_df, tower_id, TOWER_COORDINATES[tower_id], output_map_png)
    
    # Final Summary
    print("\n" + "=" * 80)
    print("CONVERSION AND MAPPING COMPLETE")
    print("=" * 80)
    
    print(f"""
OUTPUT FILES CREATED:

CSV Files (for analysis):
  • {OUTPUT_HEM_FILE}
  • {OUTPUT_LPH_FILE}

Interactive Maps (open in web browser):
  • {OUTPUT_HEM_MAP_INTERACTIVE}
  • {OUTPUT_LPH_MAP_INTERACTIVE}

Static Plots (saved as PNG):
  • {OUTPUT_HEM_MAP_STATIC}
  • {OUTPUT_LPH_MAP_STATIC}

NEXT STEPS:
  1. View interactive maps: Open .html files in web browser
  2. View static plots: Open .png files in image viewer
  3. Load CSV files into your analysis pipeline
  4. Spatial join with waveform lidar/other data using (latitude, longitude)
  5. Compare waveform-derived LAI against lai_value (ground truth)
""")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
