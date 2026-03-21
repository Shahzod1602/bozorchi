#!/bin/bash
set -e

PROJECT_DIR="/opt/bozorlik"
DOMAIN="bozorchi.identify.uz"

echo "=== Bozorlik deploy ==="

# Nginx config
cp nginx/bozorchi.identify.uz /etc/nginx/sites-available/bozorchi.identify.uz
ln -sf /etc/nginx/sites-available/bozorchi.identify.uz /etc/nginx/sites-enabled/bozorchi.identify.uz

# SSL olish (agar yo'q bo'lsa)
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "SSL sertifikat olinmoqda..."
    # Avval HTTP bilan nginx ishga tushirish
    sed -i 's/listen 443 ssl;/listen 443;/' /etc/nginx/sites-available/bozorchi.identify.uz
    sed -i '/ssl_/d' /etc/nginx/sites-available/bozorchi.identify.uz
    nginx -t && systemctl reload nginx

    certbot certonly --webroot -w /var/www/certbot \
        -d $DOMAIN --non-interactive --agree-tos -m admin@identify.uz

    # SSL qaytarish
    cp nginx/bozorchi.identify.uz /etc/nginx/sites-available/bozorchi.identify.uz
fi

nginx -t && systemctl reload nginx

# Docker deploy
cd $PROJECT_DIR
docker compose pull 2>/dev/null || true
docker compose build --no-cache
docker compose up -d
docker image prune -f

echo "=== Deploy tugadi! ==="
echo "Bot: https://$DOMAIN"
