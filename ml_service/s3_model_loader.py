"""
S3 Model Loader for downloading and caching ML models from AWS S3
"""
import os
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class S3ModelLoader:
    """Load models from S3 with local caching"""
    
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        region_name: str = "us-east-1",
        cache_dir: str = "/tmp/models"
    ):
        """
        Initialize S3 Model Loader
        
        Args:
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key (optional, uses env vars if not provided)
            aws_secret_access_key: AWS secret key (optional, uses env vars if not provided)
            region_name: AWS region
            cache_dir: Local directory to cache downloaded models
        """
        self.bucket_name = bucket_name
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=region_name or os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
        )
        
        logger.info(f"S3ModelLoader initialized with bucket: {bucket_name}")
    
    def download_model(self, s3_key: str, force_download: bool = False) -> Path:
        """
        Download model from S3 to local cache
        
        Args:
            s3_key: S3 object key (path in bucket)
            force_download: Force re-download even if cached
            
        Returns:
            Path to downloaded model file
        """
        # Create local file path
        local_path = self.cache_dir / s3_key.replace('/', '_')
        
        # Check if already cached
        if local_path.exists() and not force_download:
            logger.info(f"Model found in cache: {local_path}")
            return local_path
        
        # Download from S3
        try:
            logger.info(f"Downloading model from s3://{self.bucket_name}/{s3_key}")
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                str(local_path)
            )
            logger.info(f"Model downloaded successfully to {local_path}")
            return local_path
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise FileNotFoundError(f"Model not found in S3: s3://{self.bucket_name}/{s3_key}")
            else:
                raise Exception(f"Error downloading model from S3: {e}")
    
    def list_models(self, prefix: str = "") -> list:
        """
        List all models in S3 bucket with given prefix
        
        Args:
            prefix: S3 key prefix to filter models
            
        Returns:
            List of S3 object keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
            
        except ClientError as e:
            logger.error(f"Error listing models from S3: {e}")
            return []
    
    def upload_model(self, local_path: str, s3_key: str) -> bool:
        """
        Upload model to S3
        
        Args:
            local_path: Local file path
            s3_key: S3 object key (destination path in bucket)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Uploading model to s3://{self.bucket_name}/{s3_key}")
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key
            )
            logger.info(f"Model uploaded successfully")
            return True
            
        except ClientError as e:
            logger.error(f"Error uploading model to S3: {e}")
            return False
