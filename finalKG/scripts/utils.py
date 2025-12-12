import os
from dotenv import load_dotenv

# Load .env file explicitly from the parent directory
# This assumes utils.py is in /scripts/ and .env is in /
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

def get_env_variable(var_name: str, default: str = None, required: bool = True) -> str:
    """
    Retrieves an environment variable.
    Raises ValueError if required and not found.
    """
    value = os.getenv(var_name, default)
    if required and value is None:
        raise ValueError(f"Environment variable '{var_name}' is missing. Please check your .env file.")
    return value

def get_neo4j_driver():
    """
    Returns a configured Neo4j driver based on .env variables.
    """
    from neo4j import GraphDatabase
    
    uri = get_env_variable("NEO4J_URI")
    user = get_env_variable("NEO4J_USER")
    password = get_env_variable("NEO4J_PASS")
    
    return GraphDatabase.driver(uri, auth=(user, password))
