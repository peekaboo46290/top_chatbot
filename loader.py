import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from pydantic import BaseModel, Field

from langchain_neo4j import Neo4jGraph
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_ollama.llms import OllamaLLM
from streamlit.logger import get_logger

from utils import initialize_smth, read_pdf_pymupdf, parse_response
from chains import load_embedding_model

input_path = "./input/"#badel

load_dotenv(".env")

url = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
ollama_base_url = os.getenv("OLLAMA_BASE_URL")
llm_name = os.getenv("LLM")

logger = get_logger(__name__)

prompt = PromptTemplate(
    input_variables=["text"],
    template="""You are an expert mathematician. Extract all mathematical theorems, lemmas, propositions, and corollaries from the text below.

Return ONLY a valid JSON object in this exact format (no other text):
{{
"theorems": [
{{
    "name": "theorem name",
    "statement": "formal mathematical statement",
    "proof": "proof text or 'Not provided'",
    "subject": "main subject: Algebra, Analysis, Topology, Number Theory, Geometry, Probability, or Logic",
    "domain": "specific subdomain like Linear Algebra, Real Analysis, Group Theory, etc.",
    "dependencies": ["theorem1", "theorem2"],
    "type": "Theorem, Lemma, Proposition, or Corollary"
}}
]
}}

Rules:
1. Extract ALL mathematical statements
2. Use clear, standard mathematical terminology
3. If proof is not explicit, write "Not provided"
4. Dependencies are theorem names mentioned in the proof
5. Return valid JSON only
6. Read the Context twice and carefully before generating JSON object.
7. Do not return anything other than the JSON object.
8. Do not include any explanations or apologies in your responses.
9. Do not hallucinate.

Text to analyze:
{text}

JSON response:"""
        )
        


embeddings, dimension = load_embedding_model(
    config={"ollama_base_url": ollama_base_url, "llm" : llm_name}, logger=logger
)

llm = OllamaLLM(
    model = llm_name,
    base_url = ollama_base_url,
    temperature=0,
    num_predict= dimension,
    top_p=0.3,  # Higher value (0.95) will lead to more diverse text, while a lower value (0.5) will generate more focused text.
)

chain = LLMChain(llm= llm, prompt= prompt, verbose=False)
logger.info("did the chain stuff")

#loading neo4j
neo4j_graph = Neo4jGraph(
    url=url, username=username, password=password, refresh_schema=False
)
initialize_smth(neo4j_graph)
logger.info("Successfully connected to Neo4j")


#creating class for theorem

class Theorem(BaseModel):
    name:str
    statement: str
    proof: str = "Not provided"
    subject:str #alg or anl ...
    domain: str #top or cal..
    dependencies: List[str]
    t_type:str #lemme or prop ... 
    
def add_theorem(theorem:Theorem):
    try:
        create_theorem_query = """
        MERGE (t:Theorem {name: $name})
                SET t.statement = $statement,
                    t.proof = $proof,
                    t.type = $type
                    //you can remove below added them for the haha
                    t.updated_at = datetime()
                ON CREATE SET t.created_at = datetime()
                
                MERGE (s:Subject {name: $subject})
                MERGE (t)-[:BELONGS_TO_SUBJECT]->(s)

                MERGE (d:Domain {name: $domain})
                MERGE (t)-[:BELONGS_TO_DOMAIN]->(d)
                MERGE (d)-[:PART_OF_SUBJECT]->(s)
                
                RETURN t.name as name
        """#hound dog
        neo4j_graph.query(
            create_theorem_query,
            params={
                'name': theorem.name,
                'statement': theorem.statement,
                'proof': theorem.proof,
                'type': theorem.t_type,
                'subject': theorem.subject,
                'domain': theorem.domain
            }
        )

        for dep_name in theorem.dependencies:
            if dep_name.strip():
                dep_query = """
                MATCH (t:Theorem {name: $theorem_name})
                MERGE (d:Theorem {name: $dep_name})
                MERGE (t)-[:DEPENDS_ON]->(d)
                """
                neo4j_graph.query(
                    dep_query,
                    params={
                        'theorem_name': theorem.name,
                        'dep_name': dep_name.strip()
                    }
                )

        logger.info(f"Added: {theorem.name}")
        return True
    except Exception as e:
        logger.info(f"Failed to add {theorem.name}: {e}")
        return False    

def get_theorems_by_subject(subject: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
        MATCH (t:Theorem)-[:BELONGS_TO_SUBJECT]->(s:Subject {name: $subject})
        RETURN t.name as name, 
                t.statement as statement, 
                t.type as type, 
                t.proof as proof
        ORDER BY t.name
        LIMIT $limit
        """
        result = neo4j_graph.query(query, params={'subject': subject, 'limit': limit})
        return result

def get_theorems_by_domain(domain: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
        MATCH (t:Theorem)-[:BELONGS_TO_DOMAIN]->(s:Domain {name: $domain})
        RETURN t.name as name, 
                t.statement as statement, 
                t.type as type, 
                t.proof as proof
        ORDER BY t.name
        LIMIT $limit
        """
        result = neo4j_graph.query(query, params={'subject': domain, 'limit': limit})
        return result

#add here some more get

