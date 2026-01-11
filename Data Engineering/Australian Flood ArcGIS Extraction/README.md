# ArcGIS Data Extractor

A flexible, reusable Python tool for extracting data from any ArcGIS MapServer or FeatureServer endpoint.

## Features

- ✅ Works with both MapServer and FeatureServer endpoints
- ✅ Automatic pagination to retrieve ALL features (no record limits)
- ✅ Export to both JSON and CSV formats
- ✅ Optional geometry inclusion/exclusion
- ✅ Command-line interface for quick extractions
- ✅ Python API for programmatic use
- ✅ List available layers before extraction
- ✅ Detailed logging and progress tracking

## Installation

### Requirements
```bash
pip install requests
```

That's it! The script only requires the `requests` library, which is commonly available.

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Extract a specific layer
python arcgis_data_extractor.py <endpoint_url> <layer_id>
```

#### List Available Layers
```bash
python arcgis_data_extractor.py <endpoint_url> --list-layers
```

#### Examples

**Extract Logan City flood data (Layer 0):**
```bash
python arcgis_data_extractor.py \
  "https://arcgis.lcc.wspdigital.com/server/rest/services/FloodPortal/ConsolidatedFloodData_20250505/MapServer" \
  0
```

**Extract Moreton Bay data (Layer 0):**
```bash
python arcgis_data_extractor.py \
  "https://services-ap1.arcgis.com/152ojN3Ts9H3cdtl/arcgis/rest/services/CMB_Council_Assets/FeatureServer" \
  0
```

**List all available layers:**
```bash
python arcgis_data_extractor.py \
  "https://arcgis.lcc.wspdigital.com/server/rest/services/FloodPortal/ConsolidatedFloodData_20250505/MapServer" \
  --list-layers
```

**Extract without geometry (smaller files):**
```bash
python arcgis_data_extractor.py \
  "https://example.com/MapServer" \
  5 \
  --no-geometry
```

**Custom output location and filename:**
```bash
python arcgis_data_extractor.py \
  "https://example.com/MapServer" \
  0 \
  --output-dir my_data \
  --prefix flood_zones
```

**Save only CSV (no JSON):**
```bash
python arcgis_data_extractor.py \
  "https://example.com/MapServer" \
  0 \
  --no-json
```

### Command Line Options

```
positional arguments:
  endpoint              Base URL of the ArcGIS service
  layer_id              Layer ID to extract

optional arguments:
  -h, --help           Show help message and exit
  --list-layers        List all available layers and exit
  --output-dir DIR     Output directory (default: data)
  --prefix PREFIX      Prefix for output filenames
  --no-json            Do not save JSON output
  --no-csv             Do not save CSV output
  --no-geometry        Do not include geometry in results
  --quiet              Suppress progress messages
```

### Python API

You can also use the `ArcGISDataExtractor` class programmatically in your Python scripts:

```python
from arcgis_data_extractor import ArcGISDataExtractor

# Initialize extractor
endpoint = "https://example.com/arcgis/rest/services/MyService/MapServer"
extractor = ArcGISDataExtractor(endpoint)

# List available layers
layers = extractor.list_layers()
for layer in layers:
    print(f"Layer {layer['id']}: {layer['name']}")

# Extract a specific layer
extractor.extract_layer_data(
    layer_id=0,
    output_dir="data",
    output_prefix="my_data",
    save_json=True,
    save_csv=True,
    return_geometry=True
)
```

See `example_usage.py` for more detailed examples.

## Output Files

The extractor creates two types of output files:

### JSON Output
Contains complete data including:
- Timestamp and metadata
- Layer information (name, geometry type, fields)
- All feature data with geometry
- Layer configuration details

**Filename format:** `{output_dir}/{prefix}.json`

### CSV Output
Contains feature attributes only (no geometry):
- One row per feature
- All attribute fields as columns
- Easier to open in Excel or other spreadsheet tools

**Filename format:** `{output_dir}/{prefix}.csv`

## API Methods

### `ArcGISDataExtractor` Class

#### `__init__(base_url, verbose=True)`
Initialize the extractor with an endpoint URL.

#### `get_service_info()`
Get information about the service (available layers, etc.).

#### `get_layer_info(layer_id)`
Get detailed information about a specific layer.

#### `list_layers()`
List all available layers in the service.

#### `query_all_data(layer_id, return_geometry=True, out_fields="*")`
Query all features from a layer using automatic pagination.

#### `extract_layer_data(layer_id, output_dir="data", ...)`
Complete extraction workflow: query data and save to files.

#### `save_to_json(data, filepath)`
Save data to a JSON file.

#### `save_to_csv(features, filepath)`
Save feature attributes to a CSV file.

## How It Works

1. **Connects** to the ArcGIS service endpoint
2. **Retrieves** layer metadata (fields, geometry type, etc.)
3. **Queries** data using pagination (1000 records at a time)
4. **Continues** until all features are retrieved
5. **Saves** data to JSON and/or CSV files

The tool handles pagination automatically, so you don't need to worry about record limits imposed by the ArcGIS server.

## Troubleshooting

### Network Errors
If you encounter network errors, ensure:
- The endpoint URL is correct
- You have internet connectivity
- The ArcGIS service is accessible (not behind authentication)

### No Data Retrieved
If no features are returned:
- Verify the layer ID exists using `--list-layers`
- Check if the layer actually contains data
- Some layers may be empty or have restricted access

### Large Datasets
For very large datasets (100,000+ features):
- The extraction may take several minutes
- JSON files can become very large - consider using `--no-json`
- CSV files are generally more compact and easier to work with

## Examples from Your Original Scripts

### Logan City Floods
```bash
python arcgis_data_extractor.py \
  "https://arcgis.lcc.wspdigital.com/server/rest/services/FloodPortal/ConsolidatedFloodData_20250505/MapServer" \
  0 \
  --output-dir data/logan_city \
  --prefix low_flood_islands
```

### Moreton Bay Floods
```bash
python arcgis_data_extractor.py \
  "https://services-ap1.arcgis.com/152ojN3Ts9H3cdtl/arcgis/rest/services/CMB_Council_Assets/FeatureServer" \
  0 \
  --output-dir data/moreton_bay \
  --prefix low_flood_islands
```

## License

This is a utility script provided as-is for working with ArcGIS services.

## Contributing

Feel free to modify and extend this script for your specific needs!
