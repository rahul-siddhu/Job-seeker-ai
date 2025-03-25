from flask import Flask, request, jsonify
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from elasticsearch import Elasticsearch, NotFoundError
from dotenv import load_dotenv
import os
import json
import traceback
from typing import Dict, List, Optional, TypedDict
from pydantic import BaseModel
from openai import AsyncOpenAI
#************Getting req jobs from semantic searching and applying filters on them as well********************
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
    queryType: Optional[bool]
    job_relevant: Optional[bool]
    # user_id: Optional[str]

# Function calling definition for OpenAI
QUERY_PARSER_FUNCTION = {
    "name": "parse_job_search_criteria",
    "description": "Parse job search query into structured criteria, extracting all relevant information",
    "parameters": {
        "type": "object",
        "properties": {
            "min_salary": {
                "type": "integer",
                "description": "Minimum salary requirement in numbers only. Extract if mentioned explicitly"
            },
            "max_salary": {
                "type": "integer",
                "description": "Maximum salary requirement in numbers only. Extract if mentioned explicitly"
            },
            "experience_range_from": {
                "type": "integer",
                "description": "Minimum years of experience in numbers only. Extract if mentioned explicitly"
            },
            "experience_range_to": {
                "type": "integer",
                "description": "Maximum years of experience in numbers only. Extract if mentioned explicitly"
            },
            "city": {
                "type": "string",
                "description": "Name of the city if specifically mentioned. Should be the exact city name"
            },
            "location": {
                "type": "string",
                "description": "State, region, or country name if mentioned. Use this for non-city locations"
            },
            "qualification": {
                "type": "string",
                "description": "Educational qualification if mentioned (e.g., BTech, MBA, etc.)"
            },
            "workMode": {
                "type": "string",
                "description": "Work mode if mentioned (In Office/Hybrid/From Home). Leave empty if not specified"
            },
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of all technical skills, technologies, and job roles mentioned. Extract both explicit skills and those implied from job titles"
            },
            "queryType":{
                "type":"boolean",
                "description":"Mark true only if the query is regarding adding or updating user's data(can be skills, location or any other field), false otherwise",
                "default": False
            },
            "job_relevant":{
                "type":"boolean",
                "description":"Mark true only if the query is regarding jobs or updating user's data(can be skills, location or any other field), false otherwise",
                "default": False
            }
        },
        "required": ["skills"]  # Only skills is required, others are optional
    }
}

class NLUProcessor:

    #Currently this function is not in use
    @staticmethod
    async def parse_query(query: str) -> ParsedJobCriteria:
        """Parse natural language query using OpenAI function calling."""
        system_prompt = """
        You are a specialized job search query parser. Your role is to extract structured information from user queries.
        
        Important parsing rules:
        1. Skills:
           - Extract both explicit technical skills (python, java, etc.)
           - Include skills implied from job titles (e.g., "developer" → programming)
           - Always return skills in lowercase
           - For job titles like "software engineer", include both "software engineering" and "software development" as skills
        
        2. Location handling:
           - If a city is specifically mentioned, put it in "city"
           - Put states, regions, or countries in "location"
           - Don't duplicate locations in both fields
        
        3. Experience and Salary:
           - Only extract if explicitly mentioned
           - Convert all numbers to integers
           - Don't assume or infer ranges if not mentioned
        
        4. Work Mode:
           - Only set if explicitly mentioned as remote, hybrid, or onsite
           - Leave empty if not specified
        
        Examples:
        1. "python jobs in karnataka"
           → {"skills": ["python"], "location": "karnataka"}
        
        2. "senior software engineer in bangalore with 5 years experience"
           → {"skills": ["software engineering", "software development"], "city": "bangalore", "experience_range_from": 5}
        
        3. "remote java developer jobs in hyderabad 15-20 lpa"
           → {"skills": ["java", "software development"], "city": "hyderabad", "workMode": "remote", "min_salary": 1500000, "max_salary": 2000000}
        
        4. "frontend developer with react bangalore"
           → {"skills": ["frontend development", "react"], "city": "bangalore"}
        
        Always extract the maximum possible information while maintaining accuracy.
        Don't add information that isn't explicitly mentioned or strongly implied by the query.
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            functions=[QUERY_PARSER_FUNCTION],
            function_call={"name": "parse_job_search_criteria"}
        )
        
        function_args = response.choices[0].message.function_call.arguments
        parsed_criteria = json.loads(function_args)
        
        # Debug print
        print("Original query:", query)
        print("Parsed criteria:", json.dumps(parsed_criteria, indent=2))
        
        return parsed_criteria
    @staticmethod
    async def parse_query(query: str) -> ParsedJobCriteria:
        """Parse natural language query using OpenAI function calling."""
        system_prompt = """
        You are a job search and user update query parser. 
        Extract structured information from the user's query.
        For skills, extract both explicit skills and implied skills from job titles.
        If the query is about updating the user's profile (such as adding skills or changing location), 
        set `queryType` to `true`. Otherwise, set `queryType` to `false`.
        If the query is about jobs or about updating user's profile, then set `job_relevant` to `true`.
        Otherwise, set `job_relevant` to `false`.
        Examples:
        - "python jobs in karnataka" → skills: ["python"], location: "karnataka", queryType: false, job_relevant: true
        - "Add Python and Java to my skills" → skills: ["Python", "Java"], queryType: true, job_relevant: true
        - "Change my location to Delhi" → location: "Delhi", queryType: true, job_relevant: true
        - "Who is PM of India?" → queryType: false, job_relevant: false
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            functions=[QUERY_PARSER_FUNCTION],
            function_call={"name": "parse_job_search_criteria"}
        )
        
        function_args = response.choices[0].message.function_call.arguments
        parsed_criteria = json.loads(function_args)
        parsed_criteria.setdefault("queryType", False)
        parsed_criteria.setdefault("job_relevant", False)
        
        # Debug print
        # print("Parsed criteria:", json.dumps(parsed_criteria, indent=2))
        
        return parsed_criteria
# 3. Query Translation Layer
# from typing import Dict

class QueryBuilder:
    def __init__(self, es_client):
        self.es_client = es_client

    async def get_user_skills(self, user_id: str) -> List[str]:
        """Fetch user skills from Elasticsearch."""
        try:
            user_doc = self.es_client.get(
                index="users",
                id=user_id
            )
            return user_doc['_source'].get('skills', [])
        except Exception as e:
            print(f"Error fetching user skills: {str(e)}")
            return []
    # @staticmethod
    async def build_elasticsearch_query(self, criteria: ParsedJobCriteria) -> Dict:
        """Convert parsed criteria into Elasticsearch query with specified structure."""
        must_clauses = []
        filter_clauses = []
        should_clauses = []
        
        # Fetch user skills if user_id is provided
        if criteria.get('user_id'):
            user_skills = await self.get_user_skills(criteria['user_id'])
            if user_skills:
                # Add user skills to the existing skills list
                existing_skills = criteria.get('skills', [])
                criteria['skills'] = list(set(existing_skills + user_skills))
        
        # Add must clauses for location fields
        if criteria.get('city'):
            must_clauses.append({
                "match": {
                    "city": criteria['city']
                }
            })
            
        if criteria.get('location'):
            must_clauses.append({
                "match": {
                    "location": criteria['location']
                }
            })
            
        if criteria.get('workMode'):
            must_clauses.append({
                "match": {
                    "workMode": criteria['workMode']
                }
            })

        # Add filter clauses for ranges
        if criteria.get('min_salary'):
            filter_clauses.append({
                "range": {
                    "max_salary": {
                        "gte": criteria['min_salary']
                    }
                }
            })
            
        if criteria.get('max_salary'):
            filter_clauses.append({
                "range": {
                    "min_salary": {
                        "lte": criteria['max_salary']
                    }
                }
            })
            
        if criteria.get('experience_range_to'):
            filter_clauses.append({
                "range": {
                    "experience_range_from": {
                        "lte": criteria['experience_range_to']
                    }
                }
            })
            
        if criteria.get('experience_range_from'):
            filter_clauses.append({
                "range": {
                    "experience_range_to": {
                        "gte": criteria['experience_range_from']
                    }
                }
            })

        # Add should clauses for qualification and skills
        if criteria.get('qualification'):
            should_clauses.append({
                "match": {
                    "qualification": criteria['qualification']
                }
            })
            
        if criteria.get('skills'):
            for skill in criteria['skills']:
                should_clauses.append({
                    "match": {
                        "skills": {
                            "query": skill,
                            "boost": 3.0
                        }
                    }
                })

        # Build the final query
        query = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses,
                    "should": should_clauses,
                    "minimum_should_match": 1 if should_clauses else 0
                }
            }
        }
        
        return query
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
        You are a helpful assistant named "Buddy-bot" by "joblo.ai" that provides detailed responses about job postings.
        
        Original Query: {query}
        Found Jobs: {context}
        
        Based on "Orignal Query" and "Found Jobs" if jobs are found then,
        provide a concise summary of the available jobs based on the search criteria,
        if no jobs are found state that no jobs are found based on Orignal query and suggest user to provide more context for the job search
        Focus on mentioning the number of positions found and their general requirements.
        """
        # print("########")
        # # print(f'{context}')
        # print("########")
        self.prompt = PromptTemplate(template=self.template, input_variables=["query", "context"])
    
    def format_context(self, hits: List[Dict]) -> str:
        """Format search results into context for LLM."""
        return "\n".join([
            f"- {hit['_source'].get('name', 'Untitled')} "
            f"({hit['_source'].get('designation', 'N/A')}): "
            # f"{hit['_source'].get('description', 'No description')[:200]}... "
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
        print("########")
        print(context)
        print("########")
        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        summary = await chain.arun(query=query, context=context)
        jobs = self.format_jobs_list(hits)
        
        return {
            "response": summary,
            "jobs": jobs
        }
    
    async def off_response(self, query: str):
        template="""
        You are a helpful assistant named "Buddy-bot" by "joblo.ai" that provides one liner response.
        Original Query: {query}
        Also ask user politely for querying about jobs.
        """
        prompt = PromptTemplate(template=template, input_variables=["query"])
        chain = LLMChain(llm=self.llm, prompt=prompt)
        summary = await chain.arun(query=query)
        
        return {
            "response": summary
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

        user_id=data.get("user_id")
        if user_id :
            parsed_criteria['user_id']=user_id
        else:
            parsed_criteria['user_id']=None
        
        print("**********************")
        print("Parsed criteria:", json.dumps(parsed_criteria, indent=2))
        print("**********************")
        
        if not parsed_criteria['job_relevant'] and not parsed_criteria['queryType']:
            response_generator = ResponseGenerator(llm)
            final_response = await response_generator.off_response(
                search_query.query
            )
            return jsonify(final_response)

        elif parsed_criteria['queryType']:
            """Handling job update queries."""
            try:
                user_id = data.get("user_id")
                if not user_id:
                    return jsonify({
                        "status": "error",
                        "message": "user_id is required"
                    }), 400

                parsed_criteria['user_id'] = user_id
                
                try:
                    # Get current user document
                    user_doc = es_client.get(
                        index="users",
                        id=user_id
                    )
                    
                    # Get existing skills from nested data structure
                    current_skills = user_doc['_source'].get('skills', [])

                    # current_skills = user_doc['_source'].get('data', {}).get('skills', [])
                    print("++++++++++++++++++++++++++")
                    print(current_skills)
                    # Add new skills from parsed criteria
                    new_skills = parsed_criteria.get('skills', [])
                    new_location = parsed_criteria.get('location', "")
                    new_city = parsed_criteria.get('city', "")
                    
                    # Merge skills and remove duplicates while preserving order
                    # print(new_skills)
                    updated_skills = list(dict.fromkeys(current_skills + new_skills))
                    if new_location != "":
                        es_client.update(
                            index="users",
                            id=user_id,  # Use Elasticsearch's internal _id
                            body={
                                "doc": {  # Update fields
                                    "location": new_location
                                }
                            }
                        )
                    if new_city != "":
                        es_client.update(
                            index="users",
                            id=user_id,  # Use Elasticsearch's internal _id
                            body={
                                "doc": {  # Update fields
                                    "city": new_city
                                }
                            }
                        )
                    print(updated_skills)
                    
                    # Update user document with new skills
                    es_client.update(
                        index="users",
                        id=user_id,  # Use Elasticsearch's internal _id
                        body={
                            "doc": {  # Update fields
                                "skills": updated_skills
                            }
                        }
                    )
                    
                    # Fetch updated user document
                    # updated_user = es_client.get(
                    #     index="users",
                    #     id=user_id
                    # )
                    
                    return jsonify({
                        "status": "success",
                        "message": "Skills updated successfully",
                        "previous_skills": current_skills,
                        "new_skills": new_skills,
                        "updated_skills": updated_skills
                        # "resume_data": updated_user['_source']['data']  # Return only the data object
                    })
                    
                except NotFoundError:
                    return jsonify({
                        "status": "error",
                        "message": f"User with ID {user_id} not found"
                    }), 404
                
            except Exception as e:
                print(f"Error in update endpoint: {str(e)}")
                traceback.print_exc()
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500    
        else :
        # 3. Build Elasticsearch query
            query_builder = QueryBuilder(es_client)
            query_body = await query_builder.build_elasticsearch_query(parsed_criteria)

            # query_body = await QueryBuilder.build_elasticsearch_query(parsed_criteria)
            print("=========================")
            print("Elasticsearch query:", json.dumps(query_body, indent=2))
            print("=========================")
            
            # 4. Search jobs (synchronous operation)
            job_searcher = JobSearcher(es_client)
            search_results = job_searcher.search_jobs(query_body)
            print("///////////////////////")
            print(search_results)
            print("////////////////////////")
            
            # 5. Generate response
            response_generator = ResponseGenerator(llm)
            final_response = await response_generator.generate_response(
                search_query.query,
                search_results
            )
            print()
            return jsonify(final_response)
        
    except Exception as e:
        return jsonify({"errorr": str(e)}), 500
    
@app.route("/update", methods=["POST"])
async def update():
    """Handling job update queries."""
    try:
        # 1. Get user input
        data = request.json
        search_query = JobSearchQuery(query=data.get("query"))
        
        # 2. Parse query using NLU
        parsed_criteria = await NLUProcessor.parse_query(search_query.query)

        user_id = data.get("user_id")
        if not user_id:
            return jsonify({
                "status": "error",
                "message": "user_id is required"
            }), 400

        parsed_criteria['user_id'] = user_id
        
        try:
            # Get current user document
            user_doc = es_client.get(
                index="users",
                id=user_id
            )
            
            # Get existing skills from nested data structure
            current_skills = user_doc['_source'].get('skills', [])

            # current_skills = user_doc['_source'].get('data', {}).get('skills', [])
            print("++++++++++++++++++++++++++")
            print(current_skills)
            # Add new skills from parsed criteria
            new_skills = parsed_criteria.get('skills', [])
            
            # Merge skills and remove duplicates while preserving order
            # print(new_skills)
            updated_skills = list(dict.fromkeys(current_skills + new_skills))
            print(updated_skills)
            
            # Update user document with new skills
            es_client.update(
                index="users",
                id=user_id,  # Use Elasticsearch's internal _id
                body={
                    "doc": {  # Update fields
                        "skills": updated_skills
                    }
                }
            )
            
            # Fetch updated user document
            # updated_user = es_client.get(
            #     index="users",
            #     id=user_id
            # )
            
            return jsonify({
                "status": "success",
                "message": "Skills updated successfully",
                "previous_skills": current_skills,
                "new_skills": new_skills,
                "updated_skills": updated_skills
                # "resume_data": updated_user['_source']['data']  # Return only the data object
            })
            
        except NotFoundError:
            return jsonify({
                "status": "error",
                "message": f"User with ID {user_id} not found"
            }), 404
        
    except Exception as e:
        print(f"Error in update endpoint: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)