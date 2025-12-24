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
        feature_tags = feature.get('tags', [])
        
        for element in feature.get('elements', []):
            if element['type'] != 'scenario':
                continue
            
            element_tags = element.get('tags', [])
            # Combine tags (Scenario tags take precedence if we scan element_tags first, 
            # but here we just list them. get_tag_value stops at first match)
            # We want Scenario to override Feature? Yes.
            all_tags = element_tags + feature_tags
            
            project = get_tag_value(all_tags, 'vordu:project=')
            row = get_tag_value(all_tags, 'vordu:row=')
            phase = get_tag_value(all_tags, 'vordu:phase=')

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
                        'steps_passed': 0,
                        'details': []
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
                
                # Determine scenario status
                scenario_status = 'passed' if is_passed else 'failed'
                tag_names = [t['name'] for t in all_tags]
                if 'wip' in tag_names or '@wip' in tag_names: # Handle both formats just in case
                    scenario_status = 'pending'
                elif step_count == 0:
                     scenario_status = 'skipped'

                # Collect step details
                step_details = []
                for step in steps:
                    step_details.append({
                        'keyword': step.get('keyword', ''),
                        'name': step.get('name', ''),
                        'status': step.get('result', {}).get('status', 'undefined')
                    })

                cells[key]['details'].append({
                    'feature': feature.get('name', 'Unknown'),
                    'scenario': element['name'],
                    'status': scenario_status,
                    'passed_steps': passed_step_count,
                    'total_steps': step_count,
                    'steps': step_details,
                    'tag': ' '.join(tag_names)
                })

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
            "steps_total": data['steps_total'],
            "steps_passed": data['steps_passed'],
            "details": data['details']
        })

    return ingest_items

def ingest_data(api_url: str, items: List[Dict], api_key: str = None):
    if not items:
        print("No Vörðu tagged scenarios found.")
        return

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        response = requests.post(f"{api_url}/ingest", json=items, headers=headers)
        response.raise_for_status()
        print(f"Successfully ingested {len(items)} items. Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error ingesting data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Cucumber JSON to Vörðu")
    parser.add_argument("file", help="Path to cucumber.json report")
    parser.add_argument("--api", default="http://localhost:8000", help="Vörðu API URL")
    parser.add_argument("--api-key", help="API Key for authentication")
    
    args = parser.parse_args()
    
    items = parse_cucumber_json(args.file)
    ingest_data(args.api, items, args.api_key)
