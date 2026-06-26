import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'huid_registry')
    PORT = int(os.getenv('PORT', 5001))  # Changed to 5001 to avoid port conflicts
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
