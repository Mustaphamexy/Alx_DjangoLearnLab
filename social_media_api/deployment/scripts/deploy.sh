#!/bin/bash
# deployment/scripts/deploy.sh

set -e

echo "🚀 Starting deployment of Social Media API..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    echo -e "${YELLOW}📝 Loading environment variables...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create a .env file from .env.example"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
sudo mkdir -p /var/www/social_media_api
sudo mkdir -p /var/www/social_media_api/logs
sudo mkdir -p /run/gunicorn
sudo mkdir -p /var/log/gunicorn

# Copy project files
echo -e "${YELLOW}📋 Copying project files...${NC}"
sudo cp -r . /var/www/social_media_api/
sudo chown -R www-data:www-data /var/www/social_media_api
sudo chmod -R 755 /var/www/social_media_api

# Create virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
cd /var/www/social_media_api
sudo python3 -m venv venv
sudo chown -R www-data:www-data venv

# Activate virtual environment and install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
sudo -u www-data bash -c '
    source /var/www/social_media_api/venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
'

# Apply database migrations
echo -e "${YELLOW}🗄️ Applying database migrations...${NC}"
sudo -u www-data bash -c '
    source /var/www/social_media_api/venv/bin/activate
    cd /var/www/social_media_api
    python manage.py migrate --noinput
'

# Collect static files
echo -e "${YELLOW}📁 Collecting static files...${NC}"
sudo -u www-data bash -c '
    source /var/www/social_media_api/venv/bin/activate
    cd /var/www/social_media_api
    python manage.py collectstatic --noinput
    python manage.py compress --force
'

# Set up Gunicorn service
echo -e "${YELLOW}⚙️ Setting up Gunicorn service...${NC}"
sudo cp deployment/gunicorn/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Set up Nginx
echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
sudo cp deployment/nginx/nginx.conf /etc/nginx/sites-available/social_media_api
sudo ln -sf /etc/nginx/sites-available/social_media_api /etc/nginx/sites-enabled/
sudo nginx -t

# Remove default Nginx site if exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

sudo systemctl restart nginx

# Set up firewall
echo -e "${YELLOW}🛡️ Configuring firewall...${NC}"
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Create superuser if not exists (optional)
echo -e "${YELLOW}👤 Creating superuser (if needed)...${NC}"
read -p "Do you want to create a superuser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo -u www-data bash -c '
        source /var/www/social_media_api/venv/bin/activate
        cd /var/www/social_media_api
        python manage.py createsuperuser
    '
fi

# Set up SSL with Let's Encrypt (optional)
echo -e "${YELLOW}🔒 Setting up SSL (optional)...${NC}"
read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
    read -p "Enter your domain name (e.g., example.com): " domain
    sudo certbot --nginx -d $domain -d www.$domain
    sudo systemctl restart nginx
fi

# Set up automatic renew for SSL
if [ -f /etc/crontab ] && grep -q "certbot renew" /etc/crontab; then
    echo "SSL auto-renew already configured"
else
    echo "0 12 * * * root /usr/bin/certbot renew --quiet" | sudo tee -a /etc/crontab
fi

# Set up log rotation
echo -e "${YELLOW}📊 Setting up log rotation...${NC}"
sudo tee /etc/logrotate.d/social_media_api << EOF
/var/www/social_media_api/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn
    endscript
}
EOF

# Health check
echo -e "${YELLOW}🏥 Running health checks...${NC}"
sleep 5

# Check if services are running
if systemctl is-active --quiet gunicorn; then
    echo -e "${GREEN}✅ Gunicorn is running${NC}"
else
    echo -e "${RED}❌ Gunicorn is not running${NC}"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx is running${NC}"
else
    echo -e "${RED}❌ Nginx is not running${NC}"
fi

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Visit your server IP or domain to verify the application"
echo "2. Check logs: sudo tail -f /var/www/social_media_api/logs/django.log"
echo "3. Monitor services: sudo systemctl status gunicorn"
echo "4. Configure backup strategy"