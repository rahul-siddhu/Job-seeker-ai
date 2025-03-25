from flask import Flask, request, jsonify
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import json
from typing import Dict, List, Optional, TypedDict
from pydantic import BaseModel
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)

# Initialize OpenAI and Elasticsearch clients
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
es_client = Elasticsearch(
    os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200"),
    basic_auth=(
        os.getenv("ELASTICSEARCH_USERNAME", "elastic"),
        os.getenv("ELASTICSEARCH_PASSWORD", "changeme")
    )
)

# 1. User Input Layer
# Just validating if the query is a not empty string or not
class JobSearchQuery(BaseModel):
    query: str

# 2. Natural Language Understanding Layer
class ParsedJobCriteria(TypedDict):
    min_salary: Optional[int]
    max_salary: Optional[int]
    experience_range_from: Optional[int]
    experience_range_to: Optional[int]
    city: Optional[str]
    qualification: Optional[str]
    workMode: Optional[str]
    location: Optional[str]
    skills: List[str]

# Function calling definition for OpenAI
QUERY_PARSER_FUNCTION = {
    "name": "parse_job_search_criteria",
    "description": "Parse job search query into structured criteria",
    "parameters": {
        "type": "object",
        "properties": {
            "min_salary": {"type": "integer", "description": "Minimum salary requirement"},
            "max_salary": {"type": "integer", "description": "Maximum salary requirement"},
            "experience_range_from": {"type": "integer", "description": "Minimum years of experience"},
            "experience_range_to": {"type": "integer", "description": "Maximum years of experience"},
            "city": {"type": "string", "description": "City name"},
            "qualification": {"type": "string", "description": "Educational qualification"},
            "workMode": {"type": "string", "description": "Work mode (remote/hybrid/onsite)"},
            "location": {"type": "string", "description": "Job location"},
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Required skills"
            }
        }
    }
}

class NLUProcessor:
    @staticmethod
    async def parse_query(query: str) -> ParsedJobCriteria:
        """Parse natural language query using OpenAI function calling."""
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a job search query parser. Extract structured information from the user's query."},
                {"role": "user", "content": query}
            ],
            functions=[QUERY_PARSER_FUNCTION],
            function_call={"name": "parse_job_search_criteria"}
        )
        
        function_args = response.choices[0].message.function_call.arguments
        return json.loads(function_args)

# 3. Query Translation Layer
class QueryBuilder:
    @staticmethod
    def build_elasticsearch_query(criteria: ParsedJobCriteria) -> Dict:
        """Convert parsed criteria into Elasticsearch query."""
        must_clauses = []
        should_clauses = []
        
        # Add salary range filter
        if criteria.get('min_salary') or criteria.get('max_salary'):
            salary_range = {
                "range": {
                    "salary": {
                        "gte": criteria.get('min_salary', 0),
                        "lte": criteria.get('max_salary', 1000000)
                    }
                }
            }
            must_clauses.append(salary_range)
        
        # Add experience range filter
        if criteria.get('experience_range_from') or criteria.get('experience_range_to'):
            experience_range = {
                "range": {
                    "experience": {
                        "gte": criteria.get('experience_range_from', 0),
                        "lte": criteria.get('experience_range_to', 50)
                    }
                }
            }
            must_clauses.append(experience_range)
        
        # Add location filters
        if criteria.get('city'):
            must_clauses.append({"match": {"city": criteria['city']}})
        if criteria.get('location'):
            must_clauses.append({"match": {"location": criteria['location']}})
            
        # Add qualification filter
        if criteria.get('qualification'):
            must_clauses.append({"match": {"qualification": criteria['qualification']}})
            
        # Add work mode filter
        if criteria.get('workMode'):
            must_clauses.append({"match": {"workMode": criteria['workMode']}})
            
        # Add skills as should clauses
        if criteria.get('skills'):
            for skill in criteria['skills']:
                should_clauses.append({"match_phrase": {"skills": skill}})
        
        return {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "should": should_clauses,
                    "minimum_should_match": 1 if should_clauses else 0
                }
            }
        }

# 4. Elasticsearch Retrieval Layer
class JobSearcher:
    def __init__(self, es_client):
        self.es_client = es_client
    
    def search_jobs(self, query_body: Dict, size: int = 5) -> List[Dict]:
        """Execute search query and return results."""
        response = self.es_client.search(
            index="jobs",
            body=query_body,
            size=size
        )
        return response["hits"]["hits"]

# 5. Response Generation Layer
class ResponseGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.template = """
        You are a helpful assistant that provides detailed responses about job postings.
        
        Original Query: {query}
        Found Jobs: {context}
        
        Provide a concise summary of the available jobs based on the search criteria.
        Focus on mentioning the number of positions found and their general requirements.
        """
        self.prompt = PromptTemplate(template=self.template, input_variables=["query", "context"])
    
    def format_context(self, hits: List[Dict]) -> str:
        """Format search results into context for LLM."""
        return "\n".join([
            f"- {hit['_source'].get('name', 'Untitled')} "
            f"({hit['_source'].get('designation', 'N/A')}): "
            f"{hit['_source'].get('description', 'No description')[:200]}... "
            f"[Location: {hit['_source'].get('location', 'N/A')} | "
            f"Salary: {hit['_source'].get('salary', 'N/A')} | "
            f"Experience: {hit['_source'].get('experience', 'N/A')}]"
            for hit in hits
        ])
    
    def format_jobs_list(self, hits: List[Dict]) -> List[Dict]:
        """Format jobs for the response."""
        print(999999)
        print(f"Processing {len(hits)} hits")  # Debug print
        formatted_jobs = []
        for hit in hits:
            source = hit['_source']
            # Get all possible URL fields
            apply_url = (
                source.get('applyUrls') or
                'No URL available'
            )
            job_title = source.get('name') or source.get('title', 'Untitled Position')
            
            formatted_jobs.append({job_title: apply_url})
        return formatted_jobs
    
    async def generate_response(self, query: str, hits: List[Dict]) -> Dict:
        """Generate final response including LLM summary and job listings."""
        context = self.format_context(hits)
        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        summary = await chain.arun(query=query, context=context)
        jobs = self.format_jobs_list(hits)
        
        return {
            "response": summary,
            "jobs": jobs
        }

# Main API route
@app.route("/query", methods=["POST"])
async def query():
    """Handle job search queries."""
    try:
        # 1. Get user input
        data = request.json
        search_query = JobSearchQuery(query=data.get("query"))
        
        # 2. Parse query using NLU
        parsed_criteria = await NLUProcessor.parse_query(search_query.query)
        
        # 3. Build Elasticsearch query
        query_body = QueryBuilder.build_elasticsearch_query(parsed_criteria)
        
        # 4. Search jobs (synchronous operation)
        job_searcher = JobSearcher(es_client)
        search_results = job_searcher.search_jobs(query_body)
        
        # 5. Generate response
        response_generator = ResponseGenerator(llm)
        final_response = await response_generator.generate_response(
            search_query.query,
            search_results
        )
        
        return jsonify(final_response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)