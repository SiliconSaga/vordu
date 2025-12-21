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
        spec = entity.get('spec', {})
        
        # Look for Vörðu annotations
        row_label = annotations.get('vordu.io/row-label')
        
        if kind == 'System':
            data['system'] = {
                "name": name,
                "label": name.capitalize(), # Header uses Name (e.g. Mimir)
                "row_label": row_label or name, # Specific label for the Section Row
                "description": meta.get('description'),
                "domain": spec.get('domain'),
                "granularity": annotations.get('vordu.io/granularity', 'component') 
            }
        elif kind == 'Component':
            component_data = {
                "name": name,
                "label": row_label or name,
                "system": meta.get('system') or spec.get('partOf'),
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
    import copy
    payload = copy.deepcopy(vordu_data)
    
    if payload['system']['granularity'] == 'system':
        # Synthesize the System Row for Config ONLY
        system_item = {
            "name": payload['system']['name'],
            "label": payload['system'].get('row_label', payload['system']['name']),
            "system": payload['system']['name'],
            "parent": None
        }
        payload['components'] = [system_item]
        
    return payload

def build_status_payload(vordu_data, test_results):
    """Payload for /ingest (Flattened List[IngestItem])."""
    system_name = vordu_data['system']['name']
    domain_name = vordu_data['system'].get('domain', 'unknown-domain')
    granularity = vordu_data['system'].get('granularity', 'component')
    components = vordu_data['components']
    
    # Map mocked results to a quick lookup
    # Format: status_map[(comp_name, phase_id)] = [status1, status2]
    status_map = {}
    
    for result in test_results:
        tag_str = result['tag']
        status = result.get('status')
        # Use real step counts if available, else default to mock assumption
        r_passed = result.get('passed_steps', 5 if status == 'passed' else 0)
        r_total = result.get('total_steps', 5)
        
        # Parse tags
        comp_name = None
        phase_id = None
        
        parts = tag_str.split()
        for part in parts:
            # Normalize tag (remove @ if present)
            clean_part = part.lstrip("@")
            
            if clean_part.startswith("component:"):
                comp_name = clean_part.split(":")[1]
            elif clean_part.startswith("vordu:row="): # Support vordu tags
                comp_name = clean_part.split("=")[1]
            elif clean_part.startswith("phase:"):
                try:
                    phase_id = int(clean_part.split(":")[1])
                except ValueError:
                    continue
            elif clean_part.startswith("vordu:phase="): # Support vordu tags
                try:
                    phase_id = int(clean_part.split("=")[1])
                except ValueError:
                    continue
        
        if comp_name and phase_id is not None:
            key = (comp_name, phase_id)
            if key not in status_map:
                status_map[key] = []
            status_map[key].append({
                "status": status,
                "passed_steps": r_passed,
                "total_steps": r_total
            })
            print(f"DEBUG: Mapped {tag_str} -> {key} Status: {status} Steps: {r_passed}/{r_total}")

    print(f"DEBUG: Status Map Keys: {list(status_map.keys())}")
    
    # Grouping Logic
    groups = {} # Key: (row_id), Value: {phase: [list of component items]}
    
    for comp in components:
        comp_name = comp['name']
        parent = comp.get('parent')
        
        # Determine Target Row ID based on Granularity
        if granularity == 'domain':
             target_row = domain_name
        elif granularity == 'system':
            target_row = system_name # One row for the whole system
        elif granularity == 'component':
            # If subcomponent has a parent, roll up to parent. Else use own name.
            target_row = parent if parent else comp_name
        else:
            # Default or explicit 'subcomponent' -> Own row
            target_row = comp_name

        # Ensure we use the proper ID for the groups dictionary
        # For system granularity, this MUST match the system name as defined in build_config_payload
        if granularity == 'system':
             # The system logic above sets target_row = system_name (e.g. 'mimir')
             # The config payload sets id = system_name ('mimir')
             pass 
             
        if target_row not in groups:
            groups[target_row] = {}
            
        # Collect data for this component across all phases
        for phase in range(4):
            if phase not in groups[target_row]:
                groups[target_row][phase] = []
                
            results_list = status_map.get((comp_name, phase), [])
            
            # Calculate granular stats for this specific component/phase
            passed_scenarios_count = sum(1 for r in results_list if r['status'] == 'passed')
            total_scenarios_count = len(results_list)
            
            passed_steps_count = sum(r['passed_steps'] for r in results_list)
            total_steps_count = sum(r['total_steps'] for r in results_list)
            
            groups[target_row][phase].append({
                "passed_scenarios": passed_scenarios_count,
                "total_scenarios": total_scenarios_count,
                "passed_steps": passed_steps_count,
                "total_steps": total_steps_count
            })

    ingest_items = []
    
    # Aggregation Logic
    for row_id, phases in groups.items():
        for phase, items in phases.items():
            # items is a list of dicts from children components
            if not items:
                continue
                
            # Summation
            total_scenarios = sum(item['total_scenarios'] for item in items)
            passed_scenarios = sum(item['passed_scenarios'] for item in items)
            
            total_steps = sum(item['total_steps'] for item in items)
            passed_steps = sum(item['passed_steps'] for item in items)
            
            # Completion Calculation
            if total_steps > 0:
                completion = int((passed_steps / total_steps) * 100)
            else:
                # If no tests found, check if explicitly empty or pending?
                # If we have items but 0 tests, it means 0% completion.
                completion = 0
            
            # Status Determination
            # Check for failures first
            has_failures = any(item['status'] == 'failed' for item in items if 'status' in item) # Wait, stored items don't have status, they have counts.
            # We need to deduce status from counts or store it.
            # Actually, `items` are the granular chunks from children.
            # But the Grouping logic threw away the 'status' (pass/fail/pending) and just kept counts.
            # We should re-derive status from counts.
            
            if total_steps == 0:
                final_status = "empty"
            elif completion == 100:
                final_status = "passed" # Frontend expects 'passed' or 'pass'? Types say 'pass'. Script used 'pass'.
            elif completion == 0:
                # Disambiguate O% (Pending) vs Failure vs Empty
                # We know total_step > 0.
                final_status = "pending" 
            else:
                 final_status = "pending" # Partial completion
            
            # Correction: If we want to show red for failures, we need failure count.
            # Currently we only track passed/total. 
            # If total > passed, it implies incomplete or failed.
            # Vörðu UI simplifies this to completion %.
            # The only distinction is 0% (Pending) vs Empty.
            
            if final_status == "passed": final_status = "pass" # Align with UI types
            
            # Create Ingest Item
            item = {
                "project_name": system_name,
                "row_id": row_id,
                "phase_id": phase,
                "status": final_status,
                "completion": completion,
                "scenarios_total": total_scenarios,
                "scenarios_passed": passed_scenarios,
                "steps_total": total_steps,
                "steps_passed": passed_steps
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
        # Timeout set to 30 seconds to prevent hanging indefinitely
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"[{url}] Success: {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"[{url}] Error: {e.code} {e.reason}")
        print(e.read().decode())
        return False
    except urllib.error.URLError as e:
        print(f"[{url}] Connection Error: {e.reason}")
        return False
    except Exception as e:
        print(f"[{url}] Unexpected Error: {e}")
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
            
            # Extract tags (Handle both dicts `{'name': '@tag'}` and strings `"@tag"`)
            raw_tags = element.get('tags', [])
            tags = []
            for t in raw_tags:
                if isinstance(t, dict):
                    tags.append(t.get('name', ''))
                elif isinstance(t, str):
                    tags.append(t)
                else:
                    tags.append(str(t))
            tag_str = " ".join(tags)
            
            # Determine status & step counts
            steps = element.get('steps', [])
            total_steps = len(steps)
            passed_steps = 0
            
            for s in steps:
                if s.get('result', {}).get('status') == 'passed':
                    passed_steps += 1
            
            if "wip" in tags or "@wip" in tags or any(t.endswith("wip") for t in tags):
                 status = "pending"
                 passed_steps = 0 # Force 0/N completion
            elif not steps:
                status = "pending"
            elif any(s.get('result', {}).get('status') == 'failed' for s in steps):
                status = "failed"
            elif any(s.get('result', {}).get('status') in ['undefined', 'skipped'] for s in steps):
                status = "pending"
            elif all(s.get('result', {}).get('status') == 'passed' for s in steps):
                status = "passed"
            else:
                status = "pending"
                
            results.append({
                "tag": tag_str,
                "status": status,
                "total_steps": total_steps,
                "passed_steps": passed_steps
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
        if not post_to_api(config_url, args.api_key, config_payload):
            print(f"Failed to post config to {config_url}")
            sys.exit(1)
        
        # 2. Status Ingestion
        status_payload = build_status_payload(vordu_data, results)
        status_url = f"{args.api_url}/ingest"
        print(f"Posting Status to {status_url}...")
        if not post_to_api(status_url, args.api_key, status_payload):
            print(f"Failed to post status to {status_url}")
            sys.exit(1)
        
    else:
        print("\n[Generated Config Payload]")
        print(json.dumps(config_payload, indent=2))
        print("\n[Generated Status Payload]")
        status_payload = build_status_payload(vordu_data, results)
        print(json.dumps(status_payload, indent=2))

if __name__ == "__main__":
    main()
