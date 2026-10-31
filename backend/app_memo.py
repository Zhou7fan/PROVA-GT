from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import requests
from config import require_env

app = Flask(__name__)
CORS(app)

MEMOS_FILE = 'memos.json'
                              
MOONSHOT_API_KEY = require_env("MOONSHOT_API_KEY")

def call_kimi_api(prompt_text):
    """Call the Kimi API to process the prompt."""
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MOONSHOT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "moonshot-v1-32k",
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.3
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        print(f"API Error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

@app.route('/api/memos', methods=['GET'])
def get_memos():
    if not os.path.exists(MEMOS_FILE):
        return jsonify([])
    try:
        with open(MEMOS_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memos', methods=['POST'])
def save_memos():
    try:
        memos = request.json
        with open(MEMOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(memos, f, ensure_ascii=False, indent=2)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memo-ai', methods=['POST'])
def memo_ai():
    data = request.json
    memo_type = data.get('type')
    context = data.get('context', {})

    prompt = ""
    
    if memo_type == 'First-Order Code Notes':
        code = context.get('code', '')
        passage_count = context.get('passageCount', 0)
        passages = context.get('passages', [])
        
        passage_details = "\n".join([
            f"- **{p['passage']}**: {p['explanation']}" 
            for p in passages if p.get('explanation')
        ])
        
        prompt = f"""I am analyzing the First-Order Code: **"{code}"**

This code appears in {passage_count} interview(s)/document(s). Details are as follows:

{passage_details}

Please provide your response in English. Maintain an academic tone that is professional yet accessible."""

    elif memo_type == 'Second-Order Code Notes':
        soc = context.get('secondOrderCode', '')
        focs = context.get('firstOrderCodes', [])
        
        foc_grouped = {}
        for f in focs:
            code = f.get('code', '')
            if code not in foc_grouped:
                foc_grouped[code] = []
            foc_grouped[code].append(f)
        
        foc_details = "\n".join([
            f"- **{code}** (Occurrences: {len(items)}):\n" + 
            "\n".join([f"  - {item['passage']}: {item['explanation']}" for item in items[:3]])
            for code, items in foc_grouped.items()
        ])
        
        prompt = f"""I am analyzing the Second-Order Code (Category): **"{soc}"**

This category consists of the following first-order codes and their meanings:

{foc_details}

Please provide your response in English. Maintain an academic tone that is professional yet accessible."""

    elif memo_type == 'Theoretical Memos':
        codes = context.get('codes', [])
        
        codes_info = "\n".join([
            f"- **{c['name']}** ({c['type']}): Found in {c.get('passageCount', 0)} documents\n" +
            "  Explanations: " + "; ".join(c.get('explanations', [])[:5])
            for c in codes
        ])
        
        code_names = [c['name'] for c in codes]
        
        prompt = f"""I am exploring the logical relationships between the following concepts:

{codes_info}

Concepts: {', '.join(code_names)}

Please provide your response in English. Maintain an academic tone that is professional yet accessible."""

    elif memo_type == 'Analytical Memos':
        question = context.get('question', '')
        
        prompt = f"""I have the following question:

"{question}"

Please provide your response in English. Maintain an academic tone that is professional yet accessible."""

    else:
        return jsonify({"error": "Invalid memo type"}), 400

    print(f"Calling AI with prompt: {prompt[:200]}...")
    result = call_kimi_api(prompt)
    if result:
        return jsonify({"result": result})
    else:
        return jsonify({"error": "AI analysis failed"}), 500

@app.route('/api/memo-question', methods=['POST'])
def memo_question():
    """Handle conversational Q&A about memo content."""
    data = request.json
    memo_type = data.get('type')
    question = data.get('question', '')
    memo_content = data.get('memoContent', '')
    memo_title = data.get('memoTitle', '')
    analyze_info = data.get('analyzeInfo')                 

    if not question:
        return jsonify({"error": "Question is required"}), 400

                                                                           

                                                           
    preamble = (
        "You are an expert qualitative-research assistant. "
        "The user is working inside a qualitative coding tool that organises "
        "interview / document data in the following hierarchy:\n"
        "  • First-Order Codes - low-level labels applied to specific passages of text.\n"
        "  • Second-Order Codes - higher-level categories that group First-Order Codes.\n"
        "  • Stages - each coded item belongs to a stage that represents a phase or "
        "temporal/logical step in the data (stages have a meaningful order).\n"
        "  • Theoretical Memos use 'links' (code1—code2) to explore relationships "
        "between two concepts; the link title is formatted as \"code1—code2\" and the "
        "system finds all documents where both codes co-occur.\n\n"
    )

                                     
    memo_ctx = f"## Current Memo\n- **Type**: {memo_type}\n"
    if memo_title:
        memo_ctx += f"- **Title**: {memo_title}\n"
    if memo_content:
        memo_ctx += f"- **Content written so far by the user**:\n{memo_content}\n"

                                                                         
    trace_section = ""

    if analyze_info:
        a_type = analyze_info.get('type', '')

        if a_type == 'first-order-trace':
            code = analyze_info.get('code', '')
            passages = analyze_info.get('passages', [])
            trace_section += (
                f"## Source Trace — First-Order Code: \"{code}\"\n"
                f"This code appears in {len(passages)} passage(s). "
                "Each entry shows the document name, the stage it belongs to, "
                "the original sentence, and the researcher's note.\n\n"
            )
            for i, p in enumerate(passages, 1):
                trace_section += (
                    f"{i}. **{p.get('passage', '')}**  "
                    f"[Stage: {p.get('stage', 'N/A')}]\n"
                    f"   - Sentence: \"{p.get('sentence', '')}\"\n"
                    f"   - Note: {p.get('explanation', '')}\n"
                )

        elif a_type == 'second-order-trace':
            soc = analyze_info.get('secondOrderCode', '')
            focs = analyze_info.get('firstOrderCodes', [])
            trace_section += (
                f"## Source Trace — Second-Order Code: \"{soc}\"\n"
                f"The following First-Order Codes are grouped under this category "
                f"({len(focs)} occurrences across documents).\n\n"
            )
            for i, f in enumerate(focs, 1):
                trace_section += (
                    f"{i}. **{f.get('code', '')}** — "
                    f"from *{f.get('passage', '')}*  "
                    f"[Stage: {f.get('stage', 'N/A')}]\n"
                    f"   - Note: {f.get('explanation', '')}\n"
                )

        elif a_type == 'theory-trace':
            title = analyze_info.get('title', '')
            results = analyze_info.get('results', [])
            trace_section += (
                f"## Source Trace — Theoretical Link: \"{title}\"\n"
                "This link represents a relationship between two concepts. "
                "Below are the documents where **both** concepts co-occur. "
                "Pay attention to the stage of each code — stages have a "
                "sequential order that reflects a temporal or logical progression "
                "(e.g. earlier stages happen before later stages).\n\n"
            )
            for i, r in enumerate(results, 1):
                pname = r.get('passageName', '')
                c1 = r.get('code1Data', {})
                c2 = r.get('code2Data', {})
                trace_section += (
                    f"### Document {i}: {pname}\n"
                    f"- **{c1.get('code', '')}**  [Stage: {c1.get('stage', 'N/A')}]\n"
                    f"  - Sentence: \"{c1.get('sentence', '')}\"\n"
                    f"  - Note: {c1.get('explanation', '')}\n"
                    f"- **{c2.get('code', '')}**  [Stage: {c2.get('stage', 'N/A')}]\n"
                    f"  - Sentence: \"{c2.get('sentence', '')}\"\n"
                    f"  - Note: {c2.get('explanation', '')}\n"
                )
                                                             
                s1 = c1.get('stage', '')
                s2 = c2.get('stage', '')
                if s1 and s2:
                    if s1 == s2:
                        trace_section += f"  *(Both codes appear in the same stage: {s1})*\n"
                    else:
                        trace_section += f"  *(Cross-stage: {c1.get('code','')} is in stage \"{s1}\", {c2.get('code','')} is in stage \"{s2}\")*\n"
                trace_section += "\n"

    prompt = (
        f"{preamble}"
        f"{memo_ctx}\n"
        f"{trace_section}\n"
        f"## User's Question\n{question}\n\n"
        "Answer the question according to the above context within the dataset.\n"
        "Please provide your response in English. "
        "Maintain an academic tone that is professional yet accessible."
    )

    print(f"Calling AI for memo question: {question[:100]}...")
    result = call_kimi_api(prompt)
    if result:
        return jsonify({"result": result})
    else:
        return jsonify({"error": "AI analysis failed"}), 500

                                                                            
FINAL_LINKAGE_FILE = 'final_linkage.json'

def _read_final_links():
    if not os.path.exists(FINAL_LINKAGE_FILE):
        return []
    try:
        with open(FINAL_LINKAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def _write_final_links(data):
    with open(FINAL_LINKAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/api/final-linkage', methods=['GET'])
def get_final_linkage():
    return jsonify(_read_final_links())

@app.route('/api/final-linkage', methods=['POST'])
def add_final_linkage():
    """Add one or more links. Body can be a single object or an array."""
    try:
        incoming = request.json
        links = _read_final_links()
        if isinstance(incoming, list):
            links.extend(incoming)
        else:
            links.append(incoming)
        _write_final_links(links)
        return jsonify({"status": "success", "count": len(links)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/final-linkage/all', methods=['DELETE'])
def delete_all_final_links():
    """Clear all final links."""
    try:
        _write_final_links([])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/final-linkage/<link_id>', methods=['DELETE'])
def delete_final_link(link_id):
    """Delete a single link by its id."""
    try:
        links = _read_final_links()
        links = [l for l in links if l.get('id') != link_id]
        _write_final_links(links)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/final-linkage/node', methods=['DELETE'])
def delete_final_node():
    """Delete all links where the given code+stage is source or target."""
    try:
        code = request.args.get('code', '')
        stage = request.args.get('stage', '')
        links = _read_final_links()
        links = [l for l in links if not (
            (l.get('sourceCode') == code and l.get('sourceStage') == stage) or
            (l.get('targetCode') == code and l.get('targetStage') == stage)
        )]
        _write_final_links(links)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/final-linkage/bulk', methods=['PUT'])
def replace_final_linkage():
    """Replace all links at once (used by export)."""
    try:
        data = request.json
        _write_final_links(data if isinstance(data, list) else [])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Memo API server starting on port 5002...")
    app.run(host='0.0.0.0', port=5002)