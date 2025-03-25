import os
from typing import Dict, List
import PyPDF2
from openai import OpenAI
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200", basic_auth=("elastic", "search"))

INDEX_NAME = "users"
EMBEDDING_DIM = 1536  # Dimension for text-embedding-ada-002 model

class ResumeProcessor:# Dimension for text-embedding-ada-002 model
    def __init__(self):
        self.setup_elasticsearch()

    def setup_elasticsearch(self):
        """Setup Elasticsearch index with mappings"""
        mapping = {
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "email": {"type": "keyword"},
                    "mobile": {"type": "keyword"},
                    "city": {"type": "text"},
                    "location": {"type": "text"},
                    "skills": {"type": "text"},
                    "education": {"type": "object",
                        "properties": {
                        "institution": { "type": "text" },
                        "major": { "type": "text" },
                        "year": { "type": "text" },
                        "degree": { "type": "text" },
                        "CGPA": { "type": "text" }
                        }},
                    "embedding": {"type": "dense_vector", "dims": EMBEDDING_DIM}
                }
            }
        }

        # Create index if it doesn't exist
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(index=INDEX_NAME, body=mapping)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text

    def get_embedding(self, text: str) -> List[float]:
        """Get embeddings from OpenAI"""
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def create_combined_text(self, data: Dict) -> str:
        """Create a combined text string from all relevant fields"""
        return f"""
        Location: {data['location']} {data['city']}
        Skills: {data['skills']}
        education: {data['education']}
        """.strip()

    def extract_resume_data(self, text: str) -> Dict:
        """Extract structured data from resume text using OpenAI"""
        prompt = f"""
        Extract the following information from the resume text and format as JSON:
        - name
        - email
        - mobile
        - city
        - location (state only)
        - skills (as a comma-separated string)
        - education (education details which will only be institution, major, year, degree, CGPA)

        Resume text:
        {text}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            raise

    def process_resume(self, pdf_path: str):
        """Process resume and store in Elasticsearch"""
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_path)
            
            # Extract structured data using OpenAI
            resume_data = self.extract_resume_data(text)
            
            # Create combined text for embedding
            combined_text = self.create_combined_text(resume_data)
            
            # Get embedding for combined text
            resume_data['embedding'] = self.get_embedding(combined_text)
            
            # Index document in Elasticsearch
            es.index(index=INDEX_NAME, document=resume_data)
            
            return resume_data
        except Exception as e:
            print(f"Error processing resume: {str(e)}")
            raise

def main():
    # Initialize processor
    processor = ResumeProcessor()
    
    # Process resume
    pdf_path = "C:\\Users\\rs656\\Downloads\\Rahul_janoff.pdf"  # Replace with actual path
    result = processor.process_resume(pdf_path)
    # print(f"Processed resume and stored data: {result}")

if __name__ == "__main__":
    main()