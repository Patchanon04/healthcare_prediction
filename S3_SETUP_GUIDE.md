# 🪣 คู่มือการตั้งค่า AWS S3 สำหรับ Dog Breed Prediction

## 📋 ขั้นตอนการตั้งค่า S3 Bucket

### **ขั้นตอนที่ 1: สร้าง S3 Bucket**

1. เข้า **AWS Console**: https://console.aws.amazon.com/s3/
2. คลิก **"Create bucket"**
3. ตั้งค่าตามนี้:

   ```
   Bucket name: dogbreed-images
   AWS Region: us-east-1 (หรือ region ที่ใกล้ที่สุด)
   
   Object Ownership: 
   ✅ ACLs enabled
   ✅ Object writer
   
   Block Public Access settings:
   ⚠️ UNCHECK "Block all public access" 
   (เพื่อให้สามารถแสดงรูปภาพได้)
   ✅ Check: "I acknowledge that the current settings..."
   
   Bucket Versioning: Disabled (หรือ Enable ถ้าต้องการ)
   
   Default encryption: 
   ✅ Server-side encryption with Amazon S3 managed keys (SSE-S3)
   ```

4. คลิก **"Create bucket"**

---

### **ขั้นตอนที่ 2: ตั้งค่า Bucket Policy (สำคัญ!)**

1. เข้าไปที่ bucket `dogbreed-images`
2. ไปที่แท็บ **"Permissions"**
3. เลื่อนลงมาที่ **"Bucket policy"**
4. คลิก **"Edit"**
5. วางโค้ดนี้:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::dogbreed-images/*"
        }
    ]
}
```

6. คลิก **"Save changes"**

---

### **ขั้นตอนที่ 3: สร้าง IAM User และ Access Keys**

#### **3.1 สร้าง IAM User:**

1. ไปที่ **IAM Console**: https://console.aws.amazon.com/iam/
2. เลือก **"Users"** จากเมนูซ้าย
3. คลิก **"Create user"**
4. ตั้งค่า:
   ```
   User name: dogbreed-app-user
   ```
5. คลิก **"Next"**

#### **3.2 ตั้งค่า Permissions:**

**Option 1: ใช้ Policy ที่มีอยู่ (ง่ายกว่า)**
1. เลือก **"Attach policies directly"**
2. ค้นหา: `AmazonS3FullAccess`
3. ✅ เลือก policy นี้
4. คลิก **"Next"** → **"Create user"**

**Option 2: สร้าง Custom Policy (ปลอดภัยกว่า - แนะนำ)**
1. เลือก **"Attach policies directly"**
2. คลิก **"Create policy"**
3. เลือกแท็บ **"JSON"**
4. วางโค้ดนี้:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::dogbreed-images",
                "arn:aws:s3:::dogbreed-images/*"
            ]
        }
    ]
}
```

5. คลิก **"Next"**
6. ตั้งชื่อ Policy: `DogBreedS3Access`
7. คลิก **"Create policy"**
8. กลับไปหน้าสร้าง user แล้วเลือก policy ที่เพิ่งสร้าง

#### **3.3 สร้าง Access Keys:**

1. เข้าไปที่ user **dogbreed-app-user** ที่เพิ่งสร้าง
2. เลือกแท็บ **"Security credentials"**
3. เลื่อนลงมาที่ **"Access keys"**
4. คลิก **"Create access key"**
5. เลือก: **"Application running outside AWS"**
6. คลิก **"Next"**
7. ใส่ Description: `Dog Breed Prediction App`
8. คลิก **"Create access key"**

9. **⚠️ สำคัญมาก:**
   - บันทึก **Access key ID** 
   - บันทึก **Secret access key**
   - ⚠️ Secret key จะแสดงครั้งเดียว! ถ้าปิดหน้าต่างจะไม่เห็นอีก
   - คลิก **"Download .csv file"** เพื่อเก็บไว้

---

### **ขั้นตอนที่ 4: ตั้งค่าใน Project**

#### **4.1 สร้างไฟล์ `.env`:**

```bash
# ถ้ายังไม่มีไฟล์ .env
cp .env.example .env
```

#### **4.2 แก้ไขไฟล์ `.env`:**

เปิดไฟล์ `.env` และแก้ไขส่วนนี้:

```bash
# AWS S3 Configuration (Optional - for production)
USE_S3=True
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE          # ← ใส่ Access Key ของคุณ
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/... # ← ใส่ Secret Key ของคุณ
AWS_STORAGE_BUCKET_NAME=dogbreed-images
AWS_S3_REGION_NAME=us-east-1
```

**⚠️ แทนที่:**
- `AKIAIOSFODNN7EXAMPLE` → Access Key ID ที่ได้จาก AWS
- `wJalrXUtnFEMI/K7MDENG/...` → Secret Access Key ที่ได้จาก AWS

#### **4.3 บันทึกไฟล์และ Restart Backend:**

```bash
# Restart backend service
docker-compose restart backend

# ดู logs เพื่อตรวจสอบ
docker-compose logs -f backend
```

---

### **ขั้นตอนที่ 5: ทดสอบการ Upload**

1. เปิดเว็บแอป: **http://localhost:80**
2. เลือกรูปสุนัขและ Upload
3. ตรวจสอบใน **AWS S3 Console**:
   - เข้าไปที่ bucket `dogbreed-images`
   - ควรเห็นโฟลเดอร์ `dog_images/`
   - ภายในจะมีไฟล์รูปที่ upload

4. URL ของรูปจะเป็นแบบนี้:
   ```
   https://dogbreed-images.s3.amazonaws.com/dog_images/1697712345_mydog.jpg
   ```

---

## ✅ **Checklist การตั้งค่า**

- [ ] สร้าง S3 bucket ชื่อ `dogbreed-images`
- [ ] ตั้งค่า Bucket Policy (อนุญาตให้ public read)
- [ ] สร้าง IAM user `dogbreed-app-user`
- [ ] สร้าง Access Keys และบันทึกไว้
- [ ] แก้ไขไฟล์ `.env` ใส่ credentials
- [ ] Restart backend service
- [ ] ทดสอบ upload รูป
- [ ] ตรวจสอบไฟล์ใน S3

---

## 🔒 **ความปลอดภัย**

### **ข้อควรระวัง:**

1. **ห้าม commit `.env` เข้า git**
   - ไฟล์ `.env` อยู่ใน `.gitignore` แล้ว
   - ตรวจสอบก่อน push ทุกครั้ง

2. **ไม่แชร์ Secret Keys**
   - ห้ามส่ง Access Keys ผ่านช่องทางไม่ปลอดภัย
   - ห้าม commit ลง git

3. **ใช้ IAM User ที่มี Permission จำกัด**
   - ไม่ใช้ Root Account
   - จำกัด Permission เฉพาะที่จำเป็น

4. **Enable Encryption**
   - S3 Server-side encryption เปิดไว้แล้ว
   - ข้อมูลจะถูก encrypt automatically

---

## 💰 **ค่าใช้จ่าย**

### **AWS Free Tier (12 เดือนแรก):**
- ✅ 5 GB Standard Storage
- ✅ 20,000 GET Requests
- ✅ 2,000 PUT Requests
- ✅ 100 GB Data Transfer Out

### **ราคาหลัง Free Tier:**
- **Storage**: ~$0.023/GB/เดือน
- **Requests**: 
  - PUT: $0.005/1,000 requests
  - GET: $0.0004/1,000 requests
- **Data Transfer**: 
  - ฟรีสำหรับ 100 GB แรก/เดือน
  - $0.09/GB หลังจากนั้น

**ตัวอย่างการใช้งาน:**
- 1,000 รูป (ขนาดเฉลี่ย 2 MB) = 2 GB
- ค่าใช้จ่าย: ~$0.05/เดือน (ถูกมาก!)

---

## 🐛 **การแก้ปัญหา**

### **ปัญหา: Upload ไม่ผ่าน**

```bash
# 1. ตรวจสอบ logs
docker-compose logs backend

# 2. ตรวจสอบ credentials ใน .env
cat .env | grep AWS

# 3. ทดสอบ AWS credentials
docker-compose exec backend python manage.py shell
>>> import boto3
>>> s3 = boto3.client('s3')
>>> s3.list_buckets()
```

### **ปัญหา: ไม่สามารถเข้าถึงรูปภาพได้**

1. ตรวจสอบ Bucket Policy ว่าอนุญาต public read แล้ว
2. ตรวจสอบ Block Public Access ว่าปิดแล้ว
3. ลองเข้า URL โดยตรง:
   ```
   https://dogbreed-images.s3.amazonaws.com/dog_images/<filename>
   ```

### **ปัญหา: Access Denied**

1. ตรวจสอบ IAM permissions
2. ตรวจสอบ Access Keys ถูกต้อง
3. ตรวจสอบ bucket name ถูกต้อง

---

## 📚 **เอกสารเพิ่มเติม**

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Django Storages Documentation](https://django-storages.readthedocs.io/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

## 🎯 **สรุป**

หลังจากตั้งค่าเสร็จแล้ว:

1. ✅ รูปภาพจะถูก upload ไปเก็บที่ S3
2. ✅ URL จะเป็น `https://dogbreed-images.s3.amazonaws.com/...`
3. ✅ ไม่ต้องเก็บรูปใน server (ประหยัดพื้นที่)
4. ✅ รองรับ traffic สูง (S3 รับได้ไม่จำกัด)
5. ✅ มี CDN ในตัว (โหลดเร็ว)

**พร้อมใช้งาน Production แล้ว! 🚀**
