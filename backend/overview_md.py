from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

                 
model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

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

    return jsonify({
        'results': results,
        'targets': targets,
        'texts': texts
    })

if __name__ == '__main__':
    app.run(port=5001)