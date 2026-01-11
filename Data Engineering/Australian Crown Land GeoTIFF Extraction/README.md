# Crown Land Extraction from AUSTEN GeoTIFF

## Overview
This package contains Python scripts to extract Crown Land shapes from the AUSTEN v2 250m (2020-21) Land Tenure of Australia dataset and convert them to geographic data with latitude/longitude coordinates.

## What is Crown Land?
According to the AUSTEN metadata, **Crown Land** is:
- **Level 1 Classification Code: 2**
- **Definition**: Land owned by the Crown (non-freehold land)
- **Tenure Codes**: 2111-2302

Crown Land includes three Level 2 categories:
1. **Leasehold (21)**: Exclusive use of Crown land leased for specified term and purpose
2. **Crown Purposes (22)**: Land reserved, dedicated, or vested for Crown purposes
3. **Other Crown Land (23)**: Crown land unallocated to a purpose

## Files Included

### 1. extract_crown_land_sample.py ✅ TESTED
**Purpose**: Extract a small sample of Crown Land for testing and demonstration

**Features**:
- Memory-efficient (processes only a 2000x2000 pixel window)
- Fast execution (< 2 minutes)
- Extracts up to 50 Crown Land features
- Perfect for testing and understanding the data structure

**Output**: `crown_land_sample.geojson` (36 KB, 50 features)

**Usage**:
```bash
python extract_crown_land_sample.py
```

### 2. extract_crown_land_full.py ⚠️ FULL DATASET
**Purpose**: Extract ALL Crown Land from the entire Australia dataset

**Requirements**:
- 8-16 GB RAM
- 30-60 minutes processing time
- ~10-20 GB disk space for output

**Features**:
- Processes entire 18633 x 15669 pixel raster
- Extracts all Crown Land polygons across Australia
- Progress reporting during extraction
- Multiple output formats (GeoJSON, Shapefile, GeoPackage)

**Usage**:
```bash
python extract_crown_land_full.py
```

## Sample Results

### Test Extraction Summary
- **Features extracted**: 50 Crown Land parcels
- **Total area**: 5.75 km²
- **Classification**: Other Crown land (Level 3 code 230)
- **Location**: Central Australia (around -25.5°S, 134.5°E)

### Example Crown Land Feature
```
Tenure Code: 2301
Classification: Other Crown land
Area: 0.0625 km²
Centroid: (-25.479481°S, 134.536824°E)

Bounding Box:
  West:  134.535542°
  South: -25.480618°
  East:  134.538107°
  North: -25.478344°

Polygon Coordinates (first 5 vertices):
  1. (134.535542°, -25.478388°)
  2. (134.535592°, -25.480618°)
  3. (134.538107°, -25.480573°)
  4. (134.538057°, -25.478344°)
  5. (134.535542°, -25.478388°)  [closes polygon]
```

## Output Format

### GeoJSON Structure
Each Crown Land feature includes:

**Geometry**:
- `geometry`: Polygon with WGS84 (EPSG:4326) coordinates
- All coordinates in (longitude, latitude) format

**Properties**:
- `tenure_code`: 4-digit code (e.g., 2301)
- `L1N`: Level 1 code (always 2 for Crown land)
- `L2N`: Level 2 code (21, 22, or 23)
- `L3N`: Level 3 code (211-230)
- `L4N`: Level 4 code (2111-2302)
- `L1_DESC`: "Crown land"
- `L2_DESC`: Leasehold / Crown purposes / Other Crown land
- `L3_DESC`: Detailed classification (see metadata)
- `area_m2`: Area in square meters
- `area_km2`: Area in square kilometers
- `centroid_lon`: Centroid longitude
- `centroid_lat`: Centroid latitude
- `bbox_west`, `bbox_south`, `bbox_east`, `bbox_north`: Bounding box

## Crown Land Classifications

### Level 2 (Broad Categories)
1. **Leasehold (21)**: Crown land leased to entities
2. **Crown purposes (22)**: Reserved/dedicated lands
3. **Other Crown land (23)**: Unallocated Crown land

### Level 3 (Detailed Types)
- **211**: Freeholding lease
- **212**: Pastoral perpetual lease
- **213**: Other perpetual lease
- **214**: Pastoral term lease
- **215**: Other term lease
- **216**: Other lease
- **221**: Nature conservation reserve
- **222**: Multiple-use public forest
- **223**: Other Crown purposes
- **230**: Other Crown land

### Level 4 (Indigenous Distinction)
Adds "-Indigenous" suffix for land held by Indigenous land trusts (e.g., 2212, 2232)

## Technical Details

### Source Data
- **File**: AUSTEN_v2_250m_2020_21_alb.tif
- **Resolution**: 250m x 250m pixels
- **Projection**: GDA94 / Australian Albers (EPSG:3577)
- **Coverage**: Mainland Australia
- **Time Period**: 2020-21

### Coordinate Systems
- **Input**: EPSG:3577 (GDA94 Australian Albers, meters)
- **Output**: EPSG:4326 (WGS84, decimal degrees)

### Processing Method
1. Read GeoTIFF raster data
2. Identify Crown Land pixels (tenure codes 2000-2999)
3. Convert raster pixels to vector polygons
4. Add classification attributes from metadata
5. Calculate areas and centroids
6. Transform to WGS84 lat/lon coordinates
7. Export to GeoJSON/Shapefile/GeoPackage

## Requirements

```bash
pip install rasterio geopandas numpy shapely --break-system-packages
```

## Performance Tips

1. **For testing**: Use `extract_crown_land_sample.py`
2. **For full dataset**: 
   - Run on machine with 16GB+ RAM
   - Use GeoPackage (.gpkg) format for output (more efficient than GeoJSON)
   - Allow 30-60 minutes processing time
   - Consider cloud computing if local resources are limited

## Data Source

**Citation**:
ABARES 2024, Land tenure of Australia 2010–11 to 2020–21, Australian Bureau of Agricultural and Resource Economics and Sciences, Canberra, October, CC BY 4.0. DOI: 10.25814/89rx-zs30

**Metadata**: austen_v2_descriptivemetadata_20241031_0.pdf

## Notes

- Crown Land represents approximately 58% of Australia's land area
- This excludes native title and Indigenous-owned freehold outside Indigenous land grant instruments
- "Other Crown land" includes unallocated Crown land and some water features
- Resolution of 250m means minimum feature size is ~6.25 hectares (0.0625 km²)

## Contact

For questions about the AUSTEN dataset:
- Email: info.ABARES@agriculture.gov.au
- Web: agriculture.gov.au/abares

---
Generated: November 6, 2025
