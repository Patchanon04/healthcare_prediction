#!/usr/bin/env python3
"""
สคริปต์ทดสอบ ensemble predictor
"""
import asyncio
import httpx
from pathlib import Path


async def test_health():
    """ทดสอบ health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:5000/health/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"✅ Models Loaded: {data['models_loaded']}")
            print(f"✅ Version: {data['version']}")
            print("\nModels Info:")
            for model in data['models_info']:
                print(f"  - {model['model_name']}: {model['is_loaded']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")


async def test_prediction_file(image_path: str):
    """ทดสอบ prediction ด้วย file upload"""
    print("\n" + "="*60)
    print("Testing Prediction with File Upload")
    print("="*60)
    
    if not Path(image_path).exists():
        print(f"❌ Image file not found: {image_path}")
        return
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = await client.post(
                "http://localhost:5000/predict/brain-tumor/",
                files=files
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Diagnosis: {data['diagnosis']}")
            print(f"✅ Has Tumor: {data['has_tumor']}")
            print(f"✅ Tumor Probability: {data['tumor_probability']:.4f}")
            print(f"✅ Confidence: {data['confidence']:.4f}")
            print(f"✅ Selected Model: {data['selected_model']}")
            print(f"✅ Processing Time: {data['processing_time']}s")
            print(f"✅ Strategy: {data['strategy']}")
            
            print("\nAll Model Predictions:")
            for pred in data['all_predictions']:
                print(f"  - {pred['model_name']}: {pred['tumor_probability']:.4f} (confidence: {pred['confidence']:.4f})")
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"   {response.text}")


async def test_prediction_url(image_url: str):
    """ทดสอบ prediction ด้วย URL"""
    print("\n" + "="*60)
    print("Testing Prediction with URL")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:5000/predict/brain-tumor-url/",
            json={"image_url": image_url}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Diagnosis: {data['diagnosis']}")
            print(f"✅ Has Tumor: {data['has_tumor']}")
            print(f"✅ Tumor Probability: {data['tumor_probability']:.4f}")
            print(f"✅ Confidence: {data['confidence']:.4f}")
            print(f"✅ Selected Model: {data['selected_model']}")
            print(f"✅ Processing Time: {data['processing_time']}s")
            
            print("\nAll Model Predictions:")
            for pred in data['all_predictions']:
                print(f"  - {pred['model_name']}: {pred['tumor_probability']:.4f}")
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"   {response.text}")


async def main():
    """Main test function"""
    print("="*60)
    print("Brain Tumor Detection ML Service - Test Suite")
    print("="*60)
    
    # Test 1: Health check
    await test_health()
    
    # Test 2: File upload (ถ้ามีไฟล์ทดสอบ)
    test_image = "../Brain-Tumor-Detection1/yes/Y1.jpg"
    if Path(test_image).exists():
        await test_prediction_file(test_image)
    else:
        print(f"\n⚠️  Test image not found: {test_image}")
        print("   Skipping file upload test")
    
    # Test 3: URL-based prediction (ตัวอย่าง)
    # await test_prediction_url("https://example.com/brain-scan.jpg")
    
    print("\n" + "="*60)
    print("Test Suite Completed")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
