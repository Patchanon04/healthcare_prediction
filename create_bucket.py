#!/usr/bin/env python3
"""
สคริปต์สร้าง S3 Bucket
"""
import os
import sys

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError

def create_bucket():
    """สร้าง S3 bucket"""
    
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region = settings.AWS_S3_REGION_NAME
    
    print(f"🪣 กำลังสร้าง bucket: {bucket_name}")
    print(f"📍 Region: {region}")
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=region
    )
    
    try:
        # สร้าง bucket
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✅ สร้าง bucket '{bucket_name}' สำเร็จ!")
        
        # ตั้งค่า Public Access (สำหรับแสดงรูปภาพ)
        print(f"⚙️  กำลังตั้งค่า public access...")
        
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        
        # ตั้งค่า Bucket Policy
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        import json
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        print(f"✅ ตั้งค่า bucket policy สำเร็จ!")
        print(f"\n🎉 Bucket '{bucket_name}' พร้อมใช้งาน!")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"✅ Bucket '{bucket_name}' มีอยู่แล้ว (เป็นของคุณ)")
        elif error_code == 'BucketAlreadyExists':
            print(f"❌ Bucket '{bucket_name}' ถูกใช้โดยคนอื่นแล้ว")
            print(f"   ลองใช้ชื่ออื่น เช่น: dogbreed-images-{region}")
        else:
            print(f"❌ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    create_bucket()
