from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

              
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

                     
@app.route('/api/process', methods=['POST'])
def process_data():
    data = request.get_json()
    pocket_name = data.get('pocketName')
    updated_data = data.get('updatedData')

    if not pocket_name or not updated_data:
        return jsonify({'error': 'Missing data'}), 400

             
    all_texts = [pocket_name] + updated_data
    vectors = get_vector(all_texts)
    pocket_vector = vectors[0]
    
             
    similarities = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    ).flatten()

    return jsonify({
        'pocketName': pocket_name,
        'similarities': dict(zip(updated_data, similarities.tolist()))
    })

if __name__ == '__main__':
                 
    app.run(host='0.0.0.0', port=5002,debug=False)