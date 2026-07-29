#!/bin/bash
set -e

# AI Model Registry — One-shot VPS deployment
# Run as root on fresh Ubuntu VPS
# Usage: bash deploy.sh [DOMAIN]
# Example: bash deploy.sh registry.adamdoesai.com

DOMAIN="${1:-}"
PORT="${2:-9847}"
# PROJECT_DIR can be overridden: PROJECT_DIR=/path/to/install bash deploy.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$(dirname "$SCRIPT_DIR")}"
PYTHON_BIN="python3"

echo "=== AI Model Registry Deployment ==="
echo "Install dir: $PROJECT_DIR"
echo "Domain: ${DOMAIN:-none (HTTP only on port $PORT)}"
echo "Port: $PORT"
echo ""

# ── 1. Install system packages ──────────────────────────────────────────
echo "[1/6] Installing system packages..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git nginx > /dev/null 2>&1
if [ -n "$DOMAIN" ]; then
    apt-get install -y -qq certbot python3-certbot-nginx > /dev/null 2>&1
fi
echo "  Done."

# ── 2. Clone repo ─────────────────────────────────────────────────────────
echo "[2/6] Cloning repo..."
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    git pull origin main
else
    git clone https://github.com/adamchall87/ai-model-registry.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi
echo "  Done."

# ── 3. Python venv + deps ─────────────────────────────────────────────────
echo "[3/6] Setting up Python venv..."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q
echo "  Done."

# ── 4. systemd service ────────────────────────────────────────────────────
echo "[4/6] Installing systemd service..."
cat > /etc/systemd/system/ai-model-registry.service << EOF
[Unit]
Description=AI Model Registry — Live AI model polling service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
Environment=POLL_INTERVAL=3600
ExecStart=$PROJECT_DIR/.venv/bin/python -m uvicorn src.server:app --host 0.0.0.0 --port $PORT
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ai-model-registry
systemctl restart ai-model-registry
sleep 3
systemctl is-active ai-model-registry && echo "  Service running." || { echo "  ERROR: Service failed to start!"; journalctl -u ai-model-registry --no-pager -n 20; exit 1; }

# ── 5. nginx reverse proxy ────────────────────────────────────────────────
echo "[5/6] Configuring nginx..."
if [ -n "$DOMAIN" ]; then
    cat > /etc/nginx/sites-available/ai-model-registry << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    ln -sf /etc/nginx/sites-available/ai-model-registry /etc/nginx/sites-enabled/ai-model-registry
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl reload nginx
    echo "  nginx configured for $DOMAIN"
else
    echo "  No domain specified — skipping nginx. API available at http://localhost:8000"
fi

# ── 6. SSL via Let's Encrypt ──────────────────────────────────────────────
if [ -n "$DOMAIN" ]; then
    echo "[6/6] Setting up SSL with Let's Encrypt..."
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email adamchall87@users.noreply.github.com --redirect
    echo "  SSL configured."
else
    echo "[6/6] Skipped (no domain)."
fi

# ── Verify ────────────────────────────────────────────────────────────────
echo ""
echo "=== Deployment Complete ==="
if [ -n "$DOMAIN" ]; then
    PROTO="https"
    URL="https://$DOMAIN"
else
    PROTO="http"
    URL="http://localhost:$PORT"
fi

echo "Testing API..."
RESPONSE=$(curl -s "$URL/" 2>/dev/null || curl -s http://localhost:$PORT/ 2>/dev/null)
if echo "$RESPONSE" | grep -q "AI Model Registry"; then
    echo "PASS — API is live at $URL"
    echo ""
    echo "Endpoints:"
    echo "  $URL/"
    echo "  $URL/models"
    echo "  $URL/models/search?q=gpt"
    echo "  $URL/models/best?capability=video_gen"
    echo "  $URL/models/compare?models=bytedance/seedance-2.5,kuaishou/kling-3-pro"
    echo "  $URL/stats"
else
    echo "WARN — Could not verify API. Check: journalctl -u ai-model-registry -f"
fi
echo ""
echo "Service logs:  journalctl -u ai-model-registry -f"
echo "Restart:       systemctl restart ai-model-registry"