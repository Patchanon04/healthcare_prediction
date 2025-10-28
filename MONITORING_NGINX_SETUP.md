# 🔐 Nginx Setup for Monitoring Stack

คู่มือการตั้งค่า Nginx เพื่อเข้าถึง Grafana และ Prometheus อย่างปลอดภัย

---

## 🎯 เลือกวิธีการเข้าถึง

### Option 1: Subdomain (แนะนำ) ⭐
- **Grafana**: `https://monitoring.yourdomain.com`
- **Prometheus**: `https://monitoring.yourdomain.com/prometheus/`
- **cAdvisor**: `https://monitoring.yourdomain.com/cadvisor/`

### Option 2: Path Prefix
- **Grafana**: `https://yourdomain.com/grafana/`
- **Prometheus**: `https://yourdomain.com/prometheus/`

---

## 📋 Setup Steps

### 1. สร้าง Basic Auth Password

```bash
# Install apache2-utils (for htpasswd command)
sudo apt-get update
sudo apt-get install -y apache2-utils

# Create password file (replace 'admin' with your username)
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Add more users (without -c flag)
sudo htpasswd /etc/nginx/.htpasswd user2

# Verify
cat /etc/nginx/.htpasswd
```

**Output:**
```
admin:$apr1$xyz...
```

---

### 2. Copy Nginx Config

```bash
# Backup existing config
sudo cp /etc/nginx/sites-available/medical.conf /etc/nginx/sites-available/medical.conf.backup

# Copy new config
sudo cp nginx.conf /etc/nginx/sites-available/medical.conf

# Test config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

---

### 3. Configure DNS (ถ้าใช้ Subdomain)

**Option A: AWS Route 53**
```
Type: A Record
Name: monitoring.yourdomain.com
Value: <your-ec2-public-ip>
TTL: 300
```

**Option B: /etc/hosts (Local testing)**
```bash
# On your local machine
sudo nano /etc/hosts

# Add:
<your-ec2-ip> monitoring.yourdomain.com
```

---

### 4. Update Grafana Config (ถ้าใช้ Path Prefix)

แก้ `docker-compose.monitoring.yml`:

```yaml
grafana:
  environment:
    - GF_SERVER_ROOT_URL=http://yourdomain.com/grafana/
    - GF_SERVER_SERVE_FROM_SUB_PATH=true
```

Restart Grafana:
```bash
docker-compose -f docker-compose.prod.yml -f docker-compose.monitoring.yml restart grafana
```

---

## 🔐 Security Levels

### Level 1: Basic Auth (ทำแล้ว ✅)
```nginx
auth_basic "Monitoring Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

### Level 2: IP Whitelist (เพิ่มเติม)
```nginx
location /grafana/ {
    # Allow specific IPs
    allow 203.0.113.0/24;  # Your office IP
    allow 198.51.100.5;    # Your home IP
    deny all;
    
    # Basic auth
    auth_basic "Monitoring Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    proxy_pass http://localhost:3000/;
}
```

### Level 3: VPN Only
- Setup VPN (WireGuard/OpenVPN)
- Bind monitoring ports to VPN interface only
- No public access

---

## 🚀 Access URLs

### After Setup:

**Option 1 (Subdomain):**
- Grafana: `http://monitoring.yourdomain.com`
- Prometheus: `http://monitoring.yourdomain.com/prometheus/`
- cAdvisor: `http://monitoring.yourdomain.com/cadvisor/`

**Option 2 (Path Prefix):**
- Grafana: `http://yourdomain.com/grafana/`
- Prometheus: `http://yourdomain.com/prometheus/`

**Login:**
- Username: `admin` (ที่สร้างด้วย htpasswd)
- Password: `<your-password>`

---

## 🔒 SSL/HTTPS Setup (แนะนำ)

### Install Certbot

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate (Subdomain)
sudo certbot --nginx -d monitoring.yourdomain.com

# Get SSL certificate (Main domain + monitoring path)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### Certbot จะ auto-update nginx config:
```nginx
server {
    listen 443 ssl http2;
    server_name monitoring.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/monitoring.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitoring.yourdomain.com/privkey.pem;
    
    # ... rest of config
}
```

---

## 🧪 Testing

### 1. Test Nginx Config
```bash
sudo nginx -t
```

### 2. Test Basic Auth
```bash
# Should return 401 Unauthorized
curl http://monitoring.yourdomain.com

# Should return 200 OK
curl -u admin:yourpassword http://monitoring.yourdomain.com
```

### 3. Test Grafana
```bash
curl -u admin:yourpassword http://monitoring.yourdomain.com/api/health
```

### 4. Test Prometheus
```bash
curl -u admin:yourpassword http://monitoring.yourdomain.com/prometheus/api/v1/status/config
```

---

## 🐛 Troubleshooting

### 1. 502 Bad Gateway
```bash
# Check if services are running
docker ps | grep -E "grafana|prometheus"

# Check logs
docker logs medml_grafana
docker logs medml_prometheus

# Check nginx error log
sudo tail -f /var/log/nginx/monitoring_error.log
```

### 2. 401 Unauthorized (แม้ใส่ password ถูก)
```bash
# Check .htpasswd file exists
ls -la /etc/nginx/.htpasswd

# Check nginx can read it
sudo nginx -t

# Recreate password
sudo htpasswd -c /etc/nginx/.htpasswd admin
```

### 3. Grafana CSS/JS ไม่โหลด (ถ้าใช้ path prefix)
```bash
# Update Grafana config
docker-compose -f docker-compose.monitoring.yml exec grafana sh -c "
  echo 'GF_SERVER_ROOT_URL=http://yourdomain.com/grafana/' >> /etc/grafana/grafana.ini
  echo 'GF_SERVER_SERVE_FROM_SUB_PATH=true' >> /etc/grafana/grafana.ini
"

# Restart
docker-compose -f docker-compose.monitoring.yml restart grafana
```

---

## 📊 Monitoring Access Logs

```bash
# Watch access logs
sudo tail -f /var/log/nginx/monitoring_access.log

# Check who accessed
sudo grep "monitoring" /var/log/nginx/monitoring_access.log | awk '{print $1}' | sort | uniq -c

# Check failed auth attempts
sudo grep "401" /var/log/nginx/monitoring_access.log
```

---

## 🔐 Best Practices

1. ✅ **Always use Basic Auth** (minimum)
2. ✅ **Use HTTPS/SSL** (via Let's Encrypt)
3. ✅ **Whitelist IPs** (if possible)
4. ✅ **Change default Grafana password**
5. ✅ **Monitor access logs**
6. ✅ **Use strong passwords**
7. ✅ **Don't expose Prometheus publicly** (use Grafana only)
8. ✅ **Regular security updates**

---

## 📝 Quick Commands

```bash
# Reload nginx
sudo systemctl reload nginx

# Test nginx config
sudo nginx -t

# View nginx logs
sudo tail -f /var/log/nginx/monitoring_*.log

# Add new user
sudo htpasswd /etc/nginx/.htpasswd newuser

# Remove user
sudo htpasswd -D /etc/nginx/.htpasswd olduser

# Change password
sudo htpasswd /etc/nginx/.htpasswd existinguser
```

---

## 🎓 Next Steps

1. Setup SSL with Let's Encrypt
2. Configure Grafana dashboards
3. Setup alert notifications (Slack/Email)
4. Add more metrics exporters
5. Setup log aggregation (ELK/Loki)

---

**Happy Monitoring! 📊🔐**
