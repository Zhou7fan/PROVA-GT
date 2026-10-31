from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
import json
import csv
from threading import Lock
import chardet
from openai import OpenAI
from config import require_env

app = Flask(__name__)
CORS(app)
last_generated_csv = None

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

                
deepseek_client = OpenAI(
    api_key=require_env("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

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

def call_deepseek_api(prompt_text):                 
    print("Calling DeepSeek API with prompt:", prompt_text[-100:], "...")
    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[{
                "role": "user", 
                "content": prompt_text
            }],
            temperature=0,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"DeepSeek API Request failed: {e}")
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

def deduplicate_entries(entries):
    unique_entries = []
    seen = set()
    for entry in entries:
        if entry not in seen:
            seen.add(entry)
            unique_entries.append(entry)
    return unique_entries

def process_file(filepath, filename, chunk_size, custom_prompt):               
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
            response = call_deepseek_api(prompt)         
            if response:
                all_entries.extend(parse_response(response))
            else:
                                                    
                csv_path = export_to_csv()
                return {
                    "filename": filename,
                    "total_chunks": chunk_count,
                    "unique_entries": len(all_entries),
                    "error": "API call failed",
                    "csv_path": csv_path
                }

        unique_entries = deduplicate_entries(all_entries)
        for code, expl, sent, stage in unique_entries:
            code = code.replace('_', ' ')
            code = code.replace('*', '')
            if code not in code_library:
                code_library[code] = {'count': 0, 'passages': {}}
            if filename not in code_library[code]['passages']:
                code_library[code]['count'] += 1
                code_library[code]['passages'][filename] = (expl, sent, stage)
        
        return {
            "filename": filename,
            "total_chunks": chunk_count,
            "unique_entries": len(unique_entries)
        }
    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
                                     
        csv_path = export_to_csv()
        return {
            "filename": filename,
            "total_chunks": chunk_count,
            "unique_entries": len(all_entries) if 'all_entries' in locals() else 0,
            "error": str(e),
            "csv_path": csv_path
        }

@app.route('/upload', methods=['POST'])
def upload_files():
    global code_library, processing_status
    try:
        clear_upload_folder()
        code_library.clear()

        files = request.files.getlist('files')
        granularity_value = int(request.form.get('granularityValue', 1000))
        custom_prompt = request.form.get('prompt')
        
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
        for filename in file_order:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            result = process_file(filepath, filename, granularity_value, custom_prompt)        
            processed_files.append(result)
            with status_lock:
                processing_status['processed_files'] += 1
                processing_status['current_file'] = ''
                processing_status['current_chunk'] = 0
                processing_status['total_chunks'] = 0

        csv_path = export_to_csv()
        return jsonify({
            "processed_files": processed_files,
            "total_codes": len(code_library),
            "csv_path": csv_path
        }), 200
    except Exception as e:
        print(f"Processing error: {str(e)}")
        return jsonify({
            "error": f"Processing failed: {str(e)}",
            "processed_files": processed_files if 'processed_files' in locals() else []
        }), 500

def export_to_csv():
    print("Exporting code library to CSV...")
    try:
        public_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
        
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
            writer.writerow(['code', 'count', 'passage', 'explanation', 'sentence', 'stage'])
            for code, data in code_library.items():
                for passage, (expl, sent, stage) in data['passages'].items():
                    stage=stage.replace(']', ' ')  
                    stage=stage.replace('[', ' ')   
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

@app.route('/highlight-data')
def get_highlight_data():
    passage = request.args.get('passage')
    csv_path = request.args.get('csv')
    public_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
    file_path = os.path.join(public_folder, csv_path)
    
    highlight_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['passage'] == passage:
                    highlight_data.append({
                        'sentence': row['sentence'],
                        'code': row['code'],
                        'explanation': row['explanation'],
                        'stage': row['stage']
                    })
        return jsonify(highlight_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    global last_generated_csv
    try:
        file = request.files.get('csv_file')
        if not file or not file.filename.endswith('.csv'):
            return jsonify({"error": "Please upload a .csv file"}), 400
        
        public_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
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

if __name__ == '__main__':
    print("Starting Flask application on port 8000...")
    app.run(port=8000)