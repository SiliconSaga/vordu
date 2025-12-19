#!/usr/bin/env python3
import yaml
import json
import argparse
import sys
import os
import urllib.request
import urllib.error

def parse_catalog(file_path):
    """Parses a multi-document YAML catalog file."""
    if not os.path.exists(file_path):
        print(f"Error: Catalog file not found at {file_path}")
        return []
    
    with open(file_path, 'r') as f:
        try:
            documents = list(yaml.safe_load_all(f))
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML: {exc}")
            return []
            
    entities = []
    for doc in documents:
        if doc and 'kind' in doc and 'metadata' in doc:
            entities.append(doc)
    return entities

def extract_vordu_metadata(entities):
    """Extracts Vörðu-specific annotations from entities."""
    data = {
        "system": None,
        "components": []
    }
    
    for entity in entities:
        kind = entity.get('kind')
        meta = entity.get('metadata', {})
        name = meta.get('name')
        annotations = meta.get('annotations', {})
        
        # Look for Vörðu annotations
        row_label = annotations.get('vordu.io/row-label')
        
        if kind == 'System':
            data['system'] = {
                "name": name,
                "label": row_label or name,
                "description": meta.get('description'),
                "domain": entity.get('spec', {}).get('domain')
            }
        elif kind == 'Component':
            component_data = {
                "name": name,
                "label": row_label or name,
                "system": meta.get('system') or entity.get('spec', {}).get('partOf'),
                "parent": annotations.get('vordu.io/parent-component')
            }
            data['components'].append(component_data)
            
    return data

def mock_bdd_results():
    """Returns mock BDD data."""
    return [
        {"tag": "@component:vordu-api @phase:1", "status": "passed"},
        {"tag": "@component:autoboros-agent @phase:1", "status": "failed"},
        
        # Mimir Data
        {"tag": "@component:mimir-kafka @phase:0", "status": "passed"},
        {"tag": "@component:mimir-kafka @phase:1", "status": "passed"},
        {"tag": "@component:mimir-kafka @phase:2", "status": "pending"},
        
        {"tag": "@component:mimir-valkey @phase:0", "status": "passed"},
        {"tag": "@component:mimir-valkey @phase:1", "status": "passed"},
        
        {"tag": "@component:mimir-percona-postgres @phase:1", "status": "passed"},
        {"tag": "@component:mimir-percona-mysql @phase:1", "status": "pending"},
        {"tag": "@component:mimir-percona-mongo @phase:1", "status": "failed"}
    ]

def build_config_payload(vordu_data):
    """Payload for /config/ingest"""
    return vordu_data

def build_status_payload(vordu_data, test_results):
    """Payload for /ingest (Flattened List[IngestItem])."""
    system_name = vordu_data['system']['name']
    components = vordu_data['components']
    
    # Map mocked results to a quick lookup
    # Format: status_map[(comp_name, phase_id)] = [status1, status2]
    status_map = {}
    
    for result in test_results:
        tag_str = result['tag']
        status = result['status']
        
        # Parse tags
        comp_name = None
        phase_id = None
        
        parts = tag_str.split()
        for part in parts:
            if part.startswith("@component:"):
                comp_name = part.split(":")[1]
            elif part.startswith("@phase:"):
                try:
                    phase_id = int(part.split(":")[1])
                except ValueError:
                    continue
        
        if comp_name and phase_id is not None:
            key = (comp_name, phase_id)
            if key not in status_map:
                status_map[key] = []
            status_map[key].append(status)

    ingest_items = []
    
    # Generate items for each component and each phase (0-3)
    for comp in components:
        comp_name = comp['name']
        row_id = comp_name 
        
        for phase in range(4): # Phases 0 to 3
            statuses = status_map.get((comp_name, phase), [])
            
            if not statuses:
                # If no tests for this phase, user might want "empty" or "pending" depending on interpretation.
                # Usually if strict BDD, no tests = grey/empty. 
                # Let's send "pending" with 0 completion to signify "Not Started" or just skip?
                # Vörðu UI renders "empty" if no data. Let's skip if no data, OR send explicitly empty.
                # But to override previous data, we might need to send something?
                # For now, let's treat no-tag as "empty".
                continue 
                
            if "failed" in statuses:
                final_status = "fail"
                completion = 50
                passed = statuses.count("passed")
                total = len(statuses)
            elif any(s == "pending" for s in statuses):
                final_status = "pending"
                completion = 25
                passed = statuses.count("passed")
                total = len(statuses)
            else:
                final_status = "pass"
                completion = 100
                passed = len(statuses)
                total = len(statuses)
                
            item = {
                "project_name": system_name,
                "row_id": row_id,
                "phase_id": phase,
                "status": final_status,
                "completion": completion,
                "scenarios_total": total,
                "scenarios_passed": passed,
                "steps_total": total * 5,
                "steps_passed": passed * 5
            }
            ingest_items.append(item)
            
    return ingest_items

def post_to_api(url, api_key, payload):
    """Posts payload to URL."""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"[{url}] Success: {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"[{url}] Error: {e.code} {e.reason}")
        print(e.read().decode())
        return False
    except urllib.error.URLError as e:
        print(f"[{url}] Connection Error: {e.reason}")
        return False

def parse_cucumber_json(file_path):
    """Parses a Cucumber JSON report to extract Vörðu tags and status."""
    if not os.path.exists(file_path):
        print(f"Error: Report file not found at {file_path}")
        return []
    
    with open(file_path, 'r') as f:
        try:
            features = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return []
            
    results = []
    
    for feature in features:
        for element in feature.get('elements', []):
            if element['type'] != 'scenario':
                continue
            
            # Extract tags
            tags = [t['name'] for t in element.get('tags', [])]
            tag_str = " ".join(tags)
            
            # Determine status
            steps = element.get('steps', [])
            if not steps:
                status = "pending"
            elif any(s['result']['status'] == 'failed' for s in steps):
                status = "failed"
            elif any(s['result']['status'] == 'undefined' for s in steps):
                status = "pending"
            elif all(s['result']['status'] == 'passed' for s in steps):
                status = "passed"
            else:
                status = "pending" # Default (e.g. skipped)
                
            results.append({
                "tag": tag_str,
                "status": status
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description='Vörðu Ingestion Script')
    parser.add_argument('catalog', help='Path to catalog-info.yaml')
    parser.add_argument('--report', help='Path to cucumber.json test report (optional)')
    parser.add_argument('--api-url', help='Base URL of the Vörðu API (e.g., http://localhost:8000)')
    parser.add_argument('--api-key', help='API Key for authentication', default='dev-key')
    args = parser.parse_args()

    print(f"--- Processing {args.catalog} ---")
    
    entities = parse_catalog(args.catalog)
    if not entities:
        print("No valid entities found.")
        sys.exit(1)
        
    vordu_data = extract_vordu_metadata(entities)
    
    if not vordu_data['system']:
        print("Warning: No 'System' entity found. Proceeding with Components only.")
        
    if args.report:
        print(f"Parsing test results from {args.report}...")
        results = parse_cucumber_json(args.report)
    else:
        print("Using Mock BDD results (No report provided).")
        results = mock_bdd_results()
    
    # 1. Config Ingestion
    config_payload = build_config_payload(vordu_data)
    
    if args.api_url:
        config_url = f"{args.api_url}/config/ingest"
        print(f"Posting Config to {config_url}...")
        post_to_api(config_url, args.api_key, config_payload)
        
        # 2. Status Ingestion
        status_payload = build_status_payload(vordu_data, results)
        status_url = f"{args.api_url}/ingest"
        print(f"Posting Status to {status_url}...")
        post_to_api(status_url, args.api_key, status_payload)
        
    else:
        print("\n[Generated Config Payload]")
        print(json.dumps(config_payload, indent=2))
        print("\n[Generated Status Payload]")
        status_payload = build_status_payload(vordu_data, results)
        print(json.dumps(status_payload, indent=2))

if __name__ == "__main__":
    main()
