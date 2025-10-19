# 🚀 AWS EC2 Deployment - Quick Start

## 📦 **ไฟล์ที่เตรียมไว้สำหรับ Deploy:**

| ไฟล์ | คำอธิบาย |
|------|----------|
| `EC2_DEPLOYMENT_GUIDE.md` | 📚 คู่มือ deploy แบบละเอียด (ภาษาไทย) |
| `EC2_QUICK_DEPLOY.txt` | ⚡ Quick reference สั้นๆ |
| `deploy-ec2.sh` | 🤖 สคริปต์ deploy อัตโนมัติ |
| `setup-ssl.sh` | 🔐 สคริปต์ตั้งค่า SSL/HTTPS |
| `docker-compose.prod.yml` | 🐋 Docker config สำหรับ production |
| `nginx.conf` | 🌐 Nginx reverse proxy config |

---

## ⚡ **Quick Deploy (3 Steps)**

### **1. สร้าง EC2 Instance:**
- **Type:** t3.medium หรือ t3.large
- **OS:** Ubuntu 22.04 LTS
- **Storage:** 30 GB
- **Security Group:** เปิด ports 22, 80, 443, 8000, 5001

### **2. Upload Project:**
```bash
# จาก local machine:
cd /Users/emperor/Desktop/Xtax
scp -i your-key.pem -r MLOPs ubuntu@<EC2-IP>:~/
```

### **3. Run Deploy Script:**
```bash
# SSH เข้า EC2:
ssh -i your-key.pem ubuntu@<EC2-IP>

# Run script:
cd ~/MLOPs
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

**Done!** เปิด `http://<EC2-IP>` ใน browser

---

## 📋 **Pre-deployment Checklist:**

- [ ] มี AWS Account
- [ ] สร้าง S3 bucket: `dogbreed-images` แล้ว
- [ ] มี AWS credentials (Access Key + Secret)
- [ ] มี EC2 key pair (.pem file)
- [ ] ตั้งค่า Security Group แล้ว
- [ ] เตรียม strong passwords

---

## 🔐 **ตั้งค่า SSL/HTTPS (Optional):**

```bash
# SSH เข้า EC2
ssh -i your-key.pem ubuntu@<EC2-IP>

# Run SSL setup
cd ~/MLOPs
sudo ./setup-ssl.sh yourdomain.com
```

---

## 📚 **เอกสารเพิ่มเติม:**

### **คู่มือหลัก:**
- `EC2_DEPLOYMENT_GUIDE.md` - อ่านก่อนสำหรับ deployment แบบละเอียด

### **Quick References:**
- `EC2_QUICK_DEPLOY.txt` - สำหรับอ้างอิงเร็ว
- `README.md` - คู่มือหลักของ project

### **Configuration Files:**
- `docker-compose.yml` - สำหรับ development
- `docker-compose.prod.yml` - สำหรับ production  
- `nginx.conf` - Nginx reverse proxy
- `.env.example` - Template สำหรับ environment variables

---

## 🎯 **Architecture บน EC2:**

```
Internet
   │
   ├─→ Port 80/443 (Nginx - Optional)
   │      │
   │      ├─→ Frontend (Vue.js) - Port 80
   │      └─→ Backend API - Port 8000
   │             │
   │             ├─→ ML Service - Port 5001
   │             └─→ PostgreSQL - Port 5432
   │
   └─→ S3 (dogbreed-images)
```

---

## 💰 **ค่าใช้จ่ายประมาณ:**

### **t3.medium (แนะนำสำหรับเริ่มต้น):**
- EC2 instance: ~$30/month
- Storage: ~$3/month
- Data transfer: ~$9/month
- **Total: ~$42/month**

### **t3.large (สำหรับ traffic สูง):**
- EC2 instance: ~$60/month
- Storage: ~$3/month  
- Data transfer: ~$9/month
- **Total: ~$72/month**

### **S3 Storage:**
- 2 GB: ~$0.05/month (ถูกมาก!)

---

## 🔧 **Useful Commands:**

```bash
# View all logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update application
git pull
docker-compose build
docker-compose up -d

# Check resource usage
docker stats
htop

# Check disk space
df -h
```

---

## 🚨 **Troubleshooting:**

### **Cannot connect to EC2:**
→ Check Security Group allows port 22 from your IP

### **Services not starting:**
→ Check logs: `docker-compose logs`
→ Check disk space: `df -h`

### **Frontend blank page:**
→ Check CORS settings in `.env`
→ Check `VUE_APP_API_URL`

### **Cannot upload images:**
→ Check AWS credentials in `.env`
→ Check S3 bucket permissions

---

## 📞 **Support:**

- **Full Guide:** อ่าน `EC2_DEPLOYMENT_GUIDE.md`
- **Quick Help:** ดู `EC2_QUICK_DEPLOY.txt`
- **Local Development:** ดู `README.md` และ `QUICKSTART.md`

---

## ✅ **Next Steps After Deployment:**

1. **Test Upload:** ลองอัพโหลดรูปสุนัข
2. **Setup Domain:** ถ้ามี domain name
3. **Enable SSL:** รัน `setup-ssl.sh` สำหรับ HTTPS
4. **Setup Monitoring:** CloudWatch, logs
5. **Backup Database:** ตั้งค่า automated backups
6. **Security Review:** ตรวจสอบ Security Groups

---

**🎉 Happy Deploying!**
