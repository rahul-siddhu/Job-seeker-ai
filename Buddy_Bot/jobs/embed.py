from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer  # Using Sentence Transformers for embeddings

app = Flask(__name__)

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200", http_auth=("elastic", "search"))

INDEX_NAME = "products"
EMBEDDING_DIM = 384  # Change based on your embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Use a small, efficient model

# Create index with mappings for embeddings
def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        mapping = {
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "description": {"type": "text"},
                    "embedding": {"type": "dense_vector", "dims": EMBEDDING_DIM}
                }
            }
        }
        es.indices.create(index=INDEX_NAME, body=mapping)

create_index()


@app.route("/")
def home():
    return jsonify({"message": "Elasticsearch Flask API with embeddings is running!"})


# Create a new document with embeddings
@app.route("/products", methods=["POST"])
def create_product():
    data = request.json
    # Generate embedding for the product description
    description = data.get("description", "")
    embedding = model.encode(description).tolist()
    data["embedding"] = embedding
    response = es.index(index=INDEX_NAME, document=data)
    return jsonify(response.body)  # Use .body to convert to a dict


# Search documents using semantic similarity
@app.route("/products/search", methods=["POST"])
def search_products():
    query_text = request.json.get("query", "")
    query_embedding = model.encode(query_text).tolist()

    # Use cosine similarity to find the most similar documents
    response = es.search(index=INDEX_NAME, knn={
        "field": "embedding",
        "query_vector": query_embedding,
        "k": 10,  # Number of top results to retrieve
        "num_candidates": 100  # Number of candidates to consider
    })
    return jsonify([hit["_source"] for hit in response.body["hits"]["hits"]])  # Simplify output


if __name__ == "__main__":
    app.run(debug=True)
