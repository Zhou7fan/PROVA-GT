from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import require_env

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

                                       
client = OpenAI(
    api_key=require_env("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

EMBEDDING_MODEL = "text-embedding-v4"
EMBEDDING_DIM = 1024
BATCH_SIZE = 10                                         


def get_embeddings(texts):
    """Fetch text embeddings from the DashScope API, batching automatically."""
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        resp = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
            dimensions=EMBEDDING_DIM
        )
                          
        sorted_data = sorted(resp.data, key=lambda x: x.index)
        all_embeddings.extend([item.embedding for item in sorted_data])
    return np.array(all_embeddings)


@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    data = request.json
    targets = data['targets']
    texts = data['texts']

            
    all_texts = targets + texts
    vectors = get_embeddings(all_texts)

          
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

                                       
        print(f"\n[Batch] Text: '{texts[i][:30]}...'")
        sorted_sims = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:3]
        for target, similarity in sorted_sims:
            print(f"  -> Target '{target[:20]}': {similarity:.4f}")
    print("-" * 40)

    return jsonify({
        'results': results,
        'targets': targets,
        'texts': texts
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
