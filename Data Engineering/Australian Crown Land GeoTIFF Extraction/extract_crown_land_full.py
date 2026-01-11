#!/usr/bin/env python3
"""
Extract ALL Crown Land shapes from AUSTEN GeoTIFF
Converts raster pixels to vector polygons with lat/lon coordinates

WARNING: Processing the full dataset requires significant memory and time.
         This script processes the entire 18633 x 15669 pixel raster.
         Estimated processing time: 30-60 minutes
         Estimated memory usage: 8-16 GB

For testing, use extract_crown_land_sample.py instead.
"""

import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
import numpy as np
from datetime import datetime
import sys

def extract_all_crown_land(tif_path, output_geojson, output_csv, progress_interval=5000):
    """
    Extract ALL Crown Land polygons from the GeoTIFF.
    
    Crown Land = Level 1 code 2 (tenure codes 2111-2302)
    Includes: Leasehold, Crown purposes, and Other Crown land
    
    Args:
        tif_path: Path to the GeoTIFF file
        output_geojson: Path to save GeoJSON output
        output_csv: Path to save CSV output
        progress_interval: Print progress every N features
    
    Returns:
        GeoDataFrame with all Crown Land polygons in WGS84 (lat/lon)
    """
    
    print("="*80)
    print("FULL CROWN LAND EXTRACTION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n⚠️  WARNING: This will process the ENTIRE dataset")
    print("   Estimated time: 30-60 minutes")
    print("   Estimated memory: 8-16 GB")
    print("\n   Press Ctrl+C within 5 seconds to cancel...")
    
    try:
        import time
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
    
    print("\n✓ Starting full extraction...\n")
    
    with rasterio.open(tif_path) as src:
        print(f"📁 File: {tif_path}")
        print(f"   CRS: {src.crs}")
        print(f"   Dimensions: {src.width} x {src.height} pixels")
        print(f"   Resolution: 250m x 250m")
        
        # Read the entire raster
        print(f"\n📊 Reading full raster data...")
        print(f"   (This may take several minutes...)")
        data = src.read(1)
        
        # Create mask for Crown land (values 2000-2999)
        print(f"\n🔍 Identifying Crown Land pixels...")
        crown_mask = (data >= 2000) & (data < 3000) & (data != src.nodata)
        
        crown_pixels = np.sum(crown_mask)
        total_pixels = data.size
        crown_pct = (crown_pixels / total_pixels) * 100
        
        print(f"   ✓ Crown Land pixels: {crown_pixels:,} ({crown_pct:.2f}% of Australia)")
        print(f"   ✓ Approximate area: {(crown_pixels * 0.0625):.0f} km²")
        
        if crown_pixels == 0:
            print("\n⚠️  No Crown Land pixels found!")
            return None
        
        # Extract shapes
        print(f"\n🔄 Converting raster to vector polygons...")
        print(f"   (This is the slowest step - may take 20-40 minutes)")
        print(f"   Progress will be shown every {progress_interval:,} features\n")
        
        features = []
        start_time = datetime.now()
        
        for geom, value in shapes(data, mask=crown_mask, transform=src.transform):
            features.append({
                'geometry': shape(geom),
                'tenure_code': int(value)
            })
            
            if len(features) % progress_interval == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = len(features) / elapsed if elapsed > 0 else 0
                print(f"   Progress: {len(features):,} features extracted ({rate:.1f} features/sec)")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n   ✓ Extracted {len(features):,} total features in {elapsed/60:.1f} minutes")
        
        # Create GeoDataFrame
        print(f"\n🗺️  Creating GeoDataFrame...")
        gdf = gpd.GeoDataFrame(features, crs=src.crs)
        
        # Add classifications
        print(f"   Adding tenure classifications...")
        gdf['L1N'] = (gdf['tenure_code'] // 1000).astype(int)
        gdf['L2N'] = (gdf['tenure_code'] // 100).astype(int)
        gdf['L3N'] = (gdf['tenure_code'] // 10).astype(int)
        gdf['L4N'] = gdf['tenure_code']
        
        # Add descriptions
        l1_desc = {1: "Freehold", 2: "Crown land"}
        l2_desc = {10: "Freehold", 21: "Leasehold", 22: "Crown purposes", 23: "Other Crown land"}
        l3_desc = {
            211: "Freeholding lease", 212: "Pastoral perpetual lease",
            213: "Other perpetual lease", 214: "Pastoral term lease",
            215: "Other term lease", 216: "Other lease",
            221: "Nature conservation reserve", 222: "Multiple-use public forest",
            223: "Other Crown purposes", 230: "Other Crown land"
        }
        
        gdf['L1_DESC'] = gdf['L1N'].apply(lambda x: l1_desc.get(x, "Unknown"))
        gdf['L2_DESC'] = gdf['L2N'].apply(lambda x: l2_desc.get(x, "Unknown"))
        gdf['L3_DESC'] = gdf['L3N'].apply(lambda x: l3_desc.get(x, "Unknown"))
        
        # Calculate area
        print(f"   Calculating areas...")
        gdf['area_m2'] = gdf.geometry.area
        gdf['area_km2'] = gdf['area_m2'] / 1_000_000
        
        # Convert to WGS84 (lat/lon)
        print(f"\n🌐 Converting to WGS84 (Latitude/Longitude)...")
        gdf_wgs84 = gdf.to_crs('EPSG:4326')
        
        # Add centroid coordinates (in original projection to avoid warnings)
        print(f"   Adding centroid coordinates...")
        centroids = gdf.geometry.centroid
        centroids_wgs84 = gpd.GeoSeries(centroids, crs=src.crs).to_crs('EPSG:4326')
        gdf_wgs84['centroid_lon'] = centroids_wgs84.x
        gdf_wgs84['centroid_lat'] = centroids_wgs84.y
        
        # Add bounding boxes
        print(f"   Adding bounding boxes...")
        bounds = gdf_wgs84.geometry.bounds
        gdf_wgs84['bbox_west'] = bounds.minx
        gdf_wgs84['bbox_south'] = bounds.miny
        gdf_wgs84['bbox_east'] = bounds.maxx
        gdf_wgs84['bbox_north'] = bounds.maxy
        
        # Summary statistics
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        print(f"Total Crown Land features: {len(gdf_wgs84):,}")
        print(f"Total Crown Land area: {gdf_wgs84['area_km2'].sum():,.0f} km²")
        
        print(f"\n📊 Breakdown by Level 2 Classification:")
        for l2_desc, group in gdf_wgs84.groupby('L2_DESC'):
            count = len(group)
            area = group['area_km2'].sum()
            pct = (area / gdf_wgs84['area_km2'].sum()) * 100
            print(f"  {l2_desc:30s}: {count:8,} features, {area:12,.0f} km² ({pct:5.1f}%)")
        
        print(f"\n📊 Breakdown by Level 3 Classification:")
        for l3_desc, group in gdf_wgs84.groupby('L3_DESC'):
            count = len(group)
            area = group['area_km2'].sum()
            pct = (area / gdf_wgs84['area_km2'].sum()) * 100
            print(f"  {l3_desc:30s}: {count:8,} features, {area:12,.0f} km² ({pct:5.1f}%)")
        
        # Geographic extent
        print(f"\n📍 Geographic Extent (WGS84):")
        print(f"   West:  {gdf_wgs84.total_bounds[0]:.6f}°")
        print(f"   South: {gdf_wgs84.total_bounds[1]:.6f}°")
        print(f"   East:  {gdf_wgs84.total_bounds[2]:.6f}°")
        print(f"   North: {gdf_wgs84.total_bounds[3]:.6f}°")
        
        # Save GeoJSON output
        print(f"\n💾 Saving GeoJSON to: {output_geojson}")
        if output_geojson.endswith('.shp'):
            gdf_wgs84.to_file(output_geojson)
            print(f"   Format: ESRI Shapefile")
        elif output_geojson.endswith('.geojson') or output_geojson.endswith('.json'):
            gdf_wgs84.to_file(output_geojson, driver='GeoJSON')
            print(f"   Format: GeoJSON")
        elif output_geojson.endswith('.gpkg'):
            gdf_wgs84.to_file(output_geojson, driver='GPKG')
            print(f"   Format: GeoPackage")
        else:
            gdf_wgs84.to_file(output_geojson, driver='GeoJSON')
            print(f"   Format: GeoJSON (default)")
        
        print(f"   ✓ GeoJSON saved successfully")
        
        # Prepare and save CSV with geometry as WKT in last column
        print(f"\n💾 Saving CSV to: {output_csv}")
        csv_data = gdf_wgs84.copy()
        
        # Convert geometry to WKT (Well-Known Text) format for CSV
        print(f"   Converting geometries to WKT format...")
        csv_data['geometry_wkt'] = csv_data.geometry.apply(lambda geom: geom.wkt)
        
        # Drop the geometry column
        csv_data = csv_data.drop(columns=['geometry'])
        
        # Reorder columns: tenure info first, then spatial data, geometry last
        column_order = [
            'tenure_code',
            'L1N', 'L1_DESC',
            'L2N', 'L2_DESC', 
            'L3N', 'L3_DESC',
            'L4N',
            'area_m2', 'area_km2',
            'centroid_lon', 'centroid_lat',
            'bbox_west', 'bbox_south', 'bbox_east', 'bbox_north',
            'geometry_wkt'
        ]
        
        csv_data = csv_data[column_order]
        
        # Save to CSV
        csv_data.to_csv(output_csv, index=False)
        print(f"   ✓ CSV saved successfully")
        print(f"   Columns: {len(column_order)}")
        print(f"   Rows: {len(csv_data):,}")
        
        total_time = (datetime.now() - start_time).total_seconds()
        print("\n" + "="*80)
        print("✅ EXTRACTION COMPLETE")
        print(f"   Total processing time: {total_time/60:.1f} minutes")
        print("="*80)
        
        return gdf_wgs84

if __name__ == "__main__":
    # Configuration
    tif_path = "data/input/austen_v2_2020_21_alb_package_20241031/AUSTEN_v2_250m_2020_21_alb.tif"
    output_geojson = "data/output/crown_land_full.gpkg"  # GeoPackage is more efficient for large datasets
    output_csv = "data/output/crown_land_data_2020_21_full.csv"
    
    # Run extraction
    gdf = extract_all_crown_land(tif_path, output_geojson, output_csv)
    
    if gdf is not None:
        print(f"\n✅ Success! Crown Land data extracted to:")
        print(f"   GeoPackage: {output_geojson}")
        print(f"   CSV: {output_csv}")
        print(f"\n📋 Quick Stats:")
        print(f"   Features: {len(gdf):,}")
        print(f"   Area: {gdf['area_km2'].sum():,.0f} km²")
