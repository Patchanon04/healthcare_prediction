#!/bin/bash
# ============================================
# SSL/HTTPS Setup Script
# Dog Breed Prediction System
# ============================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🔐 SSL Certificate Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}" 
   exit 1
fi

# Check if domain is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Domain name is required${NC}"
    echo -e "${YELLOW}Usage: sudo ./setup-ssl.sh yourdomain.com${NC}"
    exit 1
fi

DOMAIN=$1

echo -e "${YELLOW}Setting up SSL for: ${DOMAIN}${NC}"
echo ""

# ============================================
# Step 1: Install Nginx
# ============================================
echo -e "${GREEN}📦 Step 1: Installing Nginx...${NC}"
apt update
apt install -y nginx

# ============================================
# Step 2: Install Certbot
# ============================================
echo -e "${GREEN}📦 Step 2: Installing Certbot...${NC}"
apt install -y certbot python3-certbot-nginx

# ============================================
# Step 3: Setup Nginx Configuration
# ============================================
echo -e "${GREEN}⚙️  Step 3: Configuring Nginx...${NC}"

# Backup default config
if [ -f /etc/nginx/sites-available/default ]; then
    mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
fi

# Create new config
cat > /etc/nginx/sites-available/dogbreed <<EOF
server {
    listen 80;
    server_name ${DOMAIN};
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/dogbreed /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
nginx -t

# Restart Nginx
systemctl restart nginx

echo -e "${GREEN}✅ Nginx configured${NC}"

# ============================================
# Step 4: Obtain SSL Certificate
# ============================================
echo -e "${GREEN}🔐 Step 4: Obtaining SSL certificate...${NC}"
echo -e "${YELLOW}Please make sure:${NC}"
echo -e "${YELLOW}  1. DNS for ${DOMAIN} points to this server${NC}"
echo -e "${YELLOW}  2. Ports 80 and 443 are open${NC}"
echo ""
echo -e "${YELLOW}Continue? (y/n)${NC}"
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted. Run this script again when ready.${NC}"
    exit 0
fi

# Obtain certificate
certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --register-unsafely-without-email

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL certificate obtained successfully!${NC}"
else
    echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
    echo -e "${YELLOW}Please check:${NC}"
    echo -e "${YELLOW}  - DNS is correctly configured${NC}"
    echo -e "${YELLOW}  - Ports 80 and 443 are open${NC}"
    echo -e "${YELLOW}  - Domain is accessible${NC}"
    exit 1
fi

# ============================================
# Step 5: Test Auto-renewal
# ============================================
echo -e "${GREEN}🔄 Step 5: Testing auto-renewal...${NC}"
certbot renew --dry-run

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Auto-renewal test passed${NC}"
else
    echo -e "${YELLOW}⚠️  Auto-renewal test failed${NC}"
fi

# ============================================
# Summary
# ============================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ SSL Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Your site is now accessible at:${NC}"
echo -e "  ${YELLOW}https://${DOMAIN}${NC}"
echo ""
echo -e "${GREEN}Certificate info:${NC}"
certbot certificates
echo ""
echo -e "${GREEN}Auto-renewal:${NC}"
echo -e "  Certbot will automatically renew certificates before expiry"
echo -e "  Check with: ${YELLOW}sudo certbot renew --dry-run${NC}"
echo ""
echo -e "${GREEN}Security Score:${NC}"
echo -e "  Test your SSL: ${YELLOW}https://www.ssllabs.com/ssltest/${NC}"
echo ""
