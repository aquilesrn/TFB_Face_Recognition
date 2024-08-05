import os
from dotenv import load_dotenv
import redis

# Load environment variables from .env file
load_dotenv()

class Config:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "recognition")
    POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
    
    # Redis configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    redis_instance = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

    # MinIO configuration
    # MINIO_SERVER = os.getenv("MINIO_SERVER", "minio-server:9000")
    # MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
    # MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
    # MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "dataset-s3-bucket")

    # minio_client = Minio(
    #     MINIO_SERVER,
    #     access_key=MINIO_ACCESS_KEY,
    #     secret_key=MINIO_SECRET_KEY,
    #     secure=False
    #)