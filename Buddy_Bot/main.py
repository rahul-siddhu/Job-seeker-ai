from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

app = Flask(__name__)

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200", http_auth=("elastic", "search"))

INDEX_NAME = "products"

@app.route("/")
def home():
    return jsonify({"message": "Elasticsearch Flask API is running!"})


# Create a new document
@app.route("/products", methods=["POST"])
def create_product():
    data = request.json
    response = es.index(index=INDEX_NAME, document=data)
    return jsonify(response.body)  # Use .body to convert to a dict


# Retrieve a document by ID
@app.route("/products/<id>", methods=["GET"])
def get_product(id):
    try:
        response = es.get(index=INDEX_NAME, id=id)
        return jsonify(response.body["_source"])  # Access _source for the document
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# Update a document by ID
@app.route("/products/<id>", methods=["PUT"])
def update_product(id):
    data = request.json
    response = es.update(index=INDEX_NAME, id=id, body={"doc": data})
    return jsonify(response.body)


# Delete a document by ID
@app.route("/products/<id>", methods=["DELETE"])
def delete_product(id):
    try:
        response = es.delete(index=INDEX_NAME, id=id)
        return jsonify(response.body)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# Search documents
@app.route("/products/search", methods=["POST"])
def search_products():
    query = request.json.get("query", {"match_all": {}})
    response = es.search(index=INDEX_NAME, query=query)
    return jsonify([hit["_source"] for hit in response.body["hits"]["hits"]])  # Simplify output


if __name__ == "__main__":
    app.run(debug=True)
