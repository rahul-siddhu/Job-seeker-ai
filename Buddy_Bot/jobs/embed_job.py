from ast import literal_eval
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer  # For embeddings
import pandas as pd
import numpy as np

app = Flask(__name__)

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200", http_auth=("elastic", "search"))

INDEX_NAME = "jobs"
EMBEDDING_DIM = 384  # Adjust based on the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Efficient model for embeddings


# Create index with mappings for embeddings
def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        mapping = {
            "settings": {
                "analysis": {
                    "normalizer": {
                        "lowercase_normalizer": {
                            "type": "custom",
                            "char_filter": [],
                            "filter": ["lowercase"]
                        }
                    },
                    "analyzer": {
                        "custom_text_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding"]  # Handles case insensitivity and special characters
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "standard"},
                    "skills": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "location": {"type": "keyword", "normalizer": "lowercase_normalizer"},
                    "embedding": {"type": "dense_vector", "dims": EMBEDDING_DIM, "index": False},
                    "designation": {"type": "text", "analyzer": "custom_text_analyzer"},
                    "industry": {"type": "text", "analyzer": "custom_text_analyzer"},
                    "qualification": {"type": "text", "analyzer": "standard"},
                    "workMode": {"type": "text", "analyzer": "custom_text_analyzer"},
                    "jobType": {"type": "text", "analyzer": "custom_text_analyzer"}
                }
            }
        }

        es.indices.create(index=INDEX_NAME, body=mapping)

create_index()


@app.route("/")
def home():
    return jsonify({"message": "Elasticsearch Flask API with embeddings is running!"})


@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        # Define batch size
        BATCH_SIZE = 100
        total_records = 0

        # Read the CSV file in chunks
        for chunk in pd.read_csv(file, chunksize=BATCH_SIZE):
            # Ensure necessary columns are present
            required_columns = {"id", "name", "description", "skills", "location", "designation", "industry", "qualification", "workMode", "jobType"}
            if not required_columns.issubset(chunk.columns):
                return jsonify({"error": f"CSV must contain the following columns: {', '.join(required_columns)}"}), 400

            # Process and index each row in the current chunk
            for _, row in chunk.iterrows():
                # Normalize and handle empty fields
                location = row["location"].lower() if pd.notna(row["location"]) and row["location"] != "" else None
                designation = row["designation"].lower() if pd.notna(row["designation"]) and row["designation"] != "" else None
                industry = row["industry"].lower() if pd.notna(row["industry"]) and row["industry"] != "" else None
                qualification = row["qualification"] if pd.notna(row["qualification"]) and row["qualification"] != "" else None
                workMode = row["workMode"].lower() if pd.notna(row["workMode"]) and row["workMode"] != "" else None
                jobType = row["jobType"].lower() if pd.notna(row["jobType"]) and row["jobType"] != "" else None

                # Parse skills, handle improperly formatted lists
                try:
                    skills = literal_eval(row["skills"]) if isinstance(row["skills"], str) and row["skills"].startswith("[") else row["skills"].split(",")
                except (ValueError, SyntaxError):
                    skills = []  # Default to empty list if skills parsing fails

                # Prepare document for Elasticsearch
                document = {
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"],
                    "location": location,
                    "skills": skills,
                    "designation": designation,
                    "industry": industry,
                    "qualification": qualification,
                    "workMode": workMode,
                    "jobType": jobType,
                    "embedding": model.encode(f"{row['description']} {' '.join(skills)} {location} {designation} {industry}").tolist()
                }

                # Index document
                es.index(index=INDEX_NAME, document=document)

            # Update total records processed
            total_records += len(chunk)

        return jsonify({"message": f"Uploaded {total_records} records to Elasticsearch"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/jobs/search", methods=["POST"])
def search_jobs():
    data = request.json
    query_text = data.get("query", "").strip()  # Handle empty or whitespace-only query
    location = data.get("location", "").lower()  # Normalize location to lowercase
    designation = data.get("designation", "").lower()
    industry = data.get("industry", "").lower()
    qualification = data.get("qualification", "").strip()
    work_mode = data.get("workMode", "").lower()
    job_type = data.get("jobType", "").lower()
    size = data.get("size", 30)  # Default size to 20 if not provided

    try:
        # Construct the search query
        must_clauses = []
        filter_clauses = []

        # Add embedding-based similarity search if query_text is provided
        if query_text:
            query_embedding = model.encode(query_text).tolist()
            knn_query = {
                "field": "embedding",
                "query_vector": query_embedding,
                "num_candidates": size
            }
            must_clauses.append({"knn": knn_query})
        size=1000
        # Add filters for exact matches on location and other fields
        if location:
            filter_clauses.append({"term": {"location": location}})
        if designation:
            filter_clauses.append({"match": {"designation": designation}})
        if industry:
            filter_clauses.append({"match": {"industry": industry}})
        if qualification:
            filter_clauses.append({"match": {"qualification": qualification}})
        if work_mode:
            filter_clauses.append({"match": {"workMode": work_mode}})
        if job_type:
            filter_clauses.append({"match": {"jobType": job_type}})

        # Ensure at least one condition is present
        if not (must_clauses or filter_clauses):
            return jsonify({"error": "At least one search parameter must be provided"}), 400

        # Combine must and filter clauses into the final query
        query = {"bool": {}}
        if must_clauses:
            query["bool"]["must"] = must_clauses
        if filter_clauses:
            query["bool"]["filter"] = filter_clauses

        # Debug: Log the query for troubleshooting
        print(f"Running query: {query}")

        # if (not must_clauses) and location:
        #     size = 10000

        # Execute the search
        response = es.search(index=INDEX_NAME, query=query, size=size)
        results = [
            {k: v for k, v in hit["_source"].items() if k != "embedding"}
            for hit in response["hits"]["hits"]
        ]

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/jobs", methods=["POST"])
def create_job():
    data = request.json

    # Extract required fields
    description = data.get("description", "")
    skills = data.get("skills", [])
    location = data.get("location", "")
    designation = data.get("designation", "")
    industry = data.get("industry", "")
    qualification = data.get("qualification", "")
    work_mode = data.get("workMode", "")
    job_type = data.get("jobType", "")

    # Sanitize and normalize fields
    location = location.lower() if location and location != "NaN" and pd.notna(location) else None
    designation = designation.lower() if designation else None
    industry = industry.lower() if industry else None
    work_mode = work_mode.lower() if work_mode else None
    job_type = job_type.lower() if job_type else None
    qualification = qualification.strip() if qualification else None

    # Generate embedding for the job
    embedding_input = f"{description} {' '.join(skills)} {location or ''} {designation or ''} {industry or ''} {qualification or ''} {work_mode or ''} {job_type or ''}"
    embedding = model.encode(embedding_input).tolist()

    # Add embedding and normalized fields to the document
    data["embedding"] = embedding
    data["location"] = location
    data["designation"] = designation
    data["industry"] = industry
    data["qualification"] = qualification
    data["workMode"] = work_mode
    data["jobType"] = job_type

    # Index the document in Elasticsearch
    response = es.index(index=INDEX_NAME, document=data)
    return jsonify(response.body)  # Use .body to convert to a dict



@app.route("/delete_index", methods=["DELETE"])
def delete_index():
    """
    Deletes the specified index from Elasticsearch.
    """
    index_name = request.args.get("index", INDEX_NAME)  # Use default index if not specified
    try:
        # Check if the index exists before attempting to delete
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            return jsonify({"message": f"Index '{index_name}' deleted successfully"}), 200
        else:
            return jsonify({"error": f"Index '{index_name}' does not exist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
