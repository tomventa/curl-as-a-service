from pymongo.collection import Collection
from pymongo import MongoClient
from fastapi.logger import logger
import os
import secrets

# Configuration used to connect to MongoDB
config = {
  'host': os.environ['MONGO_HOST'],
  'port': 27017,
  'user': os.environ['MONGO_USERNAME'],
  'password': os.environ['MONGO_PASSWORD'],
  'database': os.environ['MONGO_DB_NAME']
}

client = MongoClient(
  config['host'],
  config['port'],
  username=config['user'],
  password=config['password']
)

def get_db():
  """Return the MongoDb database instance
  """
  db = client[config['database']]
  return db