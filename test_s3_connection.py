#!/usr/bin/env python3
"""
สคริปต์ทดสอบการเชื่อมต่อ AWS S3
"""
import os
import sys

# เพิ่ม Django settings
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def test_s3_connection():
    """ทดสอบการเชื่อมต่อ S3"""
    
    print("=" * 60)
    print("🔍 ทดสอบการเชื่อมต่อ AWS S3")
    print("=" * 60)
    
    # 1. เช็ค settings
    print(f"\n📋 การตั้งค่า:")
    print(f"   USE_S3: {settings.USE_S3}")
    
    if not settings.USE_S3:
        print("\n❌ S3 ยังไม่ได้เปิดใช้งาน!")
        print("   แก้ไข: เปลี่ยน USE_S3=True ในไฟล์ .env")
        return False
    
    print(f"   Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"   Region: {settings.AWS_S3_REGION_NAME}")
    print(f"   Access Key: {settings.AWS_ACCESS_KEY_ID[:10]}..." if settings.AWS_ACCESS_KEY_ID else "   Access Key: ❌ ไม่มี")
    
    # 2. ทดสอบ credentials
    if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        print("\n❌ ไม่พบ AWS credentials!")
        print("   แก้ไข: ใส่ AWS_ACCESS_KEY_ID และ AWS_SECRET_ACCESS_KEY ในไฟล์ .env")
        return False
    
    # 3. ทดสอบเชื่อมต่อ S3
    print(f"\n🔌 กำลังทดสอบการเชื่อมต่อ...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # ทดสอบ list buckets
        response = s3_client.list_buckets()
        
        print(f"✅ เชื่อมต่อ AWS สำเร็จ!")
        print(f"\n📦 Buckets ที่มีอยู่:")
        for bucket in response['Buckets']:
            indicator = "👉" if bucket['Name'] == settings.AWS_STORAGE_BUCKET_NAME else "  "
            print(f"   {indicator} {bucket['Name']}")
        
        # 4. เช็คว่า bucket ที่ต้องการมีอยู่หรือไม่
        bucket_exists = any(b['Name'] == settings.AWS_STORAGE_BUCKET_NAME for b in response['Buckets'])
        
        if bucket_exists:
            print(f"\n✅ Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' พร้อมใช้งาน!")
            
            # ทดสอบ permissions
            try:
                s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
                print(f"✅ สามารถเข้าถึง bucket ได้")
                
                # ลอง list objects
                try:
                    objects = s3_client.list_objects_v2(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        MaxKeys=5
                    )
                    
                    if 'Contents' in objects:
                        print(f"✅ สามารถอ่านไฟล์ใน bucket ได้")
                        print(f"   พบไฟล์: {len(objects['Contents'])} ไฟล์")
                    else:
                        print(f"✅ Bucket ว่างเปล่า (ปกติสำหรับการใช้งานครั้งแรก)")
                    
                    print(f"\n🎉 ทุกอย่างพร้อมใช้งาน!")
                    return True
                    
                except ClientError as e:
                    print(f"⚠️  สามารถเข้าถึง bucket ได้ แต่อาจมีปัญหาใน permissions: {e}")
                    return False
                    
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '403':
                    print(f"❌ ไม่มีสิทธิ์เข้าถึง bucket!")
                    print(f"   แก้ไข: ตรวจสอบ IAM permissions")
                else:
                    print(f"❌ Error: {e}")
                return False
        else:
            print(f"\n❌ Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' ไม่มีอยู่!")
            print(f"   แก้ไข: สร้าง bucket ชื่อ '{settings.AWS_STORAGE_BUCKET_NAME}' ใน AWS Console")
            return False
            
    except NoCredentialsError:
        print("❌ AWS credentials ไม่ถูกต้อง!")
        print("   แก้ไข: ตรวจสอบ AWS_ACCESS_KEY_ID และ AWS_SECRET_ACCESS_KEY")
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidAccessKeyId':
            print("❌ AWS Access Key ID ไม่ถูกต้อง!")
        elif error_code == 'SignatureDoesNotMatch':
            print("❌ AWS Secret Access Key ไม่ถูกต้อง!")
        else:
            print(f"❌ Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_s3_connection()
    print("\n" + "=" * 60)
    sys.exit(0 if success else 1)
