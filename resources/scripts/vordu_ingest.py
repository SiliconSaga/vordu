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
        {"feature": "Vörðu API", "name": "Ingest Cucumber JSON", "tag": "@component:vordu-api @phase:1", "status": "passed"},
        {"feature": "Autoboros Agent", "name": "Spawn Agent", "tag": "@component:autoboros-agent @phase:1", "status": "failed"},
        
        # Mimir Data mocks left simple for now as they are checked via logic usually
        # But should be updated if used heavily. For now, just fix structure to avoid crash.
        {"feature": "Mimir", "name": "Kafka Test", "tag": "@component:mimir-kafka @phase:0", "status": "passed"},
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
            
            # Store full result object for details
            detail_item = {
                "feature": result.get('feature', 'Unknown'),
                "scenario": result.get('name', 'Unknown'), # Normalize key to 'scenario' for UI
                "status": status,
                "passed_steps": r_passed,
                "total_steps": r_total,
                "tag": tag_str,
                "steps": result.get('steps', []) # Add steps key
            }
            
            status_map[key].append(detail_item)
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
                "total_steps": total_steps_count,
                "details": results_list # Store the raw list of scenarios for aggregation
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
            
            # Aggregate Details
            all_details = []
            for item in items:
                all_details.extend(item.get('details', []))
            
            # Completion Calculation
            if total_steps > 0:
                completion = int((passed_steps / total_steps) * 100)
            else:
                completion = 0
            
            # Status Determination
            if total_steps == 0 and total_scenarios == 0:
                final_status = "empty"
            elif completion == 100:
                final_status = "passed"
            elif completion == 0:
                final_status = "pending"
            else:
                 final_status = "pending" # Partial completion
            
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
                "steps_passed": passed_steps,
                "details": all_details
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
        feature_name = feature.get('name', 'Unknown Feature')
        
        for element in feature.get('elements', []):
            if element['type'] != 'scenario':
                continue
            
            scenario_name = element.get('name', 'Unknown Scenario')
            
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
                 total_steps = 0  # Force 0 total steps for WIP to hide counts
            elif not steps:
                status = "pending"
                total_steps = 0
            elif any(s.get('result', {}).get('status') == 'failed' for s in steps):
                status = "failed"
            elif any(s.get('result', {}).get('status') in ['undefined', 'skipped'] for s in steps):
                status = "pending"
                total_steps = 0 # Treat skipped/undefined as having no visible steps
            elif all(s.get('result', {}).get('status') == 'passed' for s in steps):
                status = "passed"
            else:
                status = "pending"
                total_steps = 0
                
            # Collect step details
            step_details = []
            for s in steps:
                step_details.append({
                    "keyword": s.get('keyword', ''),
                    "name": s.get('name', ''),
                    "status": s.get('result', {}).get('status', 'undefined')
                })

            results.append({
                "feature": feature_name,
                "name": scenario_name,
                "tag": tag_str,
                "status": status,
                "total_steps": total_steps,
                "passed_steps": passed_steps,
                "steps": step_details # Store detailed steps
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
    
    # NEW: Phase A - Direct Feature Scanning (Planned Work)
    print("Scanning feature files for planned scenarios...")
    # Assume feature files are in a standard location relative to catalog or use current dir
    # For now, we search recursively in current working directory
    # Ideally this root should be configurable or relative to catalog file dir
    root_dir = os.path.dirname(os.path.abspath(args.catalog))
    scanned_features = scan_feature_files(root_dir, vordu_data['system'])
    print(f"Found {len(scanned_features)} planned scenarios.")

    if args.report:
        print(f"Parsing test results from {args.report}...")
        results = parse_cucumber_json(args.report)
    else:
        print("Using Mock BDD results (No report provided).")
        results = mock_bdd_results()
        
    # NEW: Phase B - Merge Logic
    # We want to create a master list of results.
    # 1. Start with Scanned Scenarios (Status: Planned/Pending)
    # 2. Overlay Execution Results (Status: Pass/Fail/Skip -> Pending)
    
    # Create a lookup for results by (Feature, Scenario)
    result_map = {}
    for r in results:
        key = (r.get('feature'), r.get('name'))
        result_map[key] = r
    
    merged_results = []
    
    for scanned in scanned_features:
        key = (scanned['feature'], scanned['name'])
        
        if key in result_map:
             # Found execution result -> Use it
             # Use Scanned Tags (includes conventions) + Result Status
             result = result_map[key]
             merged_item = scanned.copy()
             merged_item['status'] = result['status']
             merged_item['total_steps'] = result['total_steps']
             merged_item['passed_steps'] = result['passed_steps']
             merged_item['steps'] = result.get('steps', []) # Fix: Copy steps to merged item
             
             merged_results.append(merged_item)
             # Mark as used
             del result_map[key]
        else:
             # No result -> It is Planned
             merged_results.append(scanned)
             
    # Add any remaining results (Dynamic/Generated tests?)
    for r in result_map.values():
        merged_results.append(r)
            
    final_results = merged_results

    if args.api_url:
        config_url = f"{args.api_url}/config/ingest"
        print(f"Posting Config to {config_url}...")
        if not post_to_api(config_url, args.api_key, config_payload):
            print(f"Failed to post config to {config_url}")
            sys.exit(1)
        
        # 2. Status Ingestion (Using Merged Results)
        status_payload = build_status_payload(vordu_data, final_results)
        status_url = f"{args.api_url}/ingest"
        print(f"Posting Status to {status_url}...")
        if not post_to_api(status_url, args.api_key, status_payload):
            print(f"Failed to post status to {status_url}")
            sys.exit(1)
        
    else:
        print("\n[Generated Config Payload]")
        print(json.dumps(config_payload, indent=2))
        print("\n[Generated Status Payload]")
        status_payload = build_status_payload(vordu_data, final_results)
        print(json.dumps(status_payload, indent=2))

def deduce_component_from_path(file_path, system_name):
    """
    Deduces component name from file path conventions.
    1. features/<name>/*.feature -> system-<name>
    2. features/<name>.feature -> system-<name>
    """
    # Normalize path separators
    path = file_path.replace('\\', '/')
    parts = path.split('/')
    
    filename = parts[-1]
    name_no_ext = os.path.splitext(filename)[0]
    
    # Logic: Look for 'features' dir
    try:
        features_idx = parts.index('features')
        # Check Subdirectory (Rule 2)
        if len(parts) > features_idx + 2:
            subdir = parts[features_idx + 1]
            return f"{system_name}-{subdir}"
        
        # Check Filename (Rule 3)
        if len(parts) == features_idx + 2:
             return f"{system_name}-{name_no_ext}"
             
    except ValueError:
        pass
        
    return None

def scan_feature_files(root_dir, system_info):
    """Scans .feature files for scenarios and interprets tags/conventions."""
    import glob
    import re
    
    scanned_items = []
    system_name = system_info['name']
    
    # Find all feature files recursively
    # Use glob with recursive flag
    pattern = os.path.join(glob.escape(root_dir), "**", "*.feature")
    files = glob.glob(pattern, recursive=True)
    
    for file_path in files:
        # Determine Convention Component
        convention_comp = deduce_component_from_path(file_path, system_name)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_tags = []
        current_feature_name = "Unknown Feature"
        current_scenario = None
        current_feature_tags = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Naive Gherkin Parsing
            if line.startswith('@'):
                # Tag line
                current_tags.extend(line.split())
            elif line.startswith('Feature:'):
                 # Extract Feature Name
                 parts = line.split(':', 1)
                 if len(parts) > 1:
                     current_feature_name = parts[1].strip()
                 current_feature_tags = list(current_tags) # Capture feature tags
                 current_tags = [] # Reset tags specifically for next element (Background/Rule/Scenario)
            elif line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                # Found a Scenario
                parts = line.split(':', 1)
                scenario_name = parts[1].strip() if len(parts) > 1 else "Unknown"

                # Determine Tags
                final_tags = list(current_feature_tags) + list(current_tags)
                tag_str = " ".join(final_tags)
                
                # Check if explicit row tag exists
                has_row_tag = any(t.startswith("@vordu:row=") or t.startswith("@component:") for t in final_tags)
                
                if not has_row_tag and convention_comp:
                    # Apply Convention Tag
                    # We inject it into the tag string so build_status_payload can parse it
                    tag_str += f" @component:{convention_comp}"
                
                # Prepare for next scenario but also capture this one
                if current_scenario:
                     scanned_items.append(current_scenario)
                
                current_scenario = {
                    "feature": current_feature_name,
                    "name": scenario_name,
                    "tag": tag_str,
                    "status": "pending",
                    "total_steps": 0,
                    "passed_steps": 0,
                    "steps": []
                }
                
                current_tags = [] # Reset for next scenario
            elif line.startswith('#'):
                 pass
            elif any(line.startswith(k) for k in ['Given', 'When', 'Then', 'And', 'But']) and current_scenario:
                 # It is a step
                 parts = line.split(maxsplit=1)
                 keyword = parts[0]
                 name = parts[1] if len(parts) > 1 else ""
                 
                 current_scenario['steps'].append({
                     "keyword": keyword,
                     "name": name,
                     "status": "pending"
                 })
                 current_scenario['total_steps'] += 1
            else:
                 pass
                 
    # Append the last found scenario
    if current_scenario:
        scanned_items.append(current_scenario)
                 
    return scanned_items

if __name__ == "__main__":
    main()
