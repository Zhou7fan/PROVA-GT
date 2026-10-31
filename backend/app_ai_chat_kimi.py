"""
AI Chatbot Service (Port 5005)
Kimi (Moonshot) powered chatbot with tool calling for qualitative research.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import json
import os
import uuid
import chardet
import requests
from config import require_env

app = Flask(__name__)
CORS(app)

                                                                              
MOONSHOT_API_KEY = require_env("MOONSHOT_API_KEY")
client = OpenAI(api_key=MOONSHOT_API_KEY, base_url="https://api.moonshot.cn/v1")
MODEL = "moonshot-v1-128k"

                                                                               
MEMOS_FILE = 'memos.json'
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '../frontend/uploads')
PASSAGE_DB_FILE = 'passage_database.json'                                 
EMBEDDING_API = 'http://localhost:5003'                  

                                                                               
sessions = {}                                                                 

                                                                               

def load_memos():
    if not os.path.exists(MEMOS_FILE):
        return []
    with open(MEMOS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_memos(memos):
    with open(MEMOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(memos, f, ensure_ascii=False, indent=2)

def get_passage_database(session_id):
    """Return passageDatabase for a session (posted from frontend)."""
    s = sessions.get(session_id)
    return s.get('passage_database', {}) if s else {}

def get_stage_order(pdb):
    """Extract ordered unique stages from passageDatabase."""
    stage_set = set()
    for p in pdb.values():
        for s in p.get('stages', []):
            stage_set.add(s)
                                                    
    ordered = []
    for p in pdb.values():
        for s in p.get('stages', []):
            if s not in ordered:
                ordered.append(s)
    return ordered

                                                                                
                       
                                                                                

def tool_identify_code(pdb, code_name):
    code_lower = code_name.lower()
    is_first = False
    is_second = False
    passages_first = []
    passages_second = []
    foc_counts = {}
    soc_counts = {}

    for pname, p in pdb.items():
        for foc in p.get('firstOrderCodes', []):
            foc_counts[foc] = foc_counts.get(foc, 0) + 1
            if foc.lower() == code_lower:
                is_first = True
                if pname not in passages_first:
                    passages_first.append(pname)
        for soc in p.get('secondOrderCodes', []):
            if soc:
                soc_counts[soc] = soc_counts.get(soc, 0) + 1
                if soc.lower() == code_lower:
                    is_second = True
                    if pname not in passages_second:
                        passages_second.append(pname)

                                 
    sorted_focs = [{"code": k, "count": v} for k, v in sorted(foc_counts.items(), key=lambda x: x[1])]
    sorted_socs = [{"code": k, "count": v} for k, v in sorted(soc_counts.items(), key=lambda x: x[1])]

    return {
        "code": code_name,
        "is_first_order": is_first,
        "is_second_order": is_second,
        "passages_as_first_order": passages_first,
        "passages_as_second_order": passages_second,
        "all_first_order_codes_with_freq": sorted_focs,
        "all_second_order_codes_with_freq": sorted_socs
    }


def tool_read_first_order_code(pdb, code_names):
    if isinstance(code_names, str):
        code_names = [code_names]
    code_names_lower = [c.lower() for c in code_names]
    results = []
    for pname, p in pdb.items():
        for i, foc in enumerate(p.get('firstOrderCodes', [])):
            if foc.lower() in code_names_lower:
                results.append({
                    "code": foc,
                    "passage": pname,
                    "stage": p['stages'][i] if i < len(p.get('stages', [])) else '',
                    "sentence": p['sentences'][i] if i < len(p.get('sentences', [])) else '',
                    "explanation": p['explanations'][i] if i < len(p.get('explanations', [])) else ''
                })
    return {"codes": code_names, "count": len(results), "details": results}


def tool_read_second_order_code(pdb, second_code_names):
    if isinstance(second_code_names, str):
        second_code_names = [second_code_names]
    socs_lower = [s.lower() for s in second_code_names]
    stage_focs = {}                                      

    for pname, p in pdb.items():
        for i, soc in enumerate(p.get('secondOrderCodes', [])):
            soc_val = soc or ''
            if soc_val.lower() in socs_lower:
                foc = p['firstOrderCodes'][i]
                stage = p['stages'][i] if i < len(p.get('stages', [])) else 'unknown'
                soc_lower_key = soc_val.lower()
                if soc_lower_key not in stage_focs:
                    stage_focs[soc_lower_key] = {}
                if stage not in stage_focs[soc_lower_key]:
                    stage_focs[soc_lower_key][stage] = {}
                stage_focs[soc_lower_key][stage][foc] = stage_focs[soc_lower_key][stage].get(foc, 0) + 1

    lines = []
    stage_order = get_stage_order(pdb)
    for soc in second_code_names:
        lines.append(f'Second-Order Code: "{soc}"')
        soc_stages = stage_focs.get(soc.lower(), {})
        for stage in stage_order:
            if stage in soc_stages:
                lines.append(f'Stage "{stage}":')
                for foc, count in sorted(soc_stages[stage].items(), key=lambda x: -x[1]):
                    lines.append(f'  - {foc} ({count})')
        lines.append('')
    return "\n".join(lines).strip()


def tool_read_first_order_link(pdb, code1, code2):
    c1_lower, c2_lower = code1.lower(), code2.lower()
    results = []
    for pname, p in pdb.items():
        focs = p.get('firstOrderCodes', [])
        idx1 = next((i for i, f in enumerate(focs) if f.lower() == c1_lower), None)
        idx2 = next((i for i, f in enumerate(focs) if f.lower() == c2_lower), None)
        if idx1 is not None and idx2 is not None:
            results.append({
                "passage": pname,
                "code1": {
                    "code": focs[idx1],
                    "stage": p['stages'][idx1] if idx1 < len(p.get('stages', [])) else '',
                    "sentence": p['sentences'][idx1] if idx1 < len(p.get('sentences', [])) else '',
                    "explanation": p['explanations'][idx1] if idx1 < len(p.get('explanations', [])) else ''
                },
                "code2": {
                    "code": focs[idx2],
                    "stage": p['stages'][idx2] if idx2 < len(p.get('stages', [])) else '',
                    "sentence": p['sentences'][idx2] if idx2 < len(p.get('sentences', [])) else '',
                    "explanation": p['explanations'][idx2] if idx2 < len(p.get('explanations', [])) else ''
                }
            })
    return {"code1": code1, "code2": code2, "co_occurrences": len(results), "details": results}


def tool_read_second_order_link(pdb, soc1, soc2):
    soc1_lower, soc2_lower = soc1.lower(), soc2.lower()
    stage_order = get_stage_order(pdb)

                               
    code_to_soc = {}
    for pname, p in pdb.items():
        for i, foc in enumerate(p.get('firstOrderCodes', [])):
            stage = p['stages'][i] if i < len(p.get('stages', [])) else ''
            soc = (p['secondOrderCodes'][i] if i < len(p.get('secondOrderCodes', [])) else '') or 'unclassified'
            code_to_soc[f"{foc}#{stage}"] = f"{soc}#{stage}"

                                                                
    passage_path_tracker = {}
    for pname, p in pdb.items():
        stage_map = {}
        for i, foc in enumerate(p.get('firstOrderCodes', [])):
            stage = p['stages'][i] if i < len(p.get('stages', [])) else ''
            stage_map.setdefault(stage, []).append(f"{foc}#{stage}")
                                             
        for si in range(len(stage_order) - 1):
            s1, s2 = stage_order[si], stage_order[si + 1]
            for c1 in stage_map.get(s1, []):
                for c2 in stage_map.get(s2, []):
                    key = f"{c1}|{c2}"
                    passage_path_tracker.setdefault(key, set()).add(pname)

                            
    stage_pair_links = {}
    for path_key, passages in passage_path_tracker.items():
        src_key, tgt_key = path_key.split('|')
        src_soc_stage = code_to_soc.get(src_key)
        tgt_soc_stage = code_to_soc.get(tgt_key)
        if not src_soc_stage or not tgt_soc_stage:
            continue
        src_soc = src_soc_stage.split('#')[0]
        tgt_soc = tgt_soc_stage.split('#')[0]
        match = {src_soc.lower(), tgt_soc.lower()} == {soc1_lower, soc2_lower}
        if match:
            src_foc = src_key.split('#')[0]
            tgt_foc = tgt_key.split('#')[0]
            src_stage = src_key.split('#')[1]
            tgt_stage = tgt_key.split('#')[1]
            pair_key = f"{src_stage} -> {tgt_stage}"
            stage_pair_links.setdefault(pair_key, []).append({
                "source": src_foc, "target": tgt_foc, "value": len(passages)
            })

            
    lines = [f'Second-Order Link: "{soc1}" <-> "{soc2}"']
    for pair_key in stage_pair_links:
        lines.append(f'{pair_key}:')
        for link in sorted(stage_pair_links[pair_key], key=lambda x: -x['value']):
            lines.append(f'  - {link["source"]} -> {link["target"]} (value: {link["value"]})')
    if not stage_pair_links:
        lines.append('No cross-stage links found between these two second-order codes.')
    return "\n".join(lines)


def tool_simi_search(pdb, code, similarity=0.3):
    all_codes = set()
    code_types = {}
    code_freq = {}
    for p in pdb.values():
        for foc in p.get('firstOrderCodes', []):
            all_codes.add(foc)
            code_types.setdefault(foc, set()).add('first-order')
            code_freq[foc] = code_freq.get(foc, 0) + 1
        for soc in p.get('secondOrderCodes', []):
            if soc:
                all_codes.add(soc)
                code_types.setdefault(soc, set()).add('second-order')
                code_freq[soc] = code_freq.get(soc, 0) + 1

    all_codes_list = list(all_codes)
    if not all_codes_list:
        return {"query": code, "results": []}

    try:
        resp = requests.post(f"{EMBEDDING_API}/api/process", json={
            "pocketName": code,
            "updatedData": all_codes_list
        }, timeout=30)
        data = resp.json()
        sims = data.get('similarities', {})
    except Exception as e:
        return {"query": code, "error": str(e)}

    results = []
    for name, score in sims.items():
        if score >= similarity:
            types = list(code_types.get(name, ['unknown']))
            results.append({"code": name, "similarity": round(score, 4), "type": types[0], "frequency": code_freq.get(name, 0)})
    results.sort(key=lambda x: (x.get('frequency', 0), x['similarity']))
    return {"query": code, "threshold": similarity, "results": results}


def tool_deep_search(passage_name):
    filepath = os.path.join(UPLOAD_FOLDER, passage_name)
    if not os.path.exists(filepath):
                                   
        filepath = os.path.join(UPLOAD_FOLDER, passage_name + '.txt')
    if not os.path.exists(filepath):
        return {"error": f"File not found: {passage_name}"}
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
            enc = chardet.detect(raw)['encoding'] or 'utf-8'
        with open(filepath, 'r', encoding=enc) as f:
            text = f.read()
        return {"passage": passage_name, "length": len(text), "text": text}
    except Exception as e:
        return {"error": str(e)}


def tool_list_memos():
    memos = load_memos()
    return [{"id": m["id"], "type": m["type"], "title": m.get("title", "")} for m in memos]


def tool_read_memo(id_or_title, pdb=None):
    memos = load_memos()
    for m in memos:
        if m["id"] == id_or_title or (m.get("title") or '').lower() == id_or_title.lower():
            res = {"id": m["id"], "type": m["type"], "title": m.get("title", ""), "content": m.get("content", "")}
            
            if m["type"] == "Cluster Analysis Notes" and m.get("clusterData"):
                res["first_order_codes_in_cluster"] = m["clusterData"]
            elif pdb is not None:
                title = m.get("title", "").strip().lower()
                if m["type"] == "First-Order Code Notes" and title:
                    trace = []
                    for pname, p in pdb.items():
                        for i, foc in enumerate(p.get('firstOrderCodes', [])):
                            if foc.lower() == title:
                                trace.append({
                                    "passage": pname,
                                    "explanation": p.get('explanations', [])[i] if i < len(p.get('explanations', [])) else '',
                                    "sentence": p.get('sentences', [])[i] if i < len(p.get('sentences', [])) else ''
                                })
                    if trace:
                        res["search_analyze_results"] = trace
                elif m["type"] == "Second-Order Code Notes" and title:
                    trace = []
                    for pname, p in pdb.items():
                        for i, foc in enumerate(p.get('firstOrderCodes', [])):
                            soc = p.get('secondOrderCodes', [])[i] if i < len(p.get('secondOrderCodes', [])) else ''
                            soc_str = soc if soc is not None else ''
                            if soc_str.lower() == title:
                                trace.append({
                                    "code": foc,
                                    "passage": pname,
                                    "explanation": p.get('explanations', [])[i] if i < len(p.get('explanations', [])) else ''
                                })
                    if trace:
                        res["search_analyze_results"] = trace
                elif m["type"] == "Theoretical Memos" and title:
                    import re
                    parts = re.split(r'\s*[—\-]\s*', m.get("title", ""))
                    if len(parts) >= 2:
                        code1, code2 = parts[0].strip().lower(), parts[1].strip().lower()
                        trace = []
                        for pname, p in pdb.items():
                            focs = [f.lower() for f in p.get('firstOrderCodes', [])]
                            if code1 in focs and code2 in focs:
                                idx1, idx2 = focs.index(code1), focs.index(code2)
                                trace.append({
                                    "passageName": pname,
                                    "code1Data": {
                                        "code": p.get('firstOrderCodes', [])[idx1],
                                        "explanation": p.get('explanations', [])[idx1] if idx1 < len(p.get('explanations', [])) else '',
                                        "sentence": p.get('sentences', [])[idx1] if idx1 < len(p.get('sentences', [])) else ''
                                    },
                                    "code2Data": {
                                        "code": p.get('firstOrderCodes', [])[idx2],
                                        "explanation": p.get('explanations', [])[idx2] if idx2 < len(p.get('explanations', [])) else '',
                                        "sentence": p.get('sentences', [])[idx2] if idx2 < len(p.get('sentences', [])) else ''
                                    }
                                })
                        if trace:
                            res["search_analyze_results"] = trace
            return res
    return {"error": f"Memo not found: {id_or_title}"}


                                                                               

def tool_create_memo(memo_type, title, content):
    memos = load_memos()
    new_memo = {
        "id": str(int(__import__('time').time() * 1000)),
        "title": title,
        "type": memo_type,
        "content": content,
        "timestamp": int(__import__('time').time() * 1000)
    }
    memos.insert(0, new_memo)
    save_memos(memos)
    return {"status": "created", "id": new_memo["id"], "title": title}


def tool_update_memo(memo_id, title=None, content=None):
    memos = load_memos()
    for m in memos:
        if m["id"] == memo_id:
            if title is not None:
                m["title"] = title
            if content is not None:
                m["content"] = content
            save_memos(memos)
            return {"status": "updated", "id": memo_id}
    return {"error": f"Memo not found: {memo_id}"}


def tool_delete_memo(memo_id):
    memos = load_memos()
    new_memos = [m for m in memos if m["id"] != memo_id]
    if len(new_memos) == len(memos):
        return {"error": f"Memo not found: {memo_id}"}
    save_memos(new_memos)
    return {"status": "deleted", "id": memo_id}


def tool_create_second_and_absorb(pdb, second_code_names, similarity=0.35):
    """Create new SOCs and absorb similar unclassified FOCs."""
    if isinstance(second_code_names, str):
        second_code_names = [second_code_names]
        
                               
    unclassified_focs = set()
    for pname, p in pdb.items():
        for i, foc in enumerate(p.get('firstOrderCodes', [])):
            soc = p.get('secondOrderCodes', [])[i] if i < len(p.get('secondOrderCodes', [])) else ''
            if not soc or soc.lower() == 'unclassified':
                unclassified_focs.add(foc)
                
    unclassified_list = list(unclassified_focs)
    if not unclassified_list:
        return {"status": "no_unclassified_codes"}

                                                             
    soc_similarities = {}                          
    for foc in unclassified_list:
        soc_similarities[foc] = {}
        
    for soc in second_code_names:
        try:
            resp = requests.post(f"{EMBEDDING_API}/api/process", json={
                "pocketName": soc,
                "updatedData": unclassified_list
            }, timeout=30)
            sims = resp.json().get('similarities', {})
            for foc, score in sims.items():
                soc_similarities[foc][soc] = score
        except Exception as e:
                                                                              
            for foc in unclassified_list:
                if soc.lower() in foc.lower() or foc.lower() in soc.lower():
                                                                     
                    soc_similarities[foc][soc] = 1.0 
                else:
                    soc_similarities[foc].setdefault(soc, 0.0)
            
                                                               
    absorbed = {}                        
    for soc in second_code_names:
        absorbed[soc] = []
        
    foc_to_soc = {}
    for foc, sims in soc_similarities.items():
        best_soc = None
        best_score = -1
        for soc, score in sims.items():
            if score > best_score:
                best_score = score
                best_soc = soc
        if best_score >= similarity and best_soc:
            foc_to_soc[foc] = best_soc
            absorbed[best_soc].append(foc)
            
                
    for pname, p in pdb.items():
        for i, foc in enumerate(p.get('firstOrderCodes', [])):
            soc = p.get('secondOrderCodes', [])[i] if i < len(p.get('secondOrderCodes', [])) else ''
            if not soc or soc.lower() == 'unclassified':
                if foc in foc_to_soc:
                    while len(p.get('secondOrderCodes', [])) <= i:
                        p.setdefault('secondOrderCodes', []).append('')
                    p['secondOrderCodes'][i] = foc_to_soc[foc]
                    
    return {
        "status": "created_and_absorbed",
        "second_codes": second_code_names,
        "similarity_threshold": similarity,
        "absorbed_first_order_codes": absorbed
    }


def tool_add_first_to_second(pdb, assignments):
    """Assign lists of FOCs to SOCs in passageDatabase."""
    modified = 0
    for a in assignments:
        soc = a.get("second_code")
        first_lower = [f.lower() for f in a.get("first_codes", [])]
        for pname, p in pdb.items():
            for i, foc in enumerate(p.get('firstOrderCodes', [])):
                if foc.lower() in first_lower:
                    while len(p.setdefault('secondOrderCodes', [])) <= i:
                        p['secondOrderCodes'].append('')
                    p['secondOrderCodes'][i] = soc
                    modified += 1
    return {
        "status": "assigned",
        "assignments": assignments,
        "modified_entries": modified
    }


def tool_remove_first(pdb, first_codes):
    """Make specified FOCs unclassified."""
    first_lower = [f.lower() for f in first_codes]
    modified = 0
    for pname, p in pdb.items():
        for i, foc in enumerate(p.get('firstOrderCodes', [])):
            if foc.lower() in first_lower:
                if i < len(p.get('secondOrderCodes', [])):
                    p['secondOrderCodes'][i] = ''
                modified += 1
    return {
        "status": "removed",
        "first_codes": first_codes,
        "modified_entries": modified
    }


def tool_split_second(pdb, original_second, new_assignments):
    """Split a SOC into new SOCs with specific FOC assignments."""
    orig_lower = original_second.lower()
    modified = 0
    assigned_focs = {}
    for a in new_assignments:
        for f in a.get("first_codes", []):
            assigned_focs[f.lower()] = a.get("second_code")
            
    for pname, p in pdb.items():
        for i, soc in enumerate(p.get('secondOrderCodes', [])):
            if (soc or '').lower() == orig_lower:
                foc = p.get('firstOrderCodes', [])[i] if i < len(p.get('firstOrderCodes', [])) else ''
                if foc.lower() in assigned_focs:
                    p['secondOrderCodes'][i] = assigned_focs[foc.lower()]
                    modified += 1
                else:
                    p['secondOrderCodes'][i] = ''
                    modified += 1
    return {
        "status": "split",
        "original_second": original_second,
        "new_assignments": new_assignments,
        "modified_entries": modified
    }


def tool_merge_second(pdb, second_codes, new_second_code):
    """Merge multiple SOCs into one."""
    seconds_lower = [s.lower() for s in second_codes]
    modified = 0
    for pname, p in pdb.items():
        for i, soc in enumerate(p.get('secondOrderCodes', [])):
            if (soc or '').lower() in seconds_lower:
                p['secondOrderCodes'][i] = new_second_code
                modified += 1
    return {
        "status": "merged",
        "merged_from": second_codes,
        "merged_to": new_second_code,
        "modified_entries": modified
    }


def tool_remove_second(pdb, second_code):
    """Make all FOCs under a specific SOC unclassified."""
    target_lower = second_code.lower()
    modified = 0
    for pname, p in pdb.items():
        socs = p.get('secondOrderCodes', [])
        for i, soc in enumerate(socs):
            if (soc or '').lower() == target_lower:
                p['secondOrderCodes'][i] = ''
                modified += 1
    return {
        "status": "removed_second",
        "second_code": second_code,
        "modified_entries": modified
    }


def tool_merge_memo(memo_ids, new_title):
    """Merge multiple Analytical or Cluster memos into one."""
    memos = load_memos()
    source_memos = [m for m in memos if m["id"] in memo_ids]
    
    if not source_memos:
        return {"error": "No valid memos found for the given IDs."}
    
                                                   
    memo_type = source_memos[0]["type"]
    if memo_type not in ["Analytical Memos", "Cluster Analysis Notes"]:
        return {"error": f"Merge is only supported for 'Analytical Memos' and 'Cluster Analysis Notes', not '{memo_type}'."}
    
    for m in source_memos:
        if m["type"] != memo_type:
            return {"error": "All memos to be merged must be of the same type."}
            
                    
    merged_content = "\n\n---\n\n".join([m.get("content", "") for m in source_memos if m.get("content")])
    
                                      
    merged_cluster_data = None
    if memo_type == "Cluster Analysis Notes":
        cluster_map = {}                                                        
        for m in source_memos:
            for cluster in m.get("clusterData", []):
                code = cluster.get("code")
                if code not in cluster_map:
                    cluster_map[code] = {"code": code, "items": []}
                cluster_map[code]["items"].extend(cluster.get("items", []))
        merged_cluster_data = list(cluster_map.values())
        
    new_memo = {
        "id": str(int(__import__('time').time() * 1000)),
        "title": new_title,
        "type": memo_type,
        "content": merged_content,
        "timestamp": int(__import__('time').time() * 1000)
    }
    if merged_cluster_data:
        new_memo["clusterData"] = merged_cluster_data
        
                                         
    new_memos_list = [m for m in memos if m["id"] not in memo_ids]
    new_memos_list.insert(0, new_memo)
    save_memos(new_memos_list)
    
    return {"status": "merged", "new_id": new_memo["id"], "memo_type": memo_type, "source_count": len(source_memos)}


                                                                                
                                          
                                                                                

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "identify_code",
            "description": "Identify whether a code is a first-order code or second-order code, and which passages it belongs to. Also returns lists of all FOCs and SOCs with their appearance frequencies (sorted by count ascending).",
            "parameters": {
                "type": "object",
                "properties": {
                    "code_name": {"type": "string", "description": "The code name to identify"}
                },
                "required": ["code_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_first_order_code",
            "description": "Read detailed text information (sentence, explanation) for one or more first-order codes, grouped by passage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The first-order code name(s)"
                    }
                },
                "required": ["code_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_second_order_code",
            "description": "Read subordinate first-order codes under one or more second-order codes, grouped by stage with counts. No text details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "second_code_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The second-order code name(s)"
                    }
                },
                "required": ["second_code_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_first_order_link",
            "description": "Find passages where two first-order codes co-occur and return their text details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code1": {"type": "string", "description": "First code"},
                    "code2": {"type": "string", "description": "Second code"}
                },
                "required": ["code1", "code2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_second_order_link",
            "description": "Find cross-stage links between two second-order codes (like Sankey band drill-down), showing first-order code sub-links grouped by stage pair.",
            "parameters": {
                "type": "object",
                "properties": {
                    "soc1": {"type": "string", "description": "First second-order code"},
                    "soc2": {"type": "string", "description": "Second second-order code"}
                },
                "required": ["soc1", "soc2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "simi_search",
            "description": "Search for semantically similar codes using embedding similarity. Returns code name, similarity score, and type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The code to search for similar ones"},
                    "similarity": {"type": "number", "description": "Minimum similarity threshold (default 0.3)", "default": 0.3}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deep_search",
            "description": "Read the full original text of a passage/document for deep analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "passage_name": {"type": "string", "description": "The passage/document file name"}
                },
                "required": ["passage_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_memos",
            "description": "List all memos with their ID, type, and title.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_memo",
            "description": "Read the full content of a specific memo by ID or title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_or_title": {"type": "string", "description": "Memo ID or title"}
                },
                "required": ["id_or_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_memo",
            "description": "Create a new memo. Use this to record analysis results or conversation summaries for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "memo_type": {
                        "type": "string",
                        "enum": ["First-Order Code Notes", "Second-Order Code Notes", "Theoretical Memos", "Analytical Memos", "Cluster Analysis Notes"],
                        "description": "Type of memo"
                    },
                    "title": {"type": "string", "description": "Memo title"},
                    "content": {"type": "string", "description": "Memo content (markdown)"}
                },
                "required": ["memo_type", "title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_memo",
            "description": "Update an existing memo's title and/or content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "memo_id": {"type": "string", "description": "Memo ID"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "content": {"type": "string", "description": "New content (optional)"}
                },
                "required": ["memo_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_memo",
            "description": "Delete a memo by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "memo_id": {"type": "string", "description": "Memo ID"}
                },
                "required": ["memo_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_second_and_absorb",
            "description": "Create new second-order codes and automatically absorb similar unclassified first-order codes using embedding similarity. The FOCs will be assigned to the most similar SOC if above the threshold.",
            "parameters": {
                "type": "object",
                "properties": {
                    "second_code_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of new second-order code names"
                    },
                    "similarity": {"type": "number", "description": "Similarity threshold (default 0.35)", "default": 0.35}
                },
                "required": ["second_code_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_first_to_second",
            "description": "Assign lists of first-order codes to corresponding second-order codes in the passage database. Also use this to specify newly created second-order codes along with their constituent first-order codes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "assignments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "second_code": {"type": "string"},
                                "first_codes": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["second_code", "first_codes"]
                        },
                        "description": "List of assignments"
                    }
                },
                "required": ["assignments"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_first",
            "description": "Remove specified first-order codes from their current second-order codes, making them unclassified.",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of first-order codes to unclassify"
                    }
                },
                "required": ["first_codes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "split_second",
            "description": "Split a second-order code into new sub-categories by explicitly reassigning its constituent first-order codes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "original_second": {"type": "string", "description": "The original second-order code to split"},
                    "new_assignments": {
                         "type": "array",
                         "items": {
                             "type": "object",
                             "properties": {
                                 "second_code": {"type": "string"},
                                 "first_codes": {"type": "array", "items": {"type": "string"}}
                             },
                             "required": ["second_code", "first_codes"]
                         },
                         "description": "How the first-order codes are distributed into new second-order codes"
                    }
                },
                "required": ["original_second", "new_assignments"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "merge_second",
            "description": "Merge multiple second-order codes into a single new second-order code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "second_codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of existing second-order codes to merge"
                    },
                    "new_second_code": {"type": "string", "description": "The new second-order code name"}
                },
                "required": ["second_codes", "new_second_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_second",
            "description": "Remove a second-order code entirely by making all its constituent first-order codes unclassified.",
            "parameters": {
                "type": "object",
                "properties": {
                    "second_code": {"type": "string", "description": "The second-order code to dissolve"}
                },
                "required": ["second_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "merge_memo",
            "description": "Merge multiple memos of the same type (only Analytical Memos or Cluster Analysis Notes) into a single new memo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "memo_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of memo IDs to merge"
                    },
                    "new_title": {"type": "string", "description": "Title for the new merged memo"}
                },
                "required": ["memo_ids", "new_title"]
            }
        }
    }
]

                                            
WRITE_TOOL_NAMES = {"create_memo", "update_memo", "delete_memo", "create_second_and_absorb", "add_first_to_second", "remove_first", "split_second", "merge_second", "remove_second", "merge_memo"}

                                                                                
                  
                                                                                

def execute_tool(tool_name, args, pdb):
    """Execute a tool and return its result as a string."""
    if tool_name == "identify_code":
        result = tool_identify_code(pdb, args["code_name"])
    elif tool_name == "read_first_order_code":
        result = tool_read_first_order_code(pdb, args.get("code_names", [args.get("code_name")] if "code_name" in args else []))
    elif tool_name == "read_second_order_code":
        result = tool_read_second_order_code(pdb, args.get("second_code_names", [args.get("second_code_name")] if "second_code_name" in args else []))
    elif tool_name == "read_first_order_link":
        result = tool_read_first_order_link(pdb, args["code1"], args["code2"])
    elif tool_name == "read_second_order_link":
        result = tool_read_second_order_link(pdb, args["soc1"], args["soc2"])
    elif tool_name == "simi_search":
        result = tool_simi_search(pdb, args["code"], args.get("similarity", 0.3))
    elif tool_name == "deep_search":
        result = tool_deep_search(args["passage_name"])
    elif tool_name == "list_memos":
        result = tool_list_memos()
    elif tool_name == "read_memo":
        result = tool_read_memo(args["id_or_title"], pdb)
    elif tool_name == "create_memo":
        result = tool_create_memo(args["memo_type"], args["title"], args["content"])
    elif tool_name == "update_memo":
        result = tool_update_memo(args["memo_id"], args.get("title"), args.get("content"))
    elif tool_name == "delete_memo":
        result = tool_delete_memo(args["memo_id"])
    elif tool_name == "create_second_and_absorb":
        result = tool_create_second_and_absorb(pdb, args.get("second_code_names", []), args.get("similarity", 0.35))
    elif tool_name == "add_first_to_second":
        result = tool_add_first_to_second(pdb, args.get("assignments", []))
    elif tool_name == "remove_first":
        result = tool_remove_first(pdb, args.get("first_codes", []))
    elif tool_name == "split_second":
        result = tool_split_second(pdb, args.get("original_second", ""), args.get("new_assignments", []))
    elif tool_name == "merge_second":
        result = tool_merge_second(pdb, args.get("second_codes", []), args.get("new_second_code", ""))
    elif tool_name == "remove_second":
        result = tool_remove_second(pdb, args.get("second_code", ""))
    elif tool_name == "merge_memo":
        result = tool_merge_memo(args.get("memo_ids", []), args.get("new_title", ""))
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result


                                                                                
                
                                                                                

SYSTEM_PROMPT = """You are a qualitative research assistant embedded in the PatternWeave coding system.
You have access to the user's coding database (passageDatabase) and memos.

## Data Model
- "passages" = interview/document files. Each passage contains multiple coded items.
- Each coded item has: firstOrderCode, secondOrderCode, explanation, sentence, stage.
- "stages" have a sequential order representing a temporal/logical progression.
- "memos" = researcher's notes (5 types: First-Order Code Notes, Second-Order Code Notes, Theoretical Memos, Analytical Memos, Cluster Analysis Notes).

## Your Behavior
1. When the user mentions a code, FIRST use identify_code to determine its type before other analysis.
2. Use read tools to gather data BEFORE making analytical statements. Do not guess — always check.
3. For write operations (create/update/delete memo, create_second_and_absorb, add_first_to_second), ALWAYS explain your reasoning first, then propose the action by calling the tool. The system will ask the user to confirm before executing.
4. Keep responses academic but accessible. Use structured formatting.
5. When returning large datasets, summarize key patterns rather than listing everything raw.
6. If the user provides attachments (PDFs, text files, or memos), incorporate their content into your analysis.
7. After gathering enough information using read tools, YOU MUST generate a final text response answering the user's query. DO NOT continuously call read tools without providing a summary of your findings.
8. Always verify if you have fully completed the user's task before finishing your response.

## Available Tools
You have 9 read tools (identify_code, read_first_order_code, read_second_order_code, read_first_order_link, read_second_order_link, simi_search, deep_search, list_memos, read_memo) and 8 write tools (create_memo, update_memo, delete_memo, create_second_and_absorb, add_first_to_second, remove_first, split_second, merge_second).

Read tools execute immediately. Write tools require user confirmation before execution."""


                                                                                
                
                                                                                

@app.route('/api/chat/start', methods=['POST'])
def start_session():
    """Start a new chat session. Frontend sends passageDatabase and optional stageOrder."""
    data = request.json or {}
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}],
        "passage_database": data.get("passageDatabase", {}),
        "stage_order": data.get("stageOrder", [])
    }
    return jsonify({"session_id": session_id})


def run_agent_loop(session_id, max_iterations=20):
    """Run the reasoning loop until a write proposal or final text response is produced."""
    session = sessions.get(session_id)
    if not session:
        return {"error": "Invalid session"}, 400
        
    pdb = session["passage_database"]
    tool_calls_log = []
    proposals = []

    for iteration in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=session["messages"],
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.3
            )
        except Exception as e:
                               
            print(f"=== Kimi API Error ===\n{str(e)}\n======================")
            return {"error": f"Kimi API error: {str(e)}"}, 500

        choice = response.choices[0]
        msg = choice.message

                                                               
        if not msg.tool_calls:
            assistant_content = msg.content or ""
            session["messages"].append({"role": "assistant", "content": assistant_content})
            return {
                "response": assistant_content,
                "tool_calls": tool_calls_log,
                "proposals": proposals
            }, 200

                                                         
        assistant_msg = {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in msg.tool_calls
            ]
        }
        if msg.content:                     
            assistant_msg["content"] = msg.content
            
        session["messages"].append(assistant_msg)

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except:
                args = {}

            if tool_name in WRITE_TOOL_NAMES:
                                                                
                proposals.append({
                    "tool_call_id": tc.id,
                    "tool_name": tool_name,
                    "arguments": args
                })
                placeholder = json.dumps({"status": "pending_user_confirmation", "message": "This operation requires user confirmation before execution. Please wait for the user."})
                session["messages"].append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": placeholder
                })
                tool_calls_log.append({
                    "name": tool_name,
                    "arguments": args,
                    "result": placeholder,
                    "is_write": True
                })
            else:
                                                
                result = execute_tool(tool_name, args, pdb)
                session["messages"].append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
                tool_calls_log.append({
                    "name": tool_name,
                    "arguments": args,
                    "result": result,
                    "is_write": False
                })

                                                                        
        if proposals:
            try:
                                                                            
                response2 = client.chat.completions.create(
                    model=MODEL,
                    messages=session["messages"],
                    temperature=0.3
                )
                assistant_content = response2.choices[0].message.content or ""
                session["messages"].append({"role": "assistant", "content": assistant_content})
            except Exception as e:
                print(f"Fallback Summary API Error: {e}")
                assistant_content = ""

            return {
                "response": assistant_content,
                "tool_calls": tool_calls_log,
                "proposals": proposals
            }, 200

                                   
    try:
                           
        response2 = client.chat.completions.create(
            model=MODEL,
            messages=session["messages"],
            temperature=0.3
        )
        assistant_content = response2.choices[0].message.content or "I performed several analysis steps. Please check the results above."
        session["messages"].append({"role": "assistant", "content": assistant_content})
    except Exception as e:
        print(f"Final Fallback API Error: {e}")
        assistant_content = "I performed several analysis steps. Please check the results above."

    return {
        "response": assistant_content,
        "tool_calls": tool_calls_log,
        "proposals": proposals
    }, 200


@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """
    Send a user message. The backend handles the full tool-call loop.
    """
    data = request.json
    session_id = data.get("session_id")
    user_message = data.get("message", "")
    attachments = data.get("attachments", [])

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    session = sessions[session_id]

    if "passageDatabase" in data:
        session["passage_database"] = data["passageDatabase"]
    if "stageOrder" in data:
        session["stage_order"] = data["stageOrder"]

                                         
    full_message = user_message
    if attachments:
        full_message += "\n\n--- Attachments ---"
        for att in attachments:
            full_message += f"\n\n### [{att.get('type', 'file')}] {att.get('name', 'untitled')}\n{att.get('content', '')}"

    session["messages"].append({"role": "user", "content": full_message})

    max_iterations = data.get("max_iterations", 20)
    resp_data, status_code = run_agent_loop(session_id, max_iterations=max_iterations)
    return jsonify(resp_data), status_code


@app.route('/api/chat/confirm', methods=['POST'])
def confirm_operation():
    """User confirms or cancels a proposed write operation."""
    data = request.json
    session_id = data.get("session_id")
    tool_call_id = data.get("tool_call_id")
    confirmed = data.get("confirmed", False)

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    session = sessions[session_id]
    pdb = session["passage_database"]

    if not confirmed:
                                                
        for msg in session["messages"]:
            if msg.get("role") == "tool" and msg.get("tool_call_id") == tool_call_id:
                msg["content"] = json.dumps({"status": "cancelled", "message": "User cancelled the operation."})
                break
        
        session["messages"].append({
            "role": "user",
            "content": "[System: User cancelled the proposed operation. You can revise your plan or wait for the user.]"
        })
        
        max_iterations = data.get("max_iterations", 20)
        resp_data, status_code = run_agent_loop(session_id, max_iterations=max_iterations)
        return jsonify(resp_data), status_code

                                                   
    tool_name = data.get("tool_name")
    args = data.get("arguments", {})

                            
    result = execute_tool(tool_name, args, pdb)
    
                                                
    for msg in session["messages"]:
        if msg.get("role") == "tool" and msg.get("tool_call_id") == tool_call_id:
            msg["content"] = result
            break

    session["messages"].append({
        "role": "user",
        "content": "[System: The tool was successfully executed and applied by the user. Proceed with verifying your progress and fulfilling the user's initial request.]"
    })
    
    max_iterations = data.get("max_iterations", 20)
    resp_data, status_code = run_agent_loop(session_id, max_iterations=max_iterations)
                                                                           
    pdb_tools = {"create_second_and_absorb", "add_first_to_second", "remove_first", "split_second", "merge_second"}
    if tool_name in pdb_tools:
                                                  
        is_error = False
        if isinstance(result, str) and '"error"' in result:
            is_error = True
        elif isinstance(result, dict) and "error" in result:
            is_error = True
            
        if not is_error:
            resp_data["passage_database_modified"] = True
            resp_data["passage_database"] = pdb
    
    return jsonify(resp_data), status_code


@app.route('/api/chat/upload', methods=['POST'])
def upload_attachment():
    """Upload a PDF or TXT file and return extracted text."""
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    filename = file.filename or 'untitled'
    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext == '.pdf':
            try:
                from pypdf import PdfReader
                reader = PdfReader(file.stream)
                text = "\n".join(page.extract_text() or '' for page in reader.pages)
            except ImportError:
                return jsonify({"error": "pypdf not installed. Run: pip install pypdf"}), 500
        elif ext in ('.txt', '.text'):
            raw = file.read()
            enc = chardet.detect(raw)['encoding'] or 'utf-8'
            text = raw.decode(enc)
        else:
            return jsonify({"error": f"Unsupported file type: {ext}. Use PDF or TXT."}), 400

        return jsonify({"filename": filename, "text": text, "length": len(text)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("AI Chat service starting on port 5005...")
    app.run(host='0.0.0.0', port=5005, debug=False)