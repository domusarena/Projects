#!/usr/bin/env python3
"""
Script to fetch bushfire incident data from Queensland Government API
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any


def fetch_bushfire_data(url: str) -> Dict[str, Any]:
    """
    Fetch bushfire incident data from the API endpoint
    
    Args:
        url: API endpoint URL
        
    Returns:
        Dictionary containing the JSON response
        
    Raises:
        requests.RequestException: If the API request fails
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        raise


def parse_incidents(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse and extract incident information from the API response
    
    Args:
        data: Raw JSON data from API
        
    Returns:
        List of incident dictionaries
    """
    if 'features' in data:
        incidents = []
        for feature in data['features']:
            incident = {
                'properties': feature.get('properties', {}),
                'geometry': feature.get('geometry', {})
            }
            incidents.append(incident)
        return incidents
    return []


def display_incidents(incidents: List[Dict[str, Any]]) -> None:
    """
    Display incident information in a readable format
    
    Args:
        incidents: List of incident dictionaries
    """
    print(f"\n{'='*80}")
    print(f"BUSHFIRE INCIDENTS - Total: {len(incidents)}")
    print(f"Retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    for idx, incident in enumerate(incidents, 1):
        props = incident['properties']
        geom = incident['geometry']
        
        print(f"Incident #{idx}")
        print("-" * 40)
        
        # Display key properties
        for key, value in props.items():
            print(f"  {key}: {value}")
        
        # Display location if available
        if geom and 'coordinates' in geom:
            coords = geom['coordinates']
            print(f"  Location: {coords}")
        
        print()


def save_to_file(data: Dict[str, Any], filename: str = "data/qld_bushfire_data.json") -> None:
    """
    Save the raw data to a JSON file
    
    Args:
        data: Data to save
        filename: Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Error saving file: {e}")


def main():
    """Main execution function"""
    # API endpoint
    API_URL = "https://publiccontent-gis-psba-qld-gov-au.s3.amazonaws.com/content/Feeds/BushfireCurrentIncidents/bushfireAlert.json"
    
    print("Fetching bushfire incident data...")
    
    try:
        # Fetch data
        data = fetch_bushfire_data(API_URL)
        
        # Parse incidents
        incidents = parse_incidents(data)
        
        # Display incidents
        display_incidents(incidents)
        
        # Save to file
        save_to_file(data)
        
        # Print summary
        print(f"\nSummary:")
        print(f"  Total incidents: {len(incidents)}")
        print(f"  Data structure type: {data.get('type', 'Unknown')}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())