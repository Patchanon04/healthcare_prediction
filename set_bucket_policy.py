#!/usr/bin/env python3
"""
สคริปต์ตั้งค่า S3 Bucket Policy เพื่ออนุญาตให้ public read
"""
import os
import sys
import json

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError

def set_bucket_policy():
    """ตั้งค่า bucket policy สำหรับ public read access"""
    
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    print(f"🔧 ตั้งค่า Bucket Policy สำหรับ: {bucket_name}")
    print()
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    # Bucket Policy ที่อนุญาตให้ public read
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
    
    try:
        # ปิด Block Public Access ก่อน
        print("⚙️  ปิด Block Public Access...")
        try:
            s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            print("✅ ปิด Block Public Access สำเร็จ")
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                print("⚠️  ไม่มีสิทธิ์แก้ไข Public Access Block")
                print("   กรุณาแก้ไขใน AWS Console")
            else:
                raise
        
        # ตั้งค่า Bucket Policy
        print(f"\n⚙️  ตั้งค่า Bucket Policy...")
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        print(f"✅ ตั้งค่า Bucket Policy สำเร็จ!")
        print()
        print(f"📝 Policy:")
        print(json.dumps(bucket_policy, indent=2))
        print()
        print(f"✅ ไฟล์ใน bucket '{bucket_name}' สามารถเข้าถึงแบบ public ได้แล้ว")
        print(f"   ตัวอย่าง URL: https://{bucket_name}.s3.amazonaws.com/dog_images/test.jpg")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print(f"❌ ไม่มีสิทธิ์ตั้งค่า Bucket Policy")
            print(f"   IAM User ต้องมี permission: s3:PutBucketPolicy")
        else:
            print(f"❌ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    set_bucket_policy()
