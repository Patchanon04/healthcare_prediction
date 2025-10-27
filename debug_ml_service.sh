#!/bin/bash
# สคริปต์ debug ML Service

echo "=================================================="
echo "🔍 ML Service Debug Report"
echo "=================================================="

echo ""
echo "1️⃣ Container Status:"
docker ps --filter "name=ml_service" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "2️⃣ Health Check:"
curl -s http://localhost:5001/health/ | python3 -m json.tool

echo ""
echo "3️⃣ Startup Logs (last 100 lines):"
echo "=================================================="
docker logs medml_ml_service --tail 100

echo ""
echo "=================================================="
echo "4️⃣ Looking for errors:"
echo "=================================================="
docker logs medml_ml_service 2>&1 | grep -i "error\|exception\|failed\|warning" | tail -20

echo ""
echo "=================================================="
echo "5️⃣ Environment Variables in Container:"
echo "=================================================="
docker exec medml_ml_service env | grep -E "AWS|MODEL"

echo ""
echo "=================================================="
echo "6️⃣ Python/TensorFlow versions in Container:"
echo "=================================================="
docker exec medml_ml_service python -c "import sys; print(f'Python: {sys.version}')"
docker exec medml_ml_service python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')" 2>&1 || echo "TensorFlow import failed"
docker exec medml_ml_service python -c "import boto3; print(f'Boto3: {boto3.__version__}')"

echo ""
echo "=================================================="
echo "7️⃣ Test S3 Connection from Container:"
echo "=================================================="
docker exec medml_ml_service python -c "
import boto3
import os
try:
    s3 = boto3.client('s3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    )
    bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')
    s3.head_bucket(Bucket=bucket)
    print(f'✅ S3 connection OK: {bucket}')
except Exception as e:
    print(f'❌ S3 connection failed: {e}')
"

echo ""
echo "=================================================="
echo "💡 Recommendations:"
echo "=================================================="
echo "If you see 'models_not_loaded', check the errors above."
echo "Common issues:"
echo "  1. AWS credentials not set in container"
echo "  2. Protobuf version mismatch"
echo "  3. TensorFlow import error"
echo "  4. S3 connection failed"
echo ""
echo "To rebuild with new requirements.txt:"
echo "  docker-compose build ml_service"
echo "  docker-compose up -d ml_service"
