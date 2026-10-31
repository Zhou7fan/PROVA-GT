from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
import requests
import json
import csv
from threading import Lock
import chardet
from config import require_env

app = Flask(__name__)
CORS(app)
last_generated_csv = None

UPLOAD_FOLDER = './uploads'
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
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def call_deepseek_api(prompt_text, api_key):
    print("Calling API with prompt:", prompt_text[-100:], "...")
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        "messages": [{
            "role": "user",
            "content": prompt_text
        }],
        "temperature": 0,
        "max_tokens": 4096 ,                
        "stream": False,
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        print(f"API Error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def parse_response(response_text):
    entries = []
    for line in response_text.split('\n'):
        line = line.strip()
        if line.startswith('```') or not line:
            continue
        if line.count('#') == 3:                   
            parts = [part.strip() for part in line.split('#', 3)]
            if all(len(part) > 0 for part in parts):
                entries.append(tuple(parts))
                continue
        print(f"Invalid response line format: {line}")
    return entries


def deduplicate_entries(entries):
    unique_entries = []
    seen = set()
    for entry in entries:
        if entry not in seen:
            seen.add(entry)
            unique_entries.append(entry)
    return unique_entries

def process_file(filepath, filename, chunk_size, api_key):
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
            prompt = f"""##Context: I am conducting a research project, analyzing the life stories of social entrepreneurs, who are the founders or co-founders of social enterprises. Here is an interview transcript conducted by Steven Moe with the social entrepreneur.

            ##Objective: Please extract the keywords that are relevant to the following themes: 1) cognitive transformation of the social entrepreneur, such as how they went through sensemaking, integrative thinking, entrepreneurial epiphany; 2) triggers of the cognitive transformation, such as personal triggers and contextual triggers. Personal triggers include challenges faced in current business, burnout from previous job, reverse cultural shock, exposure to social problems. Contextual triggers include natural disaster such as earthquake, social movement in society such as global shaper, news report. 3) readiness of the social entrepreneurs, including mental preparedness and resource availability. Examples of mental preparedness include open to experience, desire to help, feeling guilty for not doing good and positive attitude towards entrepreneurship. Examples of resource availability include studying different fields of knowledge, exposure to international work environment, family business and multiple work experience in startups.

            ##Style: Please use the style of academic writing.

            ##Tone: Please use the tone of academic writing.

            ##Audience: The keywords will be further processed by other researchers, so please identify the keywords with the audience as the researcher in mind.

            ##Response: Please extract the keywords with corresponding original contents, e.g., sentences or paragraphs.The output format must lines with the following format:[keyword(all in lowercase letters)]#[explanation]#[most related sentence(no quotation marks)]#[Life Stage].((For example:education background#where alanna went to her college#I went to Harvard University.#adolescence))Life Stage has 3 kinds,Childhood,Adolescence,and Adult.Sentence must be the same as what is in the passage.If the generated response exceeds the character limit, automatically remove the least relevant entries to ensure all output datasets are formatted correctly. Do not include any explanations or additional notes before or after the output. The output text must be in English.Script:{chunk}"""
            response = call_deepseek_api(prompt, api_key)
            if response:
                print(response)
                all_entries.extend(parse_response(response))
            else:
                raise Exception(f"API call failed for chunk: {chunk[:50]}...")
        
        unique_entries = deduplicate_entries(all_entries)
        for code, expl, sent, stage in unique_entries:
            code = code.replace('_', ' ')
            code = code.replace('*', '')
            code = code.replace('-', '')
            if code not in code_library:
                code_library[code] = {'count': 0, 'passages': {}}
            if filename not in code_library[code]['passages']:
                code_library[code]['count'] += 1
                code_library[code]['passages'][filename] = (expl, sent, stage)
        
        print(f"Finished processing file: {filename}, found {len(unique_entries)} unique entries.")
        return {
            "filename": filename,
            "total_chunks": chunk_count,
            "unique_entries": len(unique_entries)
        }
    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
        raise e

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
                    writer.writerow([code.strip('[]'), data['count'], passage, expl, sent, stage])
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

@app.route('/upload', methods=['POST'])
def upload_files():
    global code_library, processing_status
    try:
        print("Starting file upload processing...")
        clear_upload_folder()
        code_library.clear()

        files = request.files.getlist('files')
        granularity_value = int(request.form.get('granularityValue', 1000))
        print(f"Received {len(files)} files with granularity: {granularity_value}")
        api_key = require_env("SILICONFLOW_API_KEY")

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
            result = process_file(filepath, filename, granularity_value, api_key)
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

if __name__ == '__main__':
    print("Starting Flask application on port 8000...")
    app.run(port=8000)