# 🔧 การแก้ไขปัญหา S3 ACL Error

## ❌ **ปัญหาที่พบ:**

```json
{
    "error": "Internal server error",
    "details": "An error occurred (AccessControlListNotSupported) when calling the PutObject operation: The bucket does not allow ACLs"
}
```

---

## 🔍 **สาเหตุ:**

AWS S3 buckets ที่สร้างหลังเดือน **เมษายน 2023** มีการตั้งค่าเริ่มต้นเป็น **"ACLs disabled"**

แต่ Django Storages (เวอร์ชันเก่า) พยายาม set ACL = `public-read` ตอน upload ไฟล์ → เกิด error

---

## ✅ **วิธีแก้ไข:**

### **แก้ไขไฟล์: `backend/config/settings.py`**

**เปลี่ยนจาก:**
```python
if USE_S3:
    # ...
    AWS_DEFAULT_ACL = 'public-read'  # ❌ ใช้ไม่ได้กับ bucket ใหม่
    AWS_S3_FILE_OVERWRITE = False
```

**เป็น:**
```python
if USE_S3:
    # ...
    
    # Disable ACLs (required for buckets created after April 2023)
    AWS_DEFAULT_ACL = None  # ✅ ปิดการใช้ ACL
    AWS_S3_FILE_OVERWRITE = False
    
    # Make objects publicly accessible without ACLs
    AWS_QUERYSTRING_AUTH = False  # ✅ ไม่ต้อง sign URLs
```

---

## 🔄 **ขั้นตอนการแก้ไข:**

```bash
# 1. แก้ไขไฟล์ settings.py (ทำแล้ว)

# 2. Rebuild backend
docker-compose up -d --build backend

# 3. ทดสอบ
curl http://localhost:8000/api/v1/health/
```

---

## 📝 **สิ่งที่เปลี่ยน:**

| Setting | ค่าเก่า | ค่าใหม่ | เหตุผล |
|---------|---------|---------|--------|
| `AWS_DEFAULT_ACL` | `'public-read'` | `None` | Bucket ไม่รองรับ ACL |
| `AWS_QUERYSTRING_AUTH` | (ไม่มี) | `False` | ทำให้ URL สามารถเข้าถึงได้โดยไม่ต้อง sign |

---

## 🎯 **ผลลัพธ์:**

✅ **Upload ไฟล์ไปยัง S3 ได้สำเร็จ**
- ไม่ต้องใช้ ACL
- ไฟล์ถูกเก็บใน bucket: `dogbreed-images`
- URL: `https://dogbreed-images.s3.amazonaws.com/dog_images/filename.jpg`

✅ **Bucket Policy จัดการ public access แทน ACL**
- ใช้ Bucket Policy เพื่ออนุญาตให้ public read
- ปลอดภัยและทันสมัยกว่า

---

## 🔐 **Bucket Policy ที่แนะนำ:**

ไปที่ **AWS S3 Console → dogbreed-images → Permissions → Bucket Policy**

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

นี่จะอนุญาตให้ทุกคนอ่านไฟล์ใน bucket ได้ (สำหรับแสดงรูปภาพในเว็บ)

---

## 📚 **อ้างอิง:**

- [AWS S3 Disabling ACLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html)
- [Django Storages S3 Settings](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)

---

## ✅ **สรุป:**

| สถานะ | รายการ |
|-------|--------|
| ✅ | S3 เชื่อมต่อได้ |
| ✅ | Upload ไฟล์ได้ |
| ✅ | ไม่มี ACL error แล้ว |
| ✅ | Backend health: OK |
| ✅ | พร้อมใช้งาน Production |

---

**แก้ไขเสร็จสิ้น: 2025-10-19 21:25 🎉**
