#!/usr/bin/env bash
set -euo pipefail

# setup-selfsigned-nginx.sh
# Create self-signed SSL cert with SAN (domain + IP), configure Nginx HTTPS reverse proxy to Django (port 8000),
# add /etc/hosts entry locally, and test with curl.
#
# Usage:
#   sudo ./setup-selfsigned-nginx.sh [DOMAIN] [IP]
# Examples:
#   sudo ./setup-selfsigned-nginx.sh dogbreed.local 203.0.113.10
#   sudo ./setup-selfsigned-nginx.sh                 # defaults domain=dogbreed.local and auto-detect IP

# Auto-elevate to root if needed
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "[info] Re-running with sudo..."
  exec sudo -E "$0" "$@"
fi

DOMAIN="${1:-dogbreed.local}"
SERVER_IP="${2:-}"

log() { echo -e "\033[1;32m==>\033[0m $*"; }
warn() { echo -e "\033[1;33m[warn]\033[0m $*"; }
err() { echo -e "\033[1;31m[err ]\033[0m $*" >&2; }

# Ensure curl exists (for IP detection)
if ! command -v curl >/dev/null 2>&1; then
  echo "[info] Installing curl..."
  apt-get update -y
  DEBIAN_FRONTEND=noninteractive apt-get install -y curl
fi

# Try AWS metadata first, then fallback to first IP from hostname -I
if [[ -z "${SERVER_IP}" ]]; then
  SERVER_IP="$(curl -fsS --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-ipv4 || true)"
  if [[ -z "${SERVER_IP}" ]]; then
    SERVER_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
  fi
fi

if [[ -z "${SERVER_IP}" ]]; then
  err "Could not determine server IP automatically. Pass it as second arg."
  err "Example: sudo $0 ${DOMAIN} 203.0.113.10"
  exit 1
fi

CERT_DIR="/etc/ssl/dogbreed"
KEY_FILE="${CERT_DIR}/${DOMAIN}.key"
CRT_FILE="${CERT_DIR}/${DOMAIN}.crt"
OPENSSL_CNF="${CERT_DIR}/openssl.cnf"
NGINX_SITE_AVAIL="/etc/nginx/sites-available/dogbreed.conf"
NGINX_SITE_ENAB="/etc/nginx/sites-enabled/dogbreed.conf"

log "Domain: ${DOMAIN}"
log "Server IP: ${SERVER_IP}"
log "Cert dir: ${CERT_DIR}"

# 0) Dependencies
if ! command -v openssl >/dev/null 2>&1; then
  log "Installing openssl..."
  apt-get update -y
  apt-get install -y openssl
fi

# 1) Prepare directory for certs
log "Preparing certificate directory..."
mkdir -p "${CERT_DIR}"
chmod 750 "${CERT_DIR}"

# 2) Build an OpenSSL config with SAN (DNS + IP)
log "Writing OpenSSL config with SAN..."
cat > "${OPENSSL_CNF}" <<EOF
[ req ]
default_bits       = 2048
distinguished_name = req_distinguished_name
req_extensions     = v3_req
x509_extensions    = v3_req
prompt             = no

[ req_distinguished_name ]
CN = ${DOMAIN}
O  = Dogbreed Local
C  = TH

[ v3_req ]
keyUsage         = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName   = @alt_names

[ alt_names ]
DNS.1 = ${DOMAIN}
DNS.2 = localhost
IP.1  = ${SERVER_IP}
IP.2  = 127.0.0.1
EOF

# 3) Generate key + self-signed cert (valid 365 days)
log "Generating 2048-bit RSA key and self-signed cert (365 days)..."
openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout "${KEY_FILE}" \
  -out "${CRT_FILE}" \
  -days 365 \
  -config "${OPENSSL_CNF}"
chmod 640 "${KEY_FILE}" "${CRT_FILE}"

# 4) Install Nginx if missing
if ! command -v nginx >/dev/null 2>&1; then
  log "Installing nginx..."
  apt-get update -y
  DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
fi

# 5) Write Nginx reverse proxy config (HTTPS 443 -> Django 8000)
log "Writing Nginx site config: ${NGINX_SITE_AVAIL}"
cat > "${NGINX_SITE_AVAIL}" <<'EOF'
# Dogbreed reverse proxy over HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name DOMAIN_PLACEHOLDER;

    # Redirect all HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name DOMAIN_PLACEHOLDER;

    # SSL certs
    ssl_certificate     CRT_PLACEHOLDER;
    ssl_certificate_key KEY_PLACEHOLDER;

    # Basic SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    # Proxy to Django backend on 8000
    location / {
        proxy_pass http://127.0.0.1:8000;

        # Proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS (adjust origins as needed)
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
        add_header Access-Control-Allow-Credentials "true" always;

        # Handle preflight requests
        if ($request_method = OPTIONS) {
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }
    }
}
EOF

# Replace placeholders
sed -i "s|DOMAIN_PLACEHOLDER|${DOMAIN}|g" "${NGINX_SITE_AVAIL}"
sed -i "s|CRT_PLACEHOLDER|${CRT_FILE}|g" "${NGINX_SITE_AVAIL}"
sed -i "s|KEY_PLACEHOLDER|${KEY_FILE}|g" "${NGINX_SITE_AVAIL}"

# 6) Enable site and test Nginx
log "Enabling Nginx site..."
ln -sf "${NGINX_SITE_AVAIL}" "${NGINX_SITE_ENAB}"
nginx -t

# Start or reload Nginx robustly
if command -v systemctl >/dev/null 2>&1; then
  if systemctl is-active --quiet nginx; then
    log "Reloading nginx..."
    systemctl reload nginx || true
  else
    log "Enabling and starting nginx..."
    systemctl enable --now nginx || true
  fi
else
  # Fallback for systems without systemd
  log "Starting nginx via service..."
  service nginx start || true
fi

sleep 1
if command -v systemctl >/dev/null 2>&1; then
  systemctl --no-pager --full status nginx || true
fi

# 7) (Optional) Open firewall ports if ufw active
if command -v ufw >/dev/null 2>&1; then
  if ufw status | grep -qi "Status: active"; then
    log "Allowing ports 80 and 443 via ufw..."
    ufw allow 80/tcp || true
    ufw allow 443/tcp || true
  else
    warn "ufw not active; skipping firewall change"
  fi
fi

# 8) Add domain and IP to /etc/hosts locally
log "Adding hosts entry to /etc/hosts..."
HOSTS_LINE="${SERVER_IP}    ${DOMAIN}"
if ! grep -qE "^[[:space:]]*${SERVER_IP}[[:space:]]+${DOMAIN}([[:space:]]|$)" /etc/hosts; then
  echo "${HOSTS_LINE}" >> /etc/hosts
  log "Added: ${HOSTS_LINE}"
else
  warn "Entry already exists in /etc/hosts"
fi

# 9) Test HTTPS (self-signed -> use --insecure)
log "Testing with curl (expect 200/301/302 headers, ignoring TLS trust)..."
curl -I --max-time 10 --insecure "https://${DOMAIN}" || true

echo
log "Completed."
echo "Browse: https://${DOMAIN} (your browser will warn about self-signed cert)"
echo "If accessing from another machine, add this line to that machine's /etc/hosts:"
echo "  ${SERVER_IP}    ${DOMAIN}"
