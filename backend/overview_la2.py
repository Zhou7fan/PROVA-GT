from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModel ,AutoModelForCausalLM 
import torch
import numpy as np
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
import requests
from config import require_env

app = Flask(__name__)
CORS(app)



                                    
tokenizer = AutoTokenizer.from_pretrained("Lajavaness/bilingual-embedding-large")
model = AutoModel.from_pretrained("Lajavaness/bilingual-embedding-large", trust_remote_code=True)

def last_token_pool(last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]

def get_vector(texts):
    max_length = 512
    batch_dict = tokenizer(texts, max_length=max_length, padding=True, truncation=True, return_tensors="pt")
    outputs = model(**batch_dict)
    embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
    return embeddings.detach().numpy()

@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    data = request.json
    targets = data['targets']
    texts = data['texts']

            
    all_texts = targets + texts
    vectors = get_vector(all_texts)
    
          
    target_vectors = vectors[:len(targets)]
    text_vectors = vectors[len(targets):]

             
    sim_matrix = cosine_similarity(text_vectors, target_vectors)
    
                               
    results = []
    for i in range(len(texts)):
        similarities = {
            targets[j]: float(sim_matrix[i][j]) 
            for j in range(len(targets))
        }
        results.append(similarities)

                               
        print(f"Text: {texts[i]}")
        for target, similarity in similarities.items():
            print(f"  Target: {target}, Similarity: {similarity:.4f}")

    
    return jsonify({
        'results': results,
        'targets': targets,
        'texts': texts
    })



def call_kimi_api(prompt_text, api_key):
    """Call the Kimi API to process the prompt."""
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "moonshot-v1-8k",
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0
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

def process_with_llm(codechunk, targets, include_explanation, is_strict_mode, api_key):
    """
    Use LLM to classify each first-order code in codechunk into second-order codes using Grounded Theory's focused coding approach.
    Returns a list of second-order codes (or 'null' if no match is found).
    """
                                              
    codes_only = [item['text'] for item in codechunk]

                                                               
    second_order_codes = [target['code'] for target in targets]
    print(second_order_codes)

    second_order_codes_exp = [target['explanation'] for target in targets]
    print(second_order_codes_exp)

    second_order_codes_full = [
        f"{second_order_codes[i]} (Explanation: {second_order_codes_exp[i]})"
        for i in range(len(second_order_codes))
    ]

                                                                    
    prompt = (
        "You are an expert in qualitative research, specifically in Grounded Theory for focused coding. "
        "I am analyzing user experiences to categorize first-order codes (low-level codes derived from data) into predefined second-order codes (higher-level thematic categories). "
        f"The second-order codes are: {', '.join(second_order_codes_full)}.\n"
        f"I have a list of first-order codes to classify: {', '.join(codes_only)}.\n\n"
        "Your task is to map each first-order code to one of the second-order codes or classify it as 'null' if it does not fit any category. "
        "Classification should align with Grounded Theory's focused coding principles, focusing on conceptual alignment rather than surface-level semantic similarity.\n"
        "Follow these criteria for classification:\n"
        "1. **Thematic Consistency**: The first-order code must align with the core theme of the second-order code. For example, a second-order code like 'Trust erosion' should only include codes indicating a decline in trust (e.g., 'loss of trust due to ads'), not codes about increasing trust (e.g., 'trust formation').\n"
        "2. **Contextual Fit**: Consider the underlying meaning of the first-order code to ensure it fits the second-order code's role in the data's dynamics.\n"
        "3. **Directional Alignment**: Ensure the direction of the concept matches. For example, codes about increasing engagement should not be placed under 'Decreased engagement', as the latter describes a negative shift.\n"
        "4. **Null Assignment**: If a first-order code does not conceptually align with any second-order code (e.g., it describes an unrelated or opposing concept), classify it as 'null'.\n"
        f"Return your answer as a single string with results separated by commas, where each result is either a second-order code from ({', '.join(second_order_codes)}) or 'null'. "
        "Do not include any explanations, extra text, or formatting beyond the comma-separated list.\n"
        "For example, if second-order codes are 'sensemaking' (includes 'learning about protecting the environment', 'realizing the importance of food safety') "
        "and 'community' (includes 'social work', 'social assistance'), "
        "and the first-order codes are 'social security, career transition, finding dreams', the response should be 'community, null, sensemaking'.\n\n"
    )

                                                              
    for target in targets:
        if target.get('isCustom', False):
            continue                                                 
        examples = ', '.join([f"'{fc}'" for fc in target['examples']])
        explanation = target['explanation']
        if include_explanation and explanation:
            prompt += f"- '{target['code']} (Explanation: {explanation})': includes {examples}.\n"
        else:
            prompt += f"- '{target['code']}': includes {examples}.\n"

                                     
    prompt += "Match based on strict conceptual alignment." if is_strict_mode else "Match based on broader conceptual alignment."

                      
    print(f"Prompt: {prompt}")
    response = call_kimi_api(prompt, api_key)

                              
    if response:
        print(f"Raw LLM response: '{response}'")                                      
        items = [item.strip().strip('"') for item in response.split(',')]
        if len(items) == len(codechunk):
            valid_result = [
                item if (item == 'null' or item in second_order_codes) else 'null'
                for item in items
            ]
            print(f"Processed result: {valid_result}")
            return valid_result
        else:
            print(f"Invalid response length: Expected {len(codechunk)} items, got {len(items)}")
            return ['null'] * len(codechunk)
    else:
        print("LLM API call failed.")
        return ['null'] * len(codechunk)
@app.route('/api/llm-process', methods=['POST'])
def llm_process():
    data = request.json
    codechunk = data['texts']
    targets = data['targets']
    include_explanation = data['options']['includeExplanation']
    is_strict_mode = data['options']['strictMode']
    api_key = require_env("MOONSHOT_API_KEY")

    secondordercodes = process_with_llm(codechunk, targets, include_explanation, is_strict_mode, api_key)

    return jsonify({
        'results': secondordercodes
    })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)