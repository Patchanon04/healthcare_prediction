#!/usr/bin/env python3
"""
สคริปต์สำหรับอัพโหลดโมเดล brain tumor ไปยัง S3
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from s3_model_loader import S3ModelLoader
import logging

# Load environment variables from parent directory's .env file
parent_dir = Path(__file__).parent.parent
env_path = parent_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    # Fallback to local .env if exists
    load_dotenv()
    print("⚠️  Using local .env or environment variables")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_brain_tumor_models():
    """อัพโหลดโมเดล brain tumor ทั้ง 2 ชุดไปยัง S3"""
    
    # ตรวจสอบ environment variables
    bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
    if not bucket_name:
        logger.error("AWS_STORAGE_BUCKET_NAME environment variable not set")
        return False
    
    # Initialize S3 loader
    try:
        s3_loader = S3ModelLoader(
            bucket_name=bucket_name,
            region_name=os.getenv("AWS_S3_REGION_NAME", "us-east-1")
        )
        logger.info(f"Connected to S3 bucket: {bucket_name}")
    except Exception as e:
        logger.error(f"Failed to connect to S3: {e}")
        return False
    
    # กำหนด paths
    project_root = Path(__file__).parent.parent
    
    # Model 1 paths (Brain-Tumor-Detection)
    model1_dir = project_root / "Brain-Tumor-Detection"
    model1_json = model1_dir / "model.json"
    model1_h5 = model1_dir / "model.h5"
    
    # Model 2 paths (Brain-Tumor-Detection1)
    model2_dir = project_root / "Brain-Tumor-Detection1" / "models"
    model2_file = model2_dir / "cnn-parameters-improvement-23-0.91.model"
    
    # ตรวจสอบว่าไฟล์มีอยู่
    files_to_upload = [
        (model1_json, "models/brain_tumor/model1/model.json"),
        (model1_h5, "models/brain_tumor/model1/model.h5"),
        (model2_file, "models/brain_tumor/model2/cnn-parameters-improvement-23-0.91.model")
    ]
    
    success_count = 0
    total_count = len(files_to_upload)
    
    for local_path, s3_key in files_to_upload:
        if not local_path.exists():
            logger.warning(f"File not found: {local_path}")
            logger.info(f"Skipping: {s3_key}")
            continue
        
        logger.info(f"\nUploading: {local_path.name}")
        logger.info(f"Size: {local_path.stat().st_size / (1024*1024):.2f} MB")
        logger.info(f"Destination: s3://{bucket_name}/{s3_key}")
        
        try:
            success = s3_loader.upload_model(str(local_path), s3_key)
            if success:
                success_count += 1
                logger.info(f"✅ Uploaded successfully")
            else:
                logger.error(f"❌ Upload failed")
        except Exception as e:
            logger.error(f"❌ Error uploading: {e}")
    
    # สรุปผลลัพธ์
    logger.info("\n" + "="*60)
    logger.info(f"Upload Summary: {success_count}/{total_count} files uploaded")
    logger.info("="*60)
    
    if success_count == total_count:
        logger.info("✅ All models uploaded successfully!")
        return True
    elif success_count > 0:
        logger.warning(f"⚠️  Some models uploaded ({success_count}/{total_count})")
        return True
    else:
        logger.error("❌ No models uploaded")
        return False


def list_uploaded_models():
    """แสดงรายการโมเดลที่อัพโหลดไปยัง S3"""
    
    bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
    if not bucket_name:
        logger.error("AWS_STORAGE_BUCKET_NAME environment variable not set")
        return
    
    try:
        s3_loader = S3ModelLoader(
            bucket_name=bucket_name,
            region_name=os.getenv("AWS_S3_REGION_NAME", "us-east-1")
        )
        
        logger.info("\n" + "="*60)
        logger.info("Models in S3:")
        logger.info("="*60)
        
        models = s3_loader.list_models(prefix="models/brain_tumor/")
        
        if not models:
            logger.info("No models found in S3")
        else:
            for model_key in models:
                logger.info(f"  📦 {model_key}")
        
        logger.info(f"\nTotal: {len(models)} files")
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload brain tumor models to S3")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List models in S3 instead of uploading"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_uploaded_models()
    else:
        logger.info("="*60)
        logger.info("Brain Tumor Models Upload to S3")
        logger.info("="*60)
        
        success = upload_brain_tumor_models()
        
        if success:
            logger.info("\n✅ Upload completed!")
            logger.info("\nYou can now start the ML service:")
            logger.info("  python main.py")
        else:
            logger.error("\n❌ Upload failed!")
            sys.exit(1)
