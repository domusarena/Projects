#!/usr/bin/env python3
"""
ArcGIS Data Extractor
A generic tool to query and export data from any ArcGIS MapServer or FeatureServer endpoint.

Usage:
    python arcgis_data_extractor.py <endpoint_url> <layer_id> [options]
    
Example:
    python arcgis_data_extractor.py https://example.com/arcgis/rest/services/MyService/MapServer 0
"""

import requests
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ArcGISDataExtractor:
    """Extract data from ArcGIS MapServer or FeatureServer endpoints"""
    
    def __init__(self, base_url: str, verbose: bool = True):
        """
        Initialize the extractor with a base URL.
        
        Args:
            base_url: Base URL of the ArcGIS service (MapServer or FeatureServer)
            verbose: Whether to print progress messages
        """
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        
    def _log(self, message: str, level: str = "INFO"):
        """Print log message if verbose is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get basic information about the MapServer/FeatureServer service"""
        params = {'f': 'json'}
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_layer_info(self, layer_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific layer.
        
        Args:
            layer_id: The ID of the layer to query
            
        Returns:
            Dictionary containing layer information
        """
        url = f"{self.base_url}/{layer_id}"
        params = {'f': 'json'}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def list_layers(self) -> List[Dict[str, Any]]:
        """
        List all available layers in the service.
        
        Returns:
            List of layer information dictionaries
        """
        service_info = self.get_service_info()
        return service_info.get('layers', [])
    
    def query_all_data(
        self, 
        layer_id: int, 
        return_geometry: bool = True, 
        out_fields: str = "*",
        max_records_per_request: int = 1000
    ) -> Dict[str, Any]:
        """
        Query ALL data from a specific layer using pagination.
        
        Args:
            layer_id: The ID of the layer to query
            return_geometry: Whether to include geometry in results
            out_fields: Fields to return (default "*" for all fields)
            max_records_per_request: Maximum records to fetch per request
            
        Returns:
            Dictionary with 'features' list and 'totalCount'
        """
        url = f"{self.base_url}/{layer_id}/query"
        
        all_features = []
        offset = 0
        
        self._log(f"Querying all data from Layer {layer_id}...")
        self._log("-" * 80)
        
        while True:
            params = {
                'where': '1=1',
                'outFields': out_fields,
                'returnGeometry': str(return_geometry).lower(),
                'f': 'json',
                'resultRecordCount': max_records_per_request,
                'resultOffset': offset
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                result = response.json()
                
                # Check for errors
                if 'error' in result:
                    self._log(f"Error from server: {result['error']}", "ERROR")
                    break
                
                # Get features from this batch
                features = result.get('features', [])
                
                if not features:
                    break
                
                all_features.extend(features)
                self._log(f"Retrieved {len(features)} features (Total: {len(all_features)})")
                
                # Check if we got fewer features than requested (indicates last batch)
                if len(features) < max_records_per_request:
                    break
                
                offset += max_records_per_request
                
            except Exception as e:
                self._log(f"Error during query: {str(e)}", "ERROR")
                break
        
        self._log("-" * 80)
        self._log(f"Total features retrieved: {len(all_features)}")
        
        return {
            'features': all_features,
            'totalCount': len(all_features)
        }
    
    def save_to_json(
        self, 
        data: Dict[str, Any], 
        filepath: str,
        indent: int = 2
    ):
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            filepath: Path to output file
            indent: JSON indentation level
        """
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        
        self._log(f"JSON data saved to: {filepath}")
    
    def save_to_csv(
        self, 
        features: List[Dict[str, Any]], 
        filepath: str
    ):
        """
        Save feature attributes to a CSV file.
        
        Args:
            features: List of feature dictionaries
            filepath: Path to output file
        """
        if not features:
            self._log("No features to save to CSV", "WARNING")
            return
        
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Get field names from the first feature
        field_names = list(features[0].get('attributes', {}).keys())
        
        if not field_names:
            self._log("No attributes found in features", "WARNING")
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            
            for feature in features:
                writer.writerow(feature.get('attributes', {}))
        
        self._log(f"CSV data saved to: {filepath}")
    
    def extract_layer_data(
        self,
        layer_id: int,
        output_dir: str = "data",
        output_prefix: Optional[str] = None,
        save_json: bool = True,
        save_csv: bool = True,
        return_geometry: bool = True
    ) -> Dict[str, Any]:
        """
        Extract all data from a layer and save to files.
        
        Args:
            layer_id: The ID of the layer to extract
            output_dir: Directory to save output files
            output_prefix: Prefix for output filenames (auto-generated if None)
            save_json: Whether to save JSON output
            save_csv: Whether to save CSV output
            return_geometry: Whether to include geometry in results
            
        Returns:
            Dictionary containing the extracted data and metadata
        """
        self._log("=" * 80)
        self._log(f"ArcGIS Data Extraction")
        self._log(f"Endpoint: {self.base_url}")
        self._log(f"Layer ID: {layer_id}")
        self._log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log("=" * 80)
        
        # Get layer information
        self._log("\n[1] Getting layer information...")
        layer_info = self.get_layer_info(layer_id)
        
        layer_name = layer_info.get('name', 'Unknown')
        geometry_type = layer_info.get('geometryType', 'N/A')
        fields = layer_info.get('fields', [])
        
        self._log(f"Layer Name: {layer_name}")
        self._log(f"Geometry Type: {geometry_type}")
        self._log(f"Fields: {len(fields)}")
        
        if fields and self.verbose:
            self._log("\nField Details:")
            for field in fields:
                self._log(f"  - {field['name']} ({field['type']}): {field.get('alias', field['name'])}")
        
        # Query all data
        self._log(f"\n[2] Querying data...")
        result = self.query_all_data(layer_id, return_geometry=return_geometry)
        
        if result['totalCount'] == 0:
            self._log("No features found in this layer.", "WARNING")
            return result
        
        # Generate output prefix if not provided
        if output_prefix is None:
            # Create a clean filename from layer name
            clean_name = layer_name.lower().replace(' ', '_').replace('/', '_')
            output_prefix = f"layer_{layer_id}_{clean_name}"
        
        # Prepare export data
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': self.base_url,
            'layer_id': layer_id,
            'layer_name': layer_name,
            'geometry_type': geometry_type,
            'total_features': result['totalCount'],
            'layer_info': layer_info,
            'features': result['features']
        }
        
        # Save files
        self._log(f"\n[3] Saving data...")
        
        if save_json:
            json_filepath = f"{output_dir}/{output_prefix}.json"
            self.save_to_json(export_data, json_filepath)
        
        if save_csv:
            csv_filepath = f"{output_dir}/{output_prefix}.csv"
            self.save_to_csv(result['features'], csv_filepath)
        
        # Display sample data
        if self.verbose and result['features']:
            self._log(f"\n[4] Sample Data (First Feature)")
            self._log("-" * 80)
            first_feature = result['features'][0]
            self._log("Attributes:")
            for key, value in first_feature.get('attributes', {}).items():
                # Truncate long values for display
                str_value = str(value)
                if len(str_value) > 100:
                    str_value = str_value[:97] + "..."
                self._log(f"  {key}: {str_value}")
            
            if 'geometry' in first_feature:
                self._log(f"\nGeometry Keys: {list(first_feature['geometry'].keys())}")
        
        self._log("\n" + "=" * 80)
        self._log("Extraction completed successfully!")
        self._log("=" * 80)
        
        return export_data


def main():
    """Command-line interface for the ArcGIS Data Extractor"""
    parser = argparse.ArgumentParser(
        description='Extract data from ArcGIS MapServer or FeatureServer endpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract layer 0 from a MapServer
  python arcgis_data_extractor.py https://example.com/arcgis/rest/services/MyService/MapServer 0
  
  # Extract layer 5 without geometry, custom output name
  python arcgis_data_extractor.py https://example.com/FeatureServer 5 --no-geometry --prefix my_data
  
  # List all available layers
  python arcgis_data_extractor.py https://example.com/MapServer --list-layers
  
  # Save only CSV output
  python arcgis_data_extractor.py https://example.com/MapServer 0 --no-json
        """
    )
    
    parser.add_argument(
        'endpoint',
        help='Base URL of the ArcGIS service (MapServer or FeatureServer)'
    )
    
    parser.add_argument(
        'layer_id',
        nargs='?',
        type=int,
        help='Layer ID to extract (required unless --list-layers is used)'
    )
    
    parser.add_argument(
        '--list-layers',
        action='store_true',
        help='List all available layers and exit'
    )
    
    parser.add_argument(
        '--output-dir',
        default='data',
        help='Output directory for saved files (default: data)'
    )
    
    parser.add_argument(
        '--prefix',
        help='Prefix for output filenames (auto-generated if not specified)'
    )
    
    parser.add_argument(
        '--no-json',
        action='store_true',
        help='Do not save JSON output'
    )
    
    parser.add_argument(
        '--no-csv',
        action='store_true',
        help='Do not save CSV output'
    )
    
    parser.add_argument(
        '--no-geometry',
        action='store_true',
        help='Do not include geometry in results'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )
    
    args = parser.parse_args()
    
    # Create extractor instance
    extractor = ArcGISDataExtractor(args.endpoint, verbose=not args.quiet)
    
    try:
        # Handle list-layers command
        if args.list_layers:
            print("\n" + "=" * 80)
            print("Available Layers")
            print("=" * 80)
            layers = extractor.list_layers()
            if layers:
                for layer in layers:
                    print(f"Layer {layer['id']}: {layer['name']}")
                    if 'geometryType' in layer:
                        print(f"  Geometry Type: {layer['geometryType']}")
                print(f"\nTotal layers: {len(layers)}")
            else:
                print("No layers found or unable to retrieve layer information.")
            print("=" * 80)
            return
        
        # Validate layer_id is provided
        if args.layer_id is None:
            parser.error("layer_id is required unless --list-layers is used")
        
        # Extract layer data
        extractor.extract_layer_data(
            layer_id=args.layer_id,
            output_dir=args.output_dir,
            output_prefix=args.prefix,
            save_json=not args.no_json,
            save_csv=not args.no_csv,
            return_geometry=not args.no_geometry
        )
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if not args.quiet:
            import traceback
            print("\nFull traceback:")
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())