from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import umap
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


                     
@app.route('/api/process', methods=['POST'])
def process_data():
    data = request.get_json()
    pocket_name = data.get('pocketName')
    updated_data = data.get('updatedData')

    if not pocket_name or updated_data is None:
        return jsonify({'error': 'Missing data'}), 400

    if not updated_data:
                                         
        return jsonify({
            'pocketName': pocket_name,
            'similarities': {}
        })

             
    all_texts = [pocket_name] + updated_data
    vectors = get_embeddings(all_texts)

             
    similarities = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    ).flatten()

    sim_dict = dict(zip(updated_data, similarities.tolist()))
    
                            
    print(f"\n[{pocket_name}] Similarity analysis results:")
                      
    sorted_sims = sorted(sim_dict.items(), key=lambda x: x[1], reverse=True)[:20]
    for text, score in sorted_sims:
        print(f"  -> {text[:20]:<20} : {score:.4f}")
    if len(sim_dict) > 20:
        print(f"  ... ({len(sim_dict)} total)")
    print("-" * 40)
                                         

    return jsonify({
        'pocketName': pocket_name,
        'similarities': sim_dict
    })


@app.route('/api/umap', methods=['POST'])
def umap_endpoint():
    """Receive a list of first-order codes and return UMAP 2D coordinates."""
    data = request.get_json()
    codes = data.get('codes', [])

    if not codes or len(codes) == 0:
        return jsonify({'error': 'No codes provided'}), 400

                    
    if len(codes) == 1:
        return jsonify({'points': [{'name': codes[0], 'x': 0.5, 'y': 0.5}]})

            
    try:
        vectors = get_embeddings(codes)
    except Exception as e:
        return jsonify({'error': f'Embedding failed: {str(e)}'}), 500

            
    try:
        if len(codes) == 2:
                                                    
            reducer = PCA(n_components=2)
            coords_2d = reducer.fit_transform(vectors)
        else:
                                               
            pca_dim = min(50, len(codes) - 1, vectors.shape[1])
            pca = PCA(n_components=pca_dim)
            vectors_reduced = pca.fit_transform(vectors)

            n_neighbors = min(15, len(codes) - 1)
            reducer = umap.UMAP(
                n_components=2,
                n_neighbors=n_neighbors,
                metric='cosine',                    
                random_state=42
            )
            coords_2d = reducer.fit_transform(vectors_reduced)
    except Exception as e:
        return jsonify({'error': f'UMAP failed: {str(e)}'}), 500

                 
    eps = 1e-8
    mins = coords_2d.min(axis=0)
    maxs = coords_2d.max(axis=0)
    ranges = maxs - mins
    ranges[ranges < eps] = 1.0        
    normed = (coords_2d - mins) / ranges

    points = []
    for i, name in enumerate(codes):
        points.append({
            'name': name,
            'x': round(float(normed[i, 0]), 6),
            'y': round(float(normed[i, 1]), 6)
        })

    print(f"\n[UMAP] Processed {len(codes)} codes -> 2D")
    for p in points[:10]:
        print(f"  -> {p['name'][:25]:<25} : ({p['x']:.4f}, {p['y']:.4f})")
    if len(points) > 10:
        print(f"  ... (total {len(points)})")
    print("-" * 40)

    return jsonify({'points': points})


if __name__ == '__main__':
                 
    app.run(host='0.0.0.0', port=5003, debug=False)
