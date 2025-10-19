# 🚀 คู่มือ Deploy Dog Breed Prediction บน AWS EC2

## 📋 ภาพรวม

คู่มือนี้จะแนะนำการ deploy ระบบ Dog Breed Prediction แบบเต็มรูปแบบบน AWS EC2

---

## 🎯 **สถาปัตยกรรม**

```
                     Internet
                        |
                   [Route 53]
                        |
                  [Load Balancer] (Optional)
                        |
        +---------------+---------------+
        |                               |
    [EC2 Instance]                [RDS PostgreSQL]
        |                         (Optional - แทน Docker DB)
        |
    +---+---+---+---+
    |   |   |   |   |
  Frontend Backend ML S3
  (Port 80) (8000) (5001) (Storage)
```

---

## 📦 **สิ่งที่ต้องเตรียม**

### **1. AWS Account**
- ✅ มี AWS Account พร้อม payment method
- ✅ มี IAM User หรือ Root access

### **2. EC2 Instance Specifications (แนะนำ)**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Instance Type | t3.medium | t3.large |
| vCPU | 2 | 2-4 |
| RAM | 4 GB | 8 GB |
| Storage | 20 GB | 30-50 GB |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |

### **3. Domain (Optional)**
- ถ้าต้องการใช้ domain name
- ตั้งค่า DNS ใน Route 53 หรือ external provider

---

## 🛠️ **ขั้นตอนการ Deploy**

### **Step 1: สร้าง EC2 Instance**

#### **1.1 เข้า EC2 Console:**
https://console.aws.amazon.com/ec2/

#### **1.2 คลิก "Launch Instance"**

#### **1.3 ตั้งค่า Instance:**

**Name and tags:**
```
Name: dogbreed-prediction-server
```

**Application and OS Images:**
```
AMI: Ubuntu Server 22.04 LTS (HVM)
Architecture: 64-bit (x86)
```

**Instance type:**
```
Minimum: t3.medium (2 vCPU, 4 GB RAM) - ~$30/month
Recommended: t3.large (2 vCPU, 8 GB RAM) - ~$60/month
```

**Key pair:**
```
Create new key pair:
- Name: dogbreed-prediction-key
- Type: RSA
- Format: .pem (for macOS/Linux) or .ppk (for Windows)
- Download และเก็บไว้ให้ปลอดภัย!
```

**Network settings:**
```
✅ Create security group
✅ Allow SSH from: My IP
✅ Allow HTTP (port 80) from: Anywhere
✅ Allow HTTPS (port 443) from: Anywhere (ถ้าใช้ SSL)
✅ Custom TCP (port 8000) from: Anywhere (Backend API)
✅ Custom TCP (port 5001) from: Anywhere (ML Service - optional)
```

**Configure storage:**
```
Volume 1: 30 GB gp3
```

**Advanced details:**
```
(ไม่ต้องแก้อะไร)
```

#### **1.4 คลิก "Launch Instance"**

รอ 2-3 นาที instance จะพร้อมใช้งาน

---

### **Step 2: เชื่อมต่อ EC2 Instance**

#### **2.1 ดู Public IP:**
- เข้า EC2 Console → Instances
- คัดลอก "Public IPv4 address"

#### **2.2 SSH เข้า Instance:**

**macOS/Linux:**
```bash
# เปลี่ยน permission ของ key file
chmod 400 dogbreed-prediction-key.pem

# SSH เข้า instance
ssh -i dogbreed-prediction-key.pem ubuntu@<PUBLIC_IP>
```

**Windows (PowerShell):**
```powershell
ssh -i dogbreed-prediction-key.pem ubuntu@<PUBLIC_IP>
```

---

### **Step 3: ติดตั้ง Dependencies บน EC2**

หลัง SSH เข้าสู่ instance แล้ว รันคำสั่งเหล่านี้:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# ติดตั้ง Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# ติดตั้ง Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# ติดตั้ง Git
sudo apt install git -y

# ติดตั้ง utilities
sudo apt install htop vim curl wget -y

# Logout และ login ใหม่เพื่อให้ Docker permissions มีผล
exit
```

**Login ใหม่:**
```bash
ssh -i dogbreed-prediction-key.pem ubuntu@<PUBLIC_IP>
```

**ตรวจสอบ:**
```bash
docker --version
docker-compose --version
```

---

### **Step 4: Clone Project และ Setup**

```bash
# Clone repository (เปลี่ยน URL ถ้ามี)
cd ~
git clone https://github.com/yourusername/MLOPs.git
cd MLOPs

# หรือถ้าไม่มี git repo ให้ใช้ scp upload จาก local:
# scp -i dogbreed-prediction-key.pem -r MLOPs ubuntu@<PUBLIC_IP>:~/
```

---

### **Step 5: ตั้งค่า Environment Variables**

```bash
# สร้างไฟล์ .env
cp .env.example .env

# แก้ไขไฟล์ .env
nano .env
```

**ใส่ค่าเหล่านี้:**
```bash
# Database Configuration
POSTGRES_DB=dogbreed_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE  # เปลี่ยน!

# Django Configuration
DJANGO_SECRET_KEY=YOUR_DJANGO_SECRET_KEY_HERE  # เปลี่ยน! (generate ใหม่)
DEBUG=False  # สำคัญ! ปิด debug mode
ALLOWED_HOSTS=<EC2_PUBLIC_IP>,yourdomain.com

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://<EC2_PUBLIC_IP>,https://yourdomain.com

# AWS S3 Configuration
USE_S3=True
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY
AWS_STORAGE_BUCKET_NAME=dogbreed-images
AWS_S3_REGION_NAME=us-east-1

# ML Service Configuration
ML_SERVICE_URL=http://ml_service:5000
ML_SERVICE_TIMEOUT=30
ML_SERVICE_MAX_RETRIES=3

# Frontend Configuration
VUE_APP_API_URL=http://<EC2_PUBLIC_IP>:8000
```

**บันทึกไฟล์:** `Ctrl + X` → `Y` → `Enter`

---

### **Step 6: Generate Django Secret Key**

```bash
# Generate new secret key
docker run --rm python:3.11 python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# คัดลอก output แล้วใส่ใน .env
```

---

### **Step 7: Build และ Start Services**

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# ดู logs
docker-compose logs -f
```

รอประมาณ 2-3 นาที สำหรับ services ทั้งหมดเริ่มต้น

---

### **Step 8: Run Database Migrations**

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser (สำหรับ Django admin)
docker-compose exec backend python manage.py createsuperuser
```

---

### **Step 9: ตรวจสอบ Services**

```bash
# เช็คว่า containers ทำงาน
docker-compose ps

# เช็ค health
curl http://localhost:8000/api/v1/health/

# เช็ค frontend
curl http://localhost:80
```

---

### **Step 10: ทดสอบจาก Browser**

เปิด browser และไปที่:

```
Frontend:  http://<EC2_PUBLIC_IP>
Backend:   http://<EC2_PUBLIC_IP>:8000/api/v1/
ML Docs:   http://<EC2_PUBLIC_IP>:5001/docs
```

---

## 🔐 **Security Best Practices**

### **1. Security Group Rules**

แนะนำให้ปิด port ที่ไม่จำเป็น:

```
✅ Port 22 (SSH): เฉพาะ My IP
✅ Port 80 (HTTP): 0.0.0.0/0
✅ Port 443 (HTTPS): 0.0.0.0/0
❌ Port 8000: ปิด (ใช้ผ่าน reverse proxy)
❌ Port 5001: ปิด (ใช้ผ่าน reverse proxy)
❌ Port 5432: ปิด (ใช้ internal network)
```

### **2. ใช้ Nginx เป็น Reverse Proxy**

สร้างไฟล์: `nginx.conf`

```nginx
server {
    listen 80;
    server_name <YOUR_DOMAIN_OR_IP>;
    
    client_max_body_size 10M;
    
    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # ML Service (optional - ถ้าต้องการเปิด)
    location /ml/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **3. ตั้งค่า SSL/HTTPS (แนะนำ)**

```bash
# ติดตั้ง Certbot
sudo apt install certbot python3-certbot-nginx -y

# ขอ SSL certificate
sudo certbot --nginx -d yourdomain.com
```

---

## 📊 **Monitoring และ Logging**

### **1. ดู Logs:**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ml_service

# Last 100 lines
docker-compose logs --tail=100
```

### **2. System Resources:**

```bash
# CPU, Memory usage
htop

# Docker stats
docker stats

# Disk usage
df -h
```

### **3. ตั้งค่า CloudWatch (Optional):**

- ติดตั้ง CloudWatch agent
- Monitor CPU, Memory, Disk
- ตั้ง alarms สำหรับ high usage

---

## 🔄 **Auto-start on Reboot**

สร้างไฟล์ systemd service:

```bash
sudo nano /etc/systemd/system/dogbreed.service
```

**เนื้อหา:**
```ini
[Unit]
Description=Dog Breed Prediction Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/MLOPs
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
```

**Enable service:**
```bash
sudo systemctl enable dogbreed.service
sudo systemctl start dogbreed.service
```

---

## 🔧 **การ Update Application**

```bash
# SSH เข้า EC2
ssh -i dogbreed-prediction-key.pem ubuntu@<PUBLIC_IP>

# ไปที่ project directory
cd ~/MLOPs

# Pull latest code (ถ้าใช้ Git)
git pull

# Rebuild และ restart
docker-compose down
docker-compose build
docker-compose up -d

# Run migrations (ถ้ามี)
docker-compose exec backend python manage.py migrate
```

---

## 💰 **ค่าใช้จ่าย (ประมาณการ)**

| Resource | Specification | ราคา/เดือน |
|----------|--------------|------------|
| EC2 t3.medium | 2 vCPU, 4GB RAM | ~$30 |
| EBS Storage | 30 GB gp3 | ~$3 |
| Data Transfer | 100 GB/month | ~$9 |
| **รวม** | | **~$42/month** |

### **ถ้าใช้ RDS แทน Docker PostgreSQL:**
| Resource | Specification | ราคา/เดือน |
|----------|--------------|------------|
| RDS db.t3.micro | 2 vCPU, 1GB RAM | ~$15 |
| Storage | 20 GB | ~$2 |

---

## 🎯 **Optimization Tips**

### **1. ลด Docker Image Size:**
- ใช้ multi-stage builds
- ลบ unnecessary dependencies

### **2. Enable Swap (สำหรับ RAM ต่ำ):**
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### **3. Log Rotation:**
```bash
# Docker log rotation
sudo nano /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

```bash
sudo systemctl restart docker
```

---

## 🚨 **Troubleshooting**

### **ปัญหา: Services ไม่ start**
```bash
# เช็ค logs
docker-compose logs

# เช็ค disk space
df -h

# เช็ค memory
free -h
```

### **ปัญหา: Connection refused**
```bash
# เช็ค security group
# ตรวจสอบว่าเปิด ports ที่จำเป็นแล้ว

# เช็คว่า services listen
sudo netstat -tulpn | grep -E '80|8000|5001'
```

### **ปัญหา: Out of memory**
```bash
# เช็ค memory usage
docker stats

# Restart specific service
docker-compose restart backend
```

---

## ✅ **Checklist การ Deploy**

- [ ] สร้าง EC2 instance เสร็จ
- [ ] ติดตั้ง Docker และ Docker Compose
- [ ] Clone project
- [ ] ตั้งค่า .env ถูกต้อง
- [ ] Build และ start services
- [ ] Run migrations
- [ ] ทดสอบ frontend ทำงาน
- [ ] ทดสอบ backend API ทำงาน
- [ ] ทดสอบ upload รูป → S3
- [ ] ทดสอบ ML prediction
- [ ] ตั้งค่า auto-start on reboot
- [ ] ตั้งค่า SSL (ถ้ามี domain)
- [ ] ตั้งค่า monitoring
- [ ] Backup database

---

## 📚 **Next Steps**

1. **Domain Name:** ซื้อ domain และตั้งค่า DNS
2. **SSL Certificate:** ใช้ Let's Encrypt ฟรี
3. **Load Balancer:** ถ้ามี traffic สูง
4. **Auto Scaling:** ตั้งค่า Auto Scaling Group
5. **RDS:** ใช้ managed database
6. **CloudFront:** CDN สำหรับ S3 images
7. **Monitoring:** CloudWatch, Datadog, New Relic
8. **Backup:** Automated daily backups

---

**🎉 พร้อม Deploy แล้ว! Good luck!**
