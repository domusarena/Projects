#!/usr/bin/env python3
"""
Extract Crown Land shapes from AUSTEN GeoTIFF (Memory-Efficient Version)
Extracts only a small sample for demonstration purposes
"""

import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape, box
import numpy as np
from datetime import datetime

def extract_crown_land_sample(tif_path, output_geojson, output_csv, max_features=50):
    """
    Extract a small sample of Crown Land polygons.
    
    Crown Land = Level 1 code 2 (values 2000-2999)
    
    Args:
        tif_path: Path to the GeoTIFF file
        output_geojson: Path to save GeoJSON output
        output_csv: Path to save CSV output
        max_features: Maximum number of features to extract (default 50)
    """
    
    print("="*80)
    print("CROWN LAND SAMPLE EXTRACTION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    with rasterio.open(tif_path) as src:
        print(f"\n📁 File: {tif_path}")
        print(f"   CRS: {src.crs}")
        print(f"   Size: {src.width} x {src.height} pixels")
        
        # Read a window from the center of the raster
        # This is much more memory-efficient than reading the entire file
        center_x = src.width // 2
        center_y = src.height // 2
        window_size = 2000  # 2000x2000 pixel window
        
        window = rasterio.windows.Window(
            center_x - window_size // 2,
            center_y - window_size // 2,
            window_size,
            window_size
        )
        
        print(f"\n📊 Reading {window_size}x{window_size} pixel window from center...")
        data = src.read(1, window=window)
        transform = src.window_transform(window)
        
        # Create mask for Crown land (values 2000-2999)
        crown_mask = (data >= 2000) & (data < 3000) & (data != src.nodata)
        
        crown_pixels = np.sum(crown_mask)
        print(f"   Crown Land pixels in window: {crown_pixels:,}")
        
        if crown_pixels == 0:
            print("⚠️  No Crown Land pixels in this window!")
            return None
        
        # Extract shapes
        print(f"\n🔄 Extracting polygons (max {max_features})...")
        features = []
        
        for geom, value in shapes(data, mask=crown_mask, transform=transform):
            if len(features) >= max_features:
                break
            
            features.append({
                'geometry': shape(geom),
                'tenure_code': int(value)
            })
        
        print(f"   ✓ Extracted {len(features)} features")
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(features, crs=src.crs)
        
        # Add classifications
        print("\n🏷️  Adding classifications...")
        gdf['L1N'] = (gdf['tenure_code'] // 1000).astype(int)
        gdf['L2N'] = (gdf['tenure_code'] // 100).astype(int)
        gdf['L3N'] = (gdf['tenure_code'] // 10).astype(int)
        
        # Add descriptions
        l2_desc = {10: "Freehold", 21: "Leasehold", 22: "Crown purposes", 23: "Other Crown land"}
        l3_desc = {
            211: "Freeholding lease", 212: "Pastoral perpetual lease",
            213: "Other perpetual lease", 214: "Pastoral term lease",
            215: "Other term lease", 216: "Other lease",
            221: "Nature conservation reserve", 222: "Multiple-use public forest",
            223: "Other Crown purposes", 230: "Other Crown land"
        }
        
        gdf['L1_DESC'] = gdf['L1N'].apply(lambda x: "Crown land" if x == 2 else "Freehold")
        gdf['L2_DESC'] = gdf['L2N'].apply(lambda x: l2_desc.get(x, "Unknown"))
        gdf['L3_DESC'] = gdf['L3N'].apply(lambda x: l3_desc.get(x, "Unknown"))
        
        # Calculate area
        gdf['area_m2'] = gdf.geometry.area
        gdf['area_km2'] = gdf['area_m2'] / 1_000_000
        
        # Convert to WGS84 (lat/lon)
        print("🌐 Converting to WGS84...")
        gdf_wgs84 = gdf.to_crs('EPSG:4326')
        
        # Add centroid
        gdf_wgs84['centroid_lon'] = gdf_wgs84.geometry.centroid.x
        gdf_wgs84['centroid_lat'] = gdf_wgs84.geometry.centroid.y
        
        # Add bounding box
        bounds = gdf_wgs84.geometry.bounds
        gdf_wgs84['bbox_west'] = bounds.minx
        gdf_wgs84['bbox_south'] = bounds.miny
        gdf_wgs84['bbox_east'] = bounds.maxx
        gdf_wgs84['bbox_north'] = bounds.maxy
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Features extracted: {len(gdf_wgs84)}")
        print(f"Total area: {gdf_wgs84['area_km2'].sum():.2f} km²")
        print(f"\nBy Level 2:")
        for desc, group in gdf_wgs84.groupby('L2_DESC'):
            print(f"  {desc:30s}: {len(group):3d} features, {group['area_km2'].sum():8.2f} km²")
        
        print(f"\nBy Level 3:")
        for desc, group in gdf_wgs84.groupby('L3_DESC'):
            print(f"  {desc:30s}: {len(group):3d} features, {group['area_km2'].sum():8.2f} km²")
        
        # Save GeoJSON
        print(f"\n💾 Saving GeoJSON to: {output_geojson}")
        gdf_wgs84.to_file(output_geojson, driver='GeoJSON')
        print("   ✓ GeoJSON saved")
        
        # Prepare CSV with geometry as WKT in last column
        print(f"\n💾 Saving CSV to: {output_csv}")
        csv_data = gdf_wgs84.copy()
        
        # Convert geometry to WKT (Well-Known Text) format for CSV
        csv_data['geometry_wkt'] = csv_data.geometry.apply(lambda geom: geom.wkt)
        
        # Drop the geometry column and reorganize columns
        csv_data = csv_data.drop(columns=['geometry'])
        
        # Reorder columns: tenure info first, then spatial data, geometry last
        column_order = [
            'tenure_code',
            'L1N', 'L1_DESC',
            'L2N', 'L2_DESC', 
            'L3N', 'L3_DESC',
            'area_m2', 'area_km2',
            'centroid_lon', 'centroid_lat',
            'bbox_west', 'bbox_south', 'bbox_east', 'bbox_north',
            'geometry_wkt'
        ]
        
        csv_data = csv_data[column_order]
        
        # Save to CSV
        csv_data.to_csv(output_csv, index=False)
        print("   ✓ CSV saved")
        print(f"\n   Columns in CSV: {len(column_order)}")
        print(f"   Rows in CSV: {len(csv_data)}")
        
        print("\n" + "="*80)
        print("✅ COMPLETE")
        print("="*80)
        
        return gdf_wgs84

def display_examples(gdf):
    """Display detailed examples"""
    print("\n" + "="*80)
    print("DETAILED EXAMPLES")
    print("="*80)
    
    for i in range(min(3, len(gdf))):
        row = gdf.iloc[i]
        geom = row.geometry
        
        print(f"\n{'='*80}")
        print(f"Crown Land Feature #{i+1}")
        print(f"{'='*80}")
        print(f"Tenure Code: {row['tenure_code']}")
        print(f"Level 2 Classification: {row['L2_DESC']}")
        print(f"Level 3 Classification: {row['L3_DESC']}")
        print(f"Area: {row['area_km2']:.4f} km²")
        print(f"\nCentroid (Lat/Lon): ({row['centroid_lat']:.6f}°, {row['centroid_lon']:.6f}°)")
        print(f"\nBounding Box:")
        print(f"  West:  {row['bbox_west']:.6f}°")
        print(f"  South: {row['bbox_south']:.6f}°")
        print(f"  East:  {row['bbox_east']:.6f}°")
        print(f"  North: {row['bbox_north']:.6f}°")
        
        print(f"\nGeometry: {geom.geom_type}")
        
        if geom.geom_type == 'Polygon':
            coords = list(geom.exterior.coords)
            print(f"Number of vertices: {len(coords)}")
            print(f"\nFirst 5 coordinates (Lon, Lat):")
            for j, (lon, lat) in enumerate(coords[:5]):
                print(f"  {j+1}. ({lon:.6f}°, {lat:.6f}°)")
            if len(coords) > 5:
                print(f"  ... ({len(coords)-5} more vertices)")

if __name__ == "__main__":
    tif_path = "data/input/austen_v2_2020_21_alb_package_20241031/AUSTEN_v2_250m_2020_21_alb.tif"
    output_geojson = "data/output/crown_land_sample.geojson"
    output_csv = "data/output/crown_land_data_2020_21_sample.csv"
    
    # Extract sample
    gdf = extract_crown_land_sample(tif_path, output_geojson, output_csv, max_features=50)
    
    if gdf is not None:
        display_examples(gdf)
