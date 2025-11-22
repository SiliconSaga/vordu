import json
import requests
import argparse
import sys
from typing import List, Dict

def parse_cucumber_json(file_path: str) -> List[Dict]:
    with open(file_path, 'r') as f:
        features = json.load(f)
    
    ingest_items = []
    
    # Helper to extract tag value
    def get_tag_value(tags, prefix):
        for tag in tags:
            if tag['name'].startswith(prefix):
                return tag['name'].split('=')[1]
        return None

    # Group scenarios by cell (project/row/phase)
    cells = {}

    for feature in features:
        for element in feature.get('elements', []):
            if element['type'] != 'scenario':
                continue
            
            tags = element.get('tags', [])
            project = get_tag_value(tags, '@vordu:project=')
            row = get_tag_value(tags, '@vordu:row=')
            phase = get_tag_value(tags, '@vordu:phase=')

            if project and row and phase:
                key = f"{project}::{row}::{phase}"
                if key not in cells:
                    cells[key] = {'total': 0, 'passed': 0, 'project': project, 'row': row, 'phase': int(phase)}
                
                cells[key]['total'] += 1
                
                # Check if all steps passed
                steps = element.get('steps', [])
                is_passed = all(step['result']['status'] == 'passed' for step in steps)
                if is_passed:
                    cells[key]['passed'] += 1

    # Convert to IngestItem format
    for key, data in cells.items():
        completion = int((data['passed'] / data['total']) * 100) if data['total'] > 0 else 0
        
        # Determine status based on completion (simplified logic)
        if completion == 100:
            status = 'pass'
        elif completion > 0:
            status = 'pending'
        else:
            status = 'fail'

        ingest_items.append({
            "project_name": data['project'],
            "row_id": data['row'],
            "phase_id": data['phase'],
            "status": status,
            "completion": completion
        })

    return ingest_items

def ingest_data(api_url: str, items: List[Dict]):
    if not items:
        print("No Vörðu tagged scenarios found.")
        return

    try:
        response = requests.post(f"{api_url}/ingest", json=items)
        response.raise_for_status()
        print(f"Successfully ingested {len(items)} items. Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error ingesting data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Cucumber JSON to Vörðu")
    parser.add_argument("file", help="Path to cucumber.json report")
    parser.add_argument("--api", default="http://localhost:8000", help="Vörðu API URL")
    
    args = parser.parse_args()
    
    items = parse_cucumber_json(args.file)
    ingest_data(args.api, items)
