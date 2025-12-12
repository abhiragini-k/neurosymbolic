import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

def check_mongo_connection():
    # Load environment variables from .env file
    load_dotenv()

    mongo_url = os.getenv("MONGODB_URL")
    if not mongo_url:
        print("Error: MONGODB_URL not found in environment variables.")
        return

    print(f"Attempting to connect to MongoDB...")
    
    try:
        # Create a client
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        
        print("Successfully connected to MongoDB!")
        
        # Print server info
        server_info = client.server_info()
        print(f"Server version: {server_info.get('version')}")
        
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    check_mongo_connection()
