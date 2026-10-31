from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
import requests
import json
import csv
import time
from threading import Lock
import chardet
from flask import send_from_directory
from config import require_env


app = Flask(__name__)
CORS(app)
last_generated_csv = None

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '../frontend/uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

code_library = {}
processing_status = {
    'current_file': '',
    'current_chunk': 0,
    'total_chunks': 0,
    'processed_files': 0,
    'total_files': 0
}
status_lock = Lock()

def clear_upload_folder():
    print("Clearing upload folder...")
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    print("Upload folder cleared.")

def chunk_text(text, chunk_size):
                   
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

                                 
    for word in words:
                         
        if current_length + len(word) + (1 if current_chunk else 0) > chunk_size:
                                       
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
                              
            current_chunk.append(word)
            current_length += len(word) + (1 if current_chunk else 0)

                            
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def call_kimi_api(prompt_text, api_key, max_retries=3, retry_delay=60):
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "moonshot-v1-8k",
        "messages": [{
            "role": "user", 
            "content": f"""{prompt_text}"""
        }],
        "temperature": 0
    }
    for attempt in range(1, max_retries + 1):
        print(f"Calling API (attempt {attempt}/{max_retries}) with prompt:", prompt_text[:100], "...")
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            print(f"API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")
        
        if attempt < max_retries:
            print(f"Retry {attempt}/{max_retries} failed. Waiting {retry_delay}s before next attempt...")
            time.sleep(retry_delay)
        else:
            print(f"All {max_retries} attempts failed for this chunk.")
    return None

def parse_response(response_text):
    entries = []
    if not response_text or len(response_text) < 4:
        print("Invalid response text: response is empty or too short")
        return entries
    
    if response_text[0:2] == '[[':
        response_text = response_text[1:-1] 
    for line in response_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('```'):
            continue
        
        if line.count('#') == 3:
            parts = [part.strip('[]') for part in line.split('#', 3)]
            if all(len(part.strip()) > 0 for part in parts):
                entries.append(tuple(parts))
            else:
                print(f"Invalid line - empty parts: {line}")
        else:
            print(f"Invalid response line format (wrong number of #): {line}")
    
    print(f"Parsed {len(entries)} entries: {entries}")
    return entries

def extract_invalid_lines(response_text):
    """Extract lines that parse_response would reject (mirrors its validation logic)."""
    invalid_lines = []
    if not response_text or len(response_text) < 4:
        return invalid_lines

    text = response_text
    if text[0:2] == '[[':
        text = text[1:-1]

    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('```'):
            continue

        if line.count('#') == 3:
            parts = [part.strip('[]') for part in line.split('#', 3)]
            if not all(len(part.strip()) > 0 for part in parts):
                invalid_lines.append(line)
        else:
            invalid_lines.append(line)

    return invalid_lines


def attempt_format_correction(invalid_lines, api_key, use_alt_view, max_correction_retries=1):
    """Send invalid lines back to the API with a correction-only prompt."""
    if not invalid_lines:
        return []

    expected_format = (
        "[Dimension Name]#[Original Excerpt / Keyword]#[Full Original Text]"
        if use_alt_view
        else "[Dimension Name]#[Original Excerpt / Keyword]#[Full Original Text]#[Corresponding Stage]"
    )
    expected_hash_count = 2 if use_alt_view else 3

    correction_prompt = (
        f"The following data lines do not follow the required format. Please fix only their format and output them line by line, "
        f"without modifying the original text content and without adding any preface, closing remarks, or explanations.\n"
        f"Required format: {expected_format}\n"
        f"Each line must contain exactly {expected_hash_count} '#' characters as separators.\n\n"
        f"Lines to fix:\n" + "\n".join(invalid_lines)
    )

    print(f"[Auto-Correction] Attempting to correct {len(invalid_lines)} invalid line(s)...")

    correction_response = call_kimi_api(
        correction_prompt, api_key, max_retries=max_correction_retries, retry_delay=10
    )

    if correction_response:
        corrected_entries = parse_response(correction_response)
        print(
            f"[Auto-Correction] Recovered {len(corrected_entries)} entries "
            f"from {len(invalid_lines)} invalid line(s)."
        )
        return corrected_entries
    else:
        print(
            f"[Auto-Correction] Correction API call failed. "
            f"{len(invalid_lines)} line(s) could not be recovered."
        )
        return []


def parse_response_with_correction(response_text, api_key, use_alt_view):
    """Parse response, then auto-correct any invalid lines via a second API call."""
    valid_entries = parse_response(response_text)
    invalid_lines = extract_invalid_lines(response_text)

    if invalid_lines:
        corrected_entries = attempt_format_correction(invalid_lines, api_key, use_alt_view)
        valid_entries.extend(corrected_entries)

    return valid_entries

def deduplicate_entries(entries):
    unique_entries = []
    seen = set()
    for entry in entries:
        if entry not in seen:
            seen.add(entry)
            unique_entries.append(entry)
    return unique_entries

def _add_entries_to_library(entries, filename, use_alt_view):
    """Helper: add parsed entries to the global code_library."""
    global code_library
    unique_entries = deduplicate_entries(entries)
    for entry in unique_entries:
        if use_alt_view:
            code, expl, sent = entry
            code = code.replace('_', ' ')
            code = code.replace('*', '')
            if code not in code_library:
                code_library[code] = {'count': 0, 'passages': {}}
            if filename not in code_library[code]['passages']:
                code_library[code]['count'] += 1
                code_library[code]['passages'][filename] = (expl, sent)
        else:
            code, expl, sent, stage = entry
            code = code.replace('_', ' ')
            code = code.replace('*', '')
            if code not in code_library:
                code_library[code] = {'count': 0, 'passages': {}}
            if filename not in code_library[code]['passages']:
                code_library[code]['count'] += 1
                code_library[code]['passages'][filename] = (expl, sent, stage)
    return unique_entries


def process_file(filepath, filename, chunk_size, api_key, custom_prompt, use_alt_view):
    global code_library, processing_status
    print(f"Processing file: {filename}")
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']
        with open(filepath, 'r', encoding=encoding) as f:
            text = f.read()

        chunks = chunk_text(text, chunk_size)
        combined_chunks = [chunks[i] + chunks[i+1] for i in range(len(chunks)-1)]
        chunk_count = len(combined_chunks)

        with status_lock:
            processing_status['total_chunks'] = chunk_count
            processing_status['current_file'] = filename
            processing_status['current_chunk'] = 0

        all_entries = []
        for index, chunk in enumerate(combined_chunks, 1):
            with status_lock:
                processing_status['current_chunk'] = index
            print(f"Processing chunk {index}/{chunk_count} of {filename}")
            prompt = custom_prompt.replace('{chunk}', chunk)
            response = call_kimi_api(prompt, api_key)
            if response:
                all_entries.extend(parse_response_with_correction(response, api_key, use_alt_view))
            else:
                                                                               
                print(f"=== CHUNK {index}/{chunk_count} FAILED after all retries ===")
                if all_entries:
                    _add_entries_to_library(all_entries, filename, use_alt_view)
                    print(f"Saved {len(all_entries)} partial entries from {filename} to code_library.")
                raise Exception(
                    f"API call failed after 3 retries for chunk {index}/{chunk_count} of {filename}"
                )

        unique_entries = _add_entries_to_library(all_entries, filename, use_alt_view)
        
        return {
            "filename": filename,
            "total_chunks": chunk_count,
            "unique_entries": len(unique_entries)
        }
    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
        raise e
@app.route('/upload', methods=['POST'])
def upload_files():
    global code_library, processing_status
    try:
        clear_upload_folder()
        code_library.clear()

        files = request.files.getlist('files')
        granularity_value = int(request.form.get('granularityValue', 1000))
        custom_prompt = request.form.get('prompt')
        use_alt_view = request.form.get('useAltView') == 'true'
        api_key = require_env("MOONSHOT_API_KEY")

        file_order = []
        for file in files:
            if file.filename.endswith('.txt'):
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                file_order.append(file.filename)

        with status_lock:
            processing_status['total_files'] = len(file_order)
            processing_status['processed_files'] = 0
            processing_status['current_file'] = ''
            processing_status['current_chunk'] = 0
            processing_status['total_chunks'] = 0

        processed_files = []
        failed_file = None
        for filename in file_order:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                result = process_file(filepath, filename, granularity_value, api_key, custom_prompt, use_alt_view)
                processed_files.append(result)
                with status_lock:
                    processing_status['processed_files'] += 1
                    processing_status['current_file'] = ''
                    processing_status['current_chunk'] = 0
                    processing_status['total_chunks'] = 0
            except Exception as file_err:
                failed_file = filename
                print(f"\n{'='*60}")
                print(f"FATAL: File '{filename}' failed after all retries.")
                print(f"{'='*60}")
                break                                 

                                                                         
        if code_library:
            csv_path = export_to_csv(use_alt_view)
            if failed_file:
                print(f"\n{'='*60}")
                print(f"[PARTIAL SAVE] CSV with processed data saved as: {csv_path}")
                print(f"{'='*60}\n")
                return jsonify({
                    "error": f"Processing stopped at file '{failed_file}' after 3 retries. Partial CSV saved: {csv_path}",
                    "processed_files": processed_files,
                    "total_codes": len(code_library),
                    "csv_path": csv_path
                }), 500
            return jsonify({
                "processed_files": processed_files,
                "total_codes": len(code_library),
                "csv_path": csv_path
            }), 200
        else:
            if failed_file:
                return jsonify({
                    "error": f"Processing failed at '{failed_file}' with no data collected.",
                    "processed_files": []
                }), 500
            return jsonify({
                "processed_files": processed_files,
                "total_codes": 0,
                "csv_path": None
            }), 200
    except Exception as e:
                                                           
        if code_library:
            try:
                csv_path = export_to_csv(use_alt_view if 'use_alt_view' in locals() else False)
                print(f"\n{'='*60}")
                print(f"[EMERGENCY SAVE] CSV saved as: {csv_path}")
                print(f"{'='*60}\n")
            except Exception:
                csv_path = None
        print(f"Processing error: {str(e)}")
        return jsonify({
            "error": f"Processing failed: {str(e)}",
            "processed_files": processed_files if 'processed_files' in locals() else []
        }), 500
def export_to_csv(use_alt_view):
    print("Exporting code library to CSV...")
    try:
        public_folder = os.environ.get('PUBLIC_FOLDER', '../frontend/public')
        
        if not os.path.exists(public_folder):
            os.makedirs(public_folder)
        
        base_filename = 'code_library.csv'
        counter = 1
        while os.path.exists(os.path.join(public_folder, base_filename)):
            base_filename = f'code_library_{counter}.csv'
            counter += 1
        
        file_path = os.path.join(public_folder, base_filename)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if use_alt_view:
                writer.writerow(['code', 'count', 'passage', 'explanation', 'sentence'])
                for code, data in code_library.items():
                    for passage, (expl, sent) in data['passages'].items():
                        writer.writerow([code.strip('[]'), data['count'], passage, expl, sent.strip('"')])
            else:
                writer.writerow(['code', 'count', 'passage', 'explanation', 'sentence', 'stage'])
                for code, data in code_library.items():
                    for passage, (expl, sent, stage) in data['passages'].items():
                        stage = stage.replace(']', ' ').replace('[', ' ')
                        writer.writerow([code.strip('[]'), data['count'], passage, expl, sent.strip('"'), stage.strip('.')])
        print(f"Code library exported to {file_path}.")
        global last_generated_csv
        last_generated_csv = base_filename
        return base_filename
    except Exception as e:
        print(f"CSV export failed: {str(e)}")
        raise e
@app.route('/progress')
def get_progress():
    with status_lock:
        return jsonify(processing_status), 200
    
@app.route('/latest-csv')
def get_latest_csv():
    return jsonify({"filename": last_generated_csv}), 200


@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    global last_generated_csv
    try:
        file = request.files.get('csv_file')
        if not file or not file.filename.endswith('.csv'):
            return jsonify({"error": "Please upload a .csv file"}), 400
        
        public_folder = os.environ.get('PUBLIC_FOLDER', '../frontend/public')
        if not os.path.exists(public_folder):
            os.makedirs(public_folder)
        
        base_filename = file.filename
        counter = 1
        while os.path.exists(os.path.join(public_folder, base_filename)):
            name, ext = os.path.splitext(file.filename)
            base_filename = f'{name}_{counter}{ext}'
            counter += 1
        
        file_path = os.path.join(public_folder, base_filename)
        file.save(file_path)
        last_generated_csv = base_filename
        
        return jsonify({"filename": base_filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/public/<path:filename>')
def serve_public_file(filename):
    public_folder = os.environ.get('PUBLIC_FOLDER', '../frontend/public')
    return send_from_directory(public_folder, filename)
        

if __name__ == '__main__':
    print("Starting Flask application on port 8000...")
    app.run(host='0.0.0.0', port=8000)