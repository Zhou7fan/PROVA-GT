from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

app = Flask(__name__)
CORS(app)

                 
model = AutoModel.from_pretrained('nvidia/NV-Embed-v2', trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained('nvidia/NV-Embed-v2', trust_remote_code=True)

                
task_instruction = "Given a query, retrieve relevant keywords"
query_prefix = f"Instruct: {task_instruction}\nQuery: "
passage_prefix = ""              

def get_embeddings(texts, is_query=True):
    """Get embeddings with NV-Embed-v2."""
    if is_query:
                           
        prefixed_texts = [query_prefix + text for text in texts]
    else:
                  
        prefixed_texts = [passage_prefix + text for text in texts]
    
            
    embeddings = model.encode(
        prefixed_texts,
        max_length=32768,
        batch_size=32,
        return_numpy=True
    )
    
           
    return F.normalize(torch.tensor(embeddings), p=2, dim=1)

@app.route('/api/process', methods=['POST'])
def process_data():
    data = request.get_json()
    print(data)
    pocket_name = data.get('pocketName')
    updated_data = data.get('updatedData')

    if not pocket_name or not updated_data:
        return jsonify({'error': 'Missing required data'}), 400

            
    query_emb = get_embeddings([pocket_name], is_query=True)
    passage_embs = get_embeddings(updated_data, is_query=False)

                   
    similarities = (query_emb @ passage_embs.T) * 100
    similarities = similarities[0].tolist()         

                   
    result = {
        'pocketName': pocket_name,
        'similarities': {word: float(sim) for word, sim in zip(updated_data, similarities)}
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, port=5000)