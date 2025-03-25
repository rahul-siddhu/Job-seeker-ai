from ast import literal_eval
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer  # For embeddings
import pandas as pd
import numpy as np
import math

app = Flask(__name__)

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200", http_auth=("elastic", "search"))

INDEX_NAME = "jobs"
EMBEDDING_DIM = 384  # Adjust based on the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Efficient model for embeddings

print(2)
# Create index with mappings for embeddings
# if es.indices.exists(index=INDEX_NAME):
#     es.indices.delete(index=INDEX_NAME, ignore=[400, 404])

def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        # print(99999999999999999999999999)
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
                            "filter": ["lowercase", "asciifolding"]
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
                    "designation": {"type": "text", "analyzer": "custom_text_analyzer"},
                    "industry": {"type": "text", "analyzer": "custom_text_analyzer"},
                    "qualification": {"type": "text", "analyzer": "standard"},
                    "workMode": {"type": "text", "analyzer": "custom_text_analyzer"},
                    "jobType": {"type": "text", "analyzer": "custom_text_analyzer"},
                    
                    # Additional fields
                    "company_id": {"type": "keyword"},
                    "designation_id": {"type": "keyword"},
                    "designationrefName": {"type": "text", "analyzer": "standard"},
                    "industry_id": {"type": "keyword"},
                    "industryrefName": {"type": "text", "analyzer": "standard"},
                    "jobFunction_id": {"type": "keyword"},
                    "jobFunctionName": {"type": "text", "analyzer": "standard"},
                    "jobFunctionrefName": {"type": "text", "analyzer": "standard"},
                    "portal": {"type": "text", "analyzer": "standard"},
                    "id_1": {"type": "keyword"},
                    "min_salary": {"type": "double"},
                    "min_salary_currency": {"type": "text", "analyzer": "standard"},
                    "max_salary": {"type": "double"},
                    "max_salary_currency": {"type": "text", "analyzer": "standard"},
                    "salary_frequency": {"type": "text", "analyzer": "standard"},
                    "salary_description": {"type": "text", "analyzer": "standard"},
                    "area": {"type": "text", "analyzer": "standard"},
                    "city": {"type": "text", "analyzer": "standard"},
                    "country": {"type": "text", "analyzer": "standard"},
                    "locationCoordinates_type": {"type": "text", "analyzer": "standard"},
                    "longitude": {"type": "text", "analyzer": "standard"},
                    "latitude": {"type": "text", "analyzer": "standard"},
                    "postedAt": {"type": "text", "analyzer": "standard"},
                    "applyUrls": {"type": "text", "analyzer": "standard"},
                    "applyUrls_external": {"type": "text", "analyzer": "standard"},
                    "experience_range_from": {"type": "double"},
                    "experience_range_to": {"type": "double"},
                    "postedBy_url": {"type": "text", "analyzer": "standard"},
                    "postedBy_name": {"type": "text", "analyzer": "standard"},
                    "applicants": {"type": "text", "analyzer": "standard"},
                    "about_html": {"type": "text", "analyzer": "standard"},
                    "jobDetail_text": {"type": "text", "analyzer": "standard"},
                    "jobDetail_html": {"type": "text", "analyzer": "standard"},
                    "qualification_html": {"type": "text", "analyzer": "standard"},
                    "tags_jobs1": {"type": "text", "analyzer": "standard"},
                    "tags_jobs2": {"type": "text", "analyzer": "standard"},
                    "tags_jobs3": {"type": "text", "analyzer": "standard"},
                    "isBlackListed": {"type": "text", "analyzer": "standard"},
                    "isExpired": {"type": "text", "analyzer": "standard"},
                    "createdAt": {"type": "text", "analyzer": "standard"},
                    "updatedAt": {"type": "text", "analyzer": "standard"},
                    "vectorText_designation": {"type": "text", "analyzer": "standard"},
                    "vectorText_skill": {"type": "text", "analyzer": "standard"},
                    "isBatched": {"type": "text", "analyzer": "standard"},
                    "tags": {"type": "text", "analyzer": "standard"},
                    "experience": {"type": "text", "analyzer": "standard"},
                    "embedding": {
                        "type": "dense_vector", 
                        "dims": EMBEDDING_DIM
                    }
                }
            }
        }
        es.indices.create(index=INDEX_NAME, body=mapping)

# if es.indices.exists(index=INDEX_NAME):
#     es.indices.delete(index=INDEX_NAME)
create_index()


print(2)
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
            # Before indexing, replace NaN values with None or appropriate default
            chunk = chunk.where(pd.notnull(chunk), None)
            required_columns = {
                "id", "name", "description", "skills", "location", "designation", "industry",
                "qualification", "workMode", "jobType", "company_id", "designation_id",
                "designationrefName", "industry_id", "industryrefName", "jobFunction_id",
                "jobFunctionName", "jobFunctionrefName", "portal", "id_1", "min_salary",
                "min_salary_currency", "max_salary", "max_salary_currency", "salary_frequency",
                "salary_description", "area", "city", "country", "locationCoordinates_type",
                "longitude", "latitude", "postedAt", "applyUrls", "applyUrls_external",
                "experience_range_from", "experience_range_to", "postedBy_url", "postedBy_name",
                "applicants", "about_html", "jobDetail_text", "jobDetail_html", "qualification_html",
                "tags_jobs1", "tags_jobs2", "tags_jobs3", "isBlackListed", "isExpired",
                "createdAt", "updatedAt", "vectorText_designation", "vectorText_skill", "isBatched",
                "tags", "experience"
            }
            if not required_columns.issubset(chunk.columns):
                return jsonify({"error": f"CSV must contain the following columns: {', '.join(required_columns)}"}), 400

            # Process and index each row in the current chunk
            for _, row in chunk.iterrows():
                # Normalize and handle empty fields
                location = row["location"].lower() if pd.notna(row["location"]) and isinstance(row["location"], str) else None
                designation = row["designation"].lower() if pd.notna(row["designation"]) and isinstance(row["designation"], str) else None
                industry = row["industry"].lower() if pd.notna(row["industry"]) and isinstance(row["industry"], str) else None
                qualification = row["qualification"] if pd.notna(row["qualification"]) else None
                workMode = row["workMode"].lower() if pd.notna(row["workMode"]) and isinstance(row["workMode"], str) else None
                jobType = row["jobType"].lower() if pd.notna(row["jobType"]) and isinstance(row["jobType"], str) else None
                designationrefName = row["designationrefName"].lower() if pd.notna(row["designationrefName"]) and isinstance(row["designationrefName"], str) else None
                industryrefName = row["industryrefName"].lower() if pd.notna(row["industryrefName"]) and isinstance(row["industryrefName"], str) else None
                jobFunctionName = row["jobFunctionName"].lower() if pd.notna(row["jobFunctionName"]) and isinstance(row["jobFunctionName"], str) else None
                jobFunctionrefName = row["jobFunctionrefName"].lower() if pd.notna(row["jobFunctionrefName"]) and isinstance(row["jobFunctionrefName"], str) else None
                portal = row["portal"].lower() if pd.notna(row["portal"]) and isinstance(row["portal"], str) else None
                min_salary_currency = row["min_salary_currency"].lower() if pd.notna(row["min_salary_currency"]) and isinstance(row["min_salary_currency"], str) else None
                max_salary_currency = row["max_salary_currency"].lower() if pd.notna(row["max_salary_currency"]) and isinstance(row["max_salary_currency"], str) else None
                salary_frequency = row["salary_frequency"].lower() if pd.notna(row["salary_frequency"]) and isinstance(row["salary_frequency"], str) else None
                salary_description = row["salary_description"].lower() if pd.notna(row["salary_description"]) and isinstance(row["salary_description"], str) else None
                area = row["area"].lower() if pd.notna(row["area"]) and isinstance(row["area"], str) else None
                city = row["city"].lower() if pd.notna(row["city"]) and isinstance(row["city"], str) else None
                country = row["country"].lower() if pd.notna(row["country"]) and isinstance(row["country"], str) else None
                locationCoordinates_type = row["locationCoordinates_type"].lower() if pd.notna(row["locationCoordinates_type"]) and isinstance(row["locationCoordinates_type"], str) else None
                longitude = row["longitude"] if pd.notna(row["longitude"]) else None
                latitude = row["latitude"] if pd.notna(row["latitude"]) else None
                postedAt = row["postedAt"].lower() if pd.notna(row["postedAt"]) and isinstance(row["postedAt"], str) else None
                applyUrls = row["applyUrls"].lower() if pd.notna(row["applyUrls"]) and isinstance(row["applyUrls"], str) else None
                applyUrls_external = row["applyUrls_external"].lower() if pd.notna(row["applyUrls_external"]) and isinstance(row["applyUrls_external"], str) else None
                postedBy_url = row["postedBy_url"].lower() if pd.notna(row["postedBy_url"]) and isinstance(row["postedBy_url"], str) else None
                postedBy_name = row["postedBy_name"].lower() if pd.notna(row["postedBy_name"]) and isinstance(row["postedBy_name"], str) else None
                applicants = row["applicants"].lower() if pd.notna(row["applicants"]) and isinstance(row["applicants"], str) else None
                about_html = row["about_html"].lower() if pd.notna(row["about_html"]) and isinstance(row["about_html"], str) else None
                jobDetail_text = row["jobDetail_text"].lower() if pd.notna(row["jobDetail_text"]) and isinstance(row["jobDetail_text"], str) else None
                jobDetail_html = row["jobDetail_html"].lower() if pd.notna(row["jobDetail_html"]) and isinstance(row["jobDetail_html"], str) else None
                qualification_html = row["qualification_html"].lower() if pd.notna(row["qualification_html"]) and isinstance(row["qualification_html"], str) else None
                tags_jobs1 = row["tags_jobs1"].lower() if pd.notna(row["tags_jobs1"]) and isinstance(row["tags_jobs1"], str) else None
                tags_jobs2 = row["tags_jobs2"].lower() if pd.notna(row["tags_jobs2"]) and isinstance(row["tags_jobs2"], str) else None
                tags_jobs3 = row["tags_jobs3"].lower() if pd.notna(row["tags_jobs3"]) and isinstance(row["tags_jobs3"], str) else None
                isBlackListed = row["isBlackListed"].lower() if pd.notna(row["isBlackListed"]) and isinstance(row["isBlackListed"], str) else None
                isExpired = row["isExpired"].lower() if pd.notna(row["isExpired"]) and isinstance(row["isExpired"], str) else None
                createdAt = row["createdAt"].lower() if pd.notna(row["createdAt"]) and isinstance(row["createdAt"], str) else None
                updatedAt = row["updatedAt"].lower() if pd.notna(row["updatedAt"]) and isinstance(row["updatedAt"], str) else None
                vectorText_designation = row["vectorText_designation"].lower() if pd.notna(row["vectorText_designation"]) and isinstance(row["vectorText_designation"], str) else None
                vectorText_skill = row["vectorText_skill"].lower() if pd.notna(row["vectorText_skill"]) and isinstance(row["vectorText_skill"], str) else None
                isBatched = row["isBatched"].lower() if pd.notna(row["isBatched"]) and isinstance(row["isBatched"], str) else None


                # tags = row["tags"].split(",") if pd.notna(row["tags"]) else []
                # experience = row["experience"].split(",") if pd.notna(row["experience"]) else []

                #skills
                try:
                    skills = literal_eval(row["skills"]) if isinstance(row["skills"], str) and row["skills"].startswith("[") else row["skills"].split(",")
                except (ValueError, SyntaxError):
                    skills = []    
                #tags
                try:
                    tags = literal_eval(row["tags"]) if isinstance(row["tags"], str) and row["tags"].startswith("[") else row["tags"].split(",")
                except (ValueError, SyntaxError):
                    tags = []
                #experience
                try:
                    experience = literal_eval(row["experience"]) if isinstance(row["experience"], str) and row["experience"].startswith("[") else row["experience"].split(",")
                except (ValueError, SyntaxError):
                    experience = []
                
                # Parse numeric and array fields
                # Robust handling of numeric fields
                min_salary = float(row["min_salary"]) if pd.notna(row["min_salary"]) and row["min_salary"] != '' and row["min_salary"] != 'NaN' else None
                max_salary = float(row["max_salary"]) if pd.notna(row["max_salary"]) and row["max_salary"] != '' and row["max_salary"] != 'NaN' else None
                
                # Experience range parsing
                experience_range_from = float(row["experience_range_from"]) if pd.notna(row["experience_range_from"]) and row["experience_range_from"] != '' and row["experience_range_from"] != 'NaN' else None
                experience_range_to = float(row["experience_range_to"]) if pd.notna(row["experience_range_to"]) and row["experience_range_to"] != '' and row["experience_range_to"] != 'NaN' else None




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
                    "company_id": row["company_id"],
                    "designation_id": row["designation_id"],
                    "designationrefName": designationrefName,
                    "industry_id": row["industry_id"],
                    "industryrefName": industryrefName,
                    "jobFunction_id": row["jobFunction_id"],
                    "jobFunctionName": jobFunctionName,
                    "jobFunctionrefName": jobFunctionrefName,
                    "portal": portal,
                    "id_1": row["id_1"],
                    "min_salary": min_salary,
                    "min_salary_currency": min_salary_currency,
                    "max_salary": max_salary,
                    "max_salary_currency": max_salary_currency,
                    "salary_frequency": salary_frequency,
                    "salary_description": salary_description,
                    "area": area,
                    "city": city,
                    "country": country,
                    "locationCoordinates_type": locationCoordinates_type,
                    "longitude": longitude,
                    "latitude": latitude,
                    "postedAt": postedAt,
                    "applyUrls": applyUrls,
                    "applyUrls_external": applyUrls_external,
                    "experience_range_from": experience_range_from,
                    "experience_range_to": experience_range_to,
                    "postedBy_url": postedBy_url,
                    "postedBy_name": postedBy_name,
                    "applicants": applicants,
                    "about_html": about_html,
                    "jobDetail_text": jobDetail_text,
                    "jobDetail_html": jobDetail_html,
                    "qualification_html": qualification_html,
                    "tags_jobs1": tags_jobs1,
                    "tags_jobs2": tags_jobs2,
                    "tags_jobs3": tags_jobs3,
                    "isBlackListed": isBlackListed,
                    "isExpired": isExpired,
                    "createdAt": createdAt,
                    "updatedAt": updatedAt,
                    "vectorText_designation": vectorText_designation,
                    "vectorText_skill": vectorText_skill,
                    "isBatched": isBatched,
                    "tags": tags,
                    "experience": experience,
                    "embedding": model.encode(f"{row['description']} {' '.join(skills)} {' '.join(tags)} {location} {designation} {industry} {jobFunctionName} {jobFunctionrefName} {designationrefName} {jobDetail_text} {min_salary} {max_salary} {area} {city} {country} {experience_range_from} {experience_range_to}").tolist()
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
    company_id = data.get("company_id", "")
    designation_id = data.get("designation_id", "")
    industry_id = data.get("industry_id", "")
    jobFunction_id = data.get("jobFunction_id", "")
    portal = data.get("portal", "").lower()
    min_salary = data.get("min_salary", None)
    max_salary = data.get("max_salary", None)
    salary_frequency = data.get("salary_frequency", "").lower()
    area = data.get("area", "").lower()
    city = data.get("city", "").lower()
    country = data.get("country", "").lower()
    # tags = data.get("tags", [])
    # skills = data.get("skills", [])
    # experience = data.get("experience", [])
    experience_range_from = data.get("experience_range_from", None)
    experience_range_to = data.get("experience_range_to", None)
    posted_by_name = data.get("postedBy_name", "").lower()
    is_blacklisted = data.get("isBlackListed", "").lower()
    is_expired = data.get("isExpired", "").lower()
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

        # Set size to 1000 if no must clauses are present (as per your original code)
        size = 1000
        print(87)
        # Add filters for exact matches on various fields
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
        if company_id:
            filter_clauses.append({"term": {"company_id": company_id}})
        if designation_id:
            filter_clauses.append({"term": {"designation_id": designation_id}})
        if industry_id:
            filter_clauses.append({"term": {"industry_id": industry_id}})
        if jobFunction_id:
            filter_clauses.append({"term": {"jobFunction_id": jobFunction_id}})
        if portal:
            filter_clauses.append({"term": {"portal": portal}})
        if salary_frequency:
            filter_clauses.append({"match": {"salary_frequency": salary_frequency}})
        if area:
            filter_clauses.append({"match": {"area": area}})
        if city:
            filter_clauses.append({"match": {"city": city}})
        if country:
            filter_clauses.append({"match": {"country": country}})
        if is_blacklisted:
            filter_clauses.append({"match": {"isBlackListed": is_blacklisted}})
        if is_expired:
            filter_clauses.append({"match": {"isExpired": is_expired}})
        if posted_by_name:
            filter_clauses.append({"match": {"postedBy_name": posted_by_name}})
        # if tags:
        #     filter_clauses.append({"terms": {"tags": tags}})
        # if skills:
        #     filter_clauses.append({"terms": {"skills": skills}})
        # if experience:
        #     filter_clauses.append({"terms": {"experience": experience}})
# Modify salary and experience range queries
        if min_salary is not None:
            filter_clauses.append({
                "bool": {
                    "should": [
                        {"range": {"min_salary": {"gte": min_salary}}},
                        {"range": {"max_salary": {"gte": min_salary}}}
                    ]
                }
            })

        if max_salary is not None:
            filter_clauses.append({
                "bool": {
                    "should": [
                        {"range": {"max_salary": {"lte": max_salary}}},
                        {"range": {"min_salary": {"lte": max_salary}}}
                    ]
                }
            })

        if experience_range_from is not None:
            filter_clauses.append({
                "bool": {
                    "should": [
                        {"range": {"experience_range_from": {"gte": experience_range_from}}},
                        {"range": {"experience_range_to": {"gte": experience_range_from}}}
                    ]
                }
            })

        if experience_range_to is not None:
            filter_clauses.append({
                "bool": {
                    "should": [
                        {"range": {"experience_range_to": {"lte": experience_range_to}}},
                        {"range": {"experience_range_from": {"lte": experience_range_to}}}
                    ]
                }
            })
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

    # Extract required and additional fields
    description = data.get("description", "")
    skills = data.get("skills", [])
    location = data.get("location", "")
    designation = data.get("designation", "")
    industry = data.get("industry", "")
    qualification = data.get("qualification", "")
    work_mode = data.get("workMode", "")
    job_type = data.get("jobType", "")
    company_id = data.get("company_id", "")
    designation_id = data.get("designation_id", "")
    designation_ref_name = data.get("designationrefName", "")
    industry_id = data.get("industry_id", "")
    industry_ref_name = data.get("industryrefName", "")
    job_function_id = data.get("jobFunction_id", "")
    job_function_name = data.get("jobFunctionName", "")
    job_function_ref_name = data.get("jobFunctionrefName", "")
    portal = data.get("portal", None)
    min_salary = data.get("min_salary", None)
    max_salary = data.get("max_salary", None)
    salary_frequency = data.get("salary_frequency", "")
    area = data.get("area", "")
    city = data.get("city", "")
    country = data.get("country", "")
    tags = data.get("tags", [])
    experience = data.get("experience", [])
    experience_range_from = data.get("experience_range_from", None)
    experience_range_to = data.get("experience_range_to", None)
    job_detail_text = data.get("jobDetail_text", "")
    posted_by_name = data.get("postedBy_name", "")
    is_blacklisted = data.get("isBlackListed", None)
    is_expired = data.get("isExpired", None)

    # Sanitize and normalize fields
    location = location.lower() if location and location != "NaN" and pd.notna(location) else None
    designation = designation.lower() if designation else None
    industry = industry.lower() if industry else None
    work_mode = work_mode.lower() if work_mode else None
    job_type = job_type.lower() if job_type else None
    qualification = qualification.strip() if qualification else None
    salary_frequency = salary_frequency.lower() if salary_frequency else None
    area = area.lower() if area else None
    city = city.lower() if city else None
    country = country.lower() if country else None
    posted_by_name = posted_by_name.lower() if posted_by_name else None

    # Generate embedding for the job
    embedding_input = (
        f"{description} {' '.join(skills)} {location or ''} {designation or ''} {industry or ''} "
        f"{qualification or ''} {work_mode or ''} {job_type or ''} {job_function_name or ''} "
        f"{job_function_ref_name or ''} {designation_ref_name or ''} {job_detail_text or ''} "
        f"{' '.join(tags)} {min_salary or ''} {max_salary or ''} {area or ''} {city or ''} "
        f"{country or ''} {experience_range_from or ''} {experience_range_to or ''}"
    )
    embedding = model.encode(embedding_input).tolist()

    # Add embedding and normalized fields to the document
    data.update({
        "embedding": embedding,
        "location": location,
        "designation": designation,
        "industry": industry,
        "qualification": qualification,
        "workMode": work_mode,
        "jobType": job_type,
        "salary_frequency": salary_frequency,
        "area": area,
        "city": city,
        "country": country,
        "tags": tags if isinstance(tags, list) else [],
        "experience_range_from": experience_range_from,
        "experience_range_to": experience_range_to,
        "jobDetail_text": job_detail_text,
        "postedBy_name": posted_by_name,
        "isBlackListed": is_blacklisted,
        "isExpired": is_expired,
    })

    # Ensure arrays and numeric values are handled
    data["skills"] = skills if isinstance(skills, list) else []
    data["portal"] = portal
    data["min_salary"] = min_salary
    data["max_salary"] = max_salary
    data["company_id"] = company_id
    data["designation_id"] = designation_id
    data["designationrefName"] = designation_ref_name
    data["industry_id"] = industry_id
    data["industryrefName"] = industry_ref_name
    data["jobFunction_id"] = job_function_id
    data["jobFunctionName"] = job_function_name
    data["jobFunctionrefName"] = job_function_ref_name

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
