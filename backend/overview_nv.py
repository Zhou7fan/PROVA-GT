from flask import Flask, request, jsonify
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

@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    data = request.json
    targets = data['targets']
    texts = data['texts']

                       
    target_emb = get_embeddings(targets, is_query=True)
                         
    text_emb = get_embeddings(texts, is_query=False)

                   
    similarities = (target_emb @ text_emb.T) * 100
    sim_matrix = similarities.numpy()

                               
    results = []
    for i in range(len(texts)):
        similarities = {
            targets[j]: float(sim_matrix[j][i])          
            for j in range(len(targets))
        }
        results.append(similarities)

    return jsonify({
        'results': results,
        'targets': targets,
        'texts': texts
    })

if __name__ == '__main__':
    app.run(port=5001)