import uuid
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from typing import Dict, List
import PyPDF2
from openai import OpenAI
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = '../data'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200", basic_auth=("elastic", "search"))

INDEX_NAME = "users"
EMBEDDING_DIM = 1536

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ResumeProcessor:
    def __init__(self):
        self.setup_elasticsearch()

    def setup_elasticsearch(self):
        """Setup Elasticsearch index with mappings"""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text"},
                    "email": {"type": "keyword"},
                    "mobile": {"type": "keyword"},
                    "city": {"type": "text"},
                    "location": {"type": "text"},
                    "skills": {"type": "text"},
                    "education": {"type": "object",
                        "properties": {
                            "institution": {"type": "text"},
                            "major": {"type": "text"},
                            "year": {"type": "text"},
                            "degree": {"type": "text"},
                            "CGPA": {"type": "text"}
                        }
                    },
                    "embedding": {"type": "dense_vector", "dims": EMBEDDING_DIM}
                }
            }
        }

        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(index=INDEX_NAME, body=mapping)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text

    def get_embedding(self, text: str) -> List[float]:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def create_combined_text(self, data: Dict) -> str:
        return f"""
        Location: {data['location']} {data['city']}
        Skills: {data['skills']}
        education: {data['education']}
        """.strip()

#     import json
# from typing import Dict

    def extract_resume_data(self, text: str) -> Dict:
        unique_id = str(uuid.uuid4())  # Generate a unique user ID before making the request

        prompt = f"""
        Extract the following information from the resume text and format as JSON:
        - name
        - email
        - mobile
        - city
        - location (state only)
        - skills (as an array of strings)
        - education (education details which will be institution, major, year, degree, CGPA)
        There can be more than one education extract them all

        Resume text:
        {text}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            resume_data = json.loads(response.choices[0].message.content)
            resume_data["id"] = unique_id  # Add the generated ID to the response
            return resume_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            raise


    def process_resume(self, pdf_path: str):
        try:
            text = self.extract_text_from_pdf(pdf_path)
            resume_data = self.extract_resume_data(text)
            combined_text = self.create_combined_text(resume_data)
            resume_data['embedding'] = self.get_embedding(combined_text)
            es.index(index=INDEX_NAME, document=resume_data)
            return resume_data
        except Exception as e:
            print(f"Error processing resume: {str(e)}")
            raise

# Initialize processor
processor = ResumeProcessor()

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    """Endpoint to upload and process a resume"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the resume
            result = processor.process_resume(filepath)
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            return jsonify({
                'message': 'Resume processed successfully',
                'data': result
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/search', methods=['POST'])
def search_resumes():
    """Endpoint to search resumes with semantic query and filters"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No search criteria provided'}), 400

        semantic_query = data.get('query', '')
        filters = data.get('filters', {})

        # Get embedding for the semantic query
        query_embedding = processor.get_embedding(semantic_query)

        # Build Elasticsearch query
        should_queries = []
        must_queries = []

        # Add semantic search query
        if semantic_query:
            should_queries.append({
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            })

        # Add filters
        for field, value in filters.items():
            if field in ['name', 'city', 'location', 'skills']:
                must_queries.append({"match": {field: value}})
            elif field in ['email', 'mobile']:
                must_queries.append({"term": {field: value}})
            elif field == 'education':
                for edu_field, edu_value in value.items():
                    must_queries.append({
                        "match": {f"education.{edu_field}": edu_value}
                    })

        # Combine queries
        query = {
            "query": {
                "bool": {
                    "should": should_queries,
                    "must": must_queries,
                    "minimum_should_match": 0
                }
            }
        }

        # Execute search
        results = es.search(index=INDEX_NAME, body=query)

        # Format response
        hits = results['hits']['hits']
        formatted_results = [
            {
                'score': hit['_score'],
                'data': hit['_source']
            }
            for hit in hits
        ]

        return jsonify({
            'message': 'Search completed successfully',
            'results': formatted_results,
            'total': len(formatted_results)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)