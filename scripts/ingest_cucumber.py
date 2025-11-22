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
                    cells[key] = {
                        'project': project, 
                        'row': row, 
                        'phase': int(phase),
                        'scenarios_total': 0,
                        'scenarios_passed': 0,
                        'steps_total': 0,
                        'steps_passed': 0
                    }
                
                cells[key]['scenarios_total'] += 1
                
                # Check steps
                steps = element.get('steps', [])
                step_count = len(steps)
                passed_step_count = sum(1 for step in steps if step['result']['status'] == 'passed')
                
                cells[key]['steps_total'] += step_count
                cells[key]['steps_passed'] += passed_step_count

                is_passed = (step_count > 0) and (step_count == passed_step_count)
                if is_passed:
                    cells[key]['scenarios_passed'] += 1

    # Convert to IngestItem format
    for key, data in cells.items():
        completion = int((data['scenarios_passed'] / data['scenarios_total']) * 100) if data['scenarios_total'] > 0 else 0
        
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
            "completion": completion,
            "scenarios_total": data['scenarios_total'],
            "scenarios_passed": data['scenarios_passed'],
            "steps_total": data['steps_total'],
            "steps_passed": data['steps_passed']
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
