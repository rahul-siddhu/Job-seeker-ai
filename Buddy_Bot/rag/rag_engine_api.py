from flask import Flask, request, jsonify
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)

# Elasticsearch connection
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
ES_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
ES_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "changeme")

# Initialize Elasticsearch client with authentication
es_client = Elasticsearch(
    ES_HOST,
    basic_auth=(ES_USERNAME, ES_PASSWORD)
)

# Template for RAG
template = """
You are a helpful assistant that provides detailed responses about job postings.

Query: {query}

Use the following job data retrieved from the database:
{context}

Provide a short response based on the context.
"""

# Elasticsearch query function
def search_elasticsearch(index, query, size=5):
    """Search Elasticsearch for relevant documents."""
    response = es_client.search(
        index=index,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["skills^2", "name", "description", "designation", "industry", "qualification"]
                }
            }
        },
        size=size
    )
    hits = response["hits"]["hits"]
    return [hit["_source"] for hit in hits]

# Create a function to retrieve and format data
def get_context(index, query):
    """Retrieve job data from Elasticsearch and format it."""
    documents = search_elasticsearch(index, query)
    context = "\n".join([
        f"- {doc['name']} ({doc.get('designation', 'N/A')}): {doc['description'][:200]}... "
        f"[Location: {doc.get('location', 'N/A')} | Job Type: {doc.get('jobType', 'N/A')}]"
        for doc in documents
    ])
    return context

# Route for the RAG API
@app.route("/query", methods=["POST"])
def query():
    """Handle job-related queries."""
    try:
        data = request.json
        user_query = data.get("query")
        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        # Fetch context from Elasticsearch
        index = "jobs"  # Your Elasticsearch index name
        context = get_context(index, user_query)

        # Set up the LLM chain
        llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
        prompt = PromptTemplate(template=template, input_variables=["query", "context"])
        chain = LLMChain(llm=llm, prompt=prompt)

        # Generate response
        response = chain.run({"query": user_query, "context": context})
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
