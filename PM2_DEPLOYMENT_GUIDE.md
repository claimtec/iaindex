# 🚀 AIIndex v1.1 - PM2 Deployment Guide

**Last Updated**: 2025-10-14 21:45:00
**For**: Production deployment with PM2 process manager

---

## 📋 Overview

PM2 is a production-grade process manager for Node.js and Python applications with:
- ✅ Process clustering (multi-core utilization)
- ✅ Auto-restart on crashes
- ✅ Zero-downtime reloads
- ✅ Log management
- ✅ Monitoring dashboard
- ✅ Startup scripts (auto-start on boot)

---

## 🔧 Prerequisites

### 1. Install PM2 (2 minutes)

```bash
# Install PM2 globally
npm install -g pm2

# Install serve (for docs)
npm install -g serve

# Verify installation
pm2 --version
```

### 2. Create Logs Directory (1 minute)

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex
mkdir -p logs
```

### 3. Build Dashboard (if not already done)

```bash
cd apps/web
npm run build
cd ../..
```

### 4. Build Documentation (if not already done)

```bash
cd apps/docs
npm run build
cd ../..
```

---

## 🚀 Quick Start (5 minutes)

### Start All Services

```bash
# Production
pm2 start ecosystem.config.js --env production

# Or Staging
pm2 start ecosystem.config.js --env staging
```

This starts:
- **aiindex-api** - FastAPI backend (4 instances on port 8000)
- **aiindex-dashboard** - Next.js dashboard (2 instances on port 3000)
- **aiindex-docs** - Docusaurus docs (1 instance on port 3001)

### Check Status

```bash
pm2 status

# Expected output:
# ┌─────┬────────────────────┬─────────┬─────────┬─────────┬──────────┐
# │ id  │ name               │ mode    │ ↺       │ status  │ cpu      │
# ├─────┼────────────────────┼─────────┼─────────┼─────────┼──────────┤
# │ 0   │ aiindex-api        │ cluster │ 0       │ online  │ 2%       │
# │ 1   │ aiindex-dashboard  │ cluster │ 0       │ online  │ 1%       │
# │ 2   │ aiindex-docs       │ fork    │ 0       │ online  │ 0%       │
# └─────┴────────────────────┴─────────┴─────────┴─────────┴──────────┘
```

### Test Services

```bash
# Test API
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test Dashboard
curl http://localhost:3000
# Expected: HTML response

# Test Docs
curl http://localhost:3001
# Expected: HTML response
```

---

## 📊 PM2 Commands Reference

### Process Management

```bash
# Start all apps
pm2 start ecosystem.config.js --env production

# Stop all apps
pm2 stop all

# Restart all apps
pm2 restart all

# Delete all apps from PM2
pm2 delete all

# Start specific app
pm2 start aiindex-api

# Restart specific app (zero-downtime)
pm2 reload aiindex-dashboard

# Scale app (increase/decrease instances)
pm2 scale aiindex-api 8
```

### Monitoring

```bash
# Real-time monitoring dashboard
pm2 monit

# View logs (all apps)
pm2 logs

# View logs (specific app)
pm2 logs aiindex-api

# View only errors
pm2 logs --err

# Clear logs
pm2 flush
```

### Information

```bash
# Show process details
pm2 show aiindex-api

# List all processes
pm2 list

# Pretty-print process list
pm2 prettylist
```

### Startup Scripts

```bash
# Generate startup script (auto-start on boot)
pm2 startup

# Save current process list
pm2 save

# Restore saved process list
pm2 resurrect

# Remove startup script
pm2 unstartup
```

---

## ⚙️ Configuration Details

### Ecosystem File: [ecosystem.config.js](./ecosystem.config.js)

```javascript
module.exports = {
  apps: [
    {
      name: 'aiindex-api',
      script: 'run_local.py',
      cwd: './apps/api',
      interpreter: 'python3',
      instances: 4,              // 4 instances for load balancing
      exec_mode: 'cluster',      // Cluster mode
      max_memory_restart: '500M', // Restart if memory > 500MB
      env_production: {
        NODE_ENV: 'production',
        PORT: 8000,
      },
    },
    // ... other apps
  ]
};
```

### Key Features:

**API**:
- 4 clustered instances for high availability
- Auto-restart on crash
- Memory limit: 500MB per instance
- Logs: `logs/api-error.log`, `logs/api-out.log`

**Dashboard**:
- 2 clustered instances
- Zero-downtime reload support
- Memory limit: 500MB per instance
- Logs: `logs/dashboard-error.log`, `logs/dashboard-out.log`

**Docs**:
- Single instance (static files)
- Served by `serve` package
- Memory limit: 200MB
- Logs: `logs/docs-error.log`, `logs/docs-out.log`

---

## 🔄 Deployment Workflow

### Initial Deployment

```bash
# 1. Navigate to project
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# 2. Build dashboard and docs
cd apps/web && npm run build && cd ../..
cd apps/docs && npm run build && cd ../..

# 3. Start with PM2
pm2 start ecosystem.config.js --env production

# 4. Save process list
pm2 save

# 5. Setup auto-start on boot
pm2 startup
# Follow the command it prints

# 6. Verify
pm2 status
pm2 logs
```

### Update Deployment (Zero-Downtime)

```bash
# 1. Pull latest code
git pull origin main

# 2. Update dependencies (if needed)
cd apps/api && pip3 install -r requirements.txt && cd ../..
cd apps/web && npm install && cd ../..

# 3. Rebuild dashboard and docs
cd apps/web && npm run build && cd ../..
cd apps/docs && npm run build && cd ../..

# 4. Reload apps (zero-downtime)
pm2 reload aiindex-api
pm2 reload aiindex-dashboard
pm2 restart aiindex-docs

# 5. Verify
pm2 logs --lines 50
```

---

## 🌐 Nginx Reverse Proxy (Recommended)

For production, use Nginx as reverse proxy:

### Install Nginx

```bash
# macOS
brew install nginx

# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### Nginx Configuration

Create `/etc/nginx/sites-available/aiindex`:

```nginx
# API
server {
    listen 80;
    server_name api.aiindex.org;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# Dashboard
server {
    listen 80;
    server_name aiindex.org www.aiindex.org;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Documentation
server {
    listen 80;
    server_name docs.aiindex.org;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

### Enable Configuration

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/aiindex /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Add SSL with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificates
sudo certbot --nginx -d aiindex.org -d www.aiindex.org
sudo certbot --nginx -d api.aiindex.org
sudo certbot --nginx -d docs.aiindex.org

# Auto-renewal (certbot adds this automatically)
sudo certbot renew --dry-run
```

---

## 📊 Monitoring & Logging

### PM2 Web Monitoring

```bash
# Install PM2+ (optional, free tier available)
pm2 plus

# Or use built-in web interface
pm2 web
# Opens web interface at http://localhost:9615
```

### Log Management

```bash
# View real-time logs
pm2 logs

# View logs with timestamps
pm2 logs --timestamp

# View last 100 lines
pm2 logs --lines 100

# Export logs
pm2 logs > aiindex-logs.txt

# Rotate logs (prevent large files)
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
pm2 set pm2-logrotate:compress true
```

### Monitoring Metrics

```bash
# Real-time monitoring
pm2 monit

# CPU/Memory usage
pm2 show aiindex-api

# JSON output for scripting
pm2 jlist
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

Store sensitive data in environment files:

```bash
# apps/api/.env.production
DATABASE_URL=postgresql://...
SUPABASE_KEY=...
SECRET_KEY=...
```

Load with PM2:

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'aiindex-api',
    script: 'run_local.py',
    env_file: './apps/api/.env.production', // PM2 5.0+
  }]
};
```

### 2. Run as Non-Root User

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash aiindex

# Install PM2 for user
sudo -u aiindex npm install -g pm2

# Start services as user
sudo -u aiindex pm2 start ecosystem.config.js --env production
```

### 3. Firewall Configuration

```bash
# Allow only specific ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Block direct access to app ports
sudo ufw deny 8000/tcp  # API
sudo ufw deny 3000/tcp  # Dashboard
sudo ufw deny 3001/tcp  # Docs
```

---

## 📈 Performance Tuning

### 1. Cluster Mode

```javascript
// Adjust instances based on CPU cores
{
  name: 'aiindex-api',
  instances: 'max',  // Use all CPU cores
  // or
  instances: 4,      // Fixed number
}
```

### 2. Memory Limits

```javascript
{
  max_memory_restart: '500M',  // Restart if exceeds 500MB
}
```

### 3. Load Balancing

PM2 automatically load-balances across instances in cluster mode.

---

## 🚨 Troubleshooting

### API Won't Start

```bash
# Check logs
pm2 logs aiindex-api --err

# Check Python path
which python3

# Test manually
cd apps/api
python3 run_local.py
```

### Dashboard Build Fails

```bash
# Clear Next.js cache
cd apps/web
rm -rf .next
npm run build
```

### PM2 Startup Script Not Working

```bash
# Remove old startup script
pm2 unstartup

# Generate new one
pm2 startup

# Save processes
pm2 save
```

### High Memory Usage

```bash
# Restart specific app
pm2 restart aiindex-api

# Reduce instances
pm2 scale aiindex-api 2
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] PM2 installed globally
- [ ] Dashboard built (`npm run build`)
- [ ] Docs built (`npm run build`)
- [ ] Environment variables configured
- [ ] Database accessible
- [ ] Logs directory created

### Deployment
- [ ] Start apps with PM2
- [ ] Verify all apps online (`pm2 status`)
- [ ] Test endpoints (API, Dashboard, Docs)
- [ ] Check logs for errors
- [ ] Save process list (`pm2 save`)
- [ ] Setup startup script (`pm2 startup`)

### Post-Deployment
- [ ] Configure Nginx reverse proxy
- [ ] Setup SSL certificates
- [ ] Configure firewall
- [ ] Enable log rotation
- [ ] Set up monitoring alerts
- [ ] Test auto-restart (kill a process)
- [ ] Test server reboot (auto-start)

---

## 🎯 Quick Reference

```bash
# Start
pm2 start ecosystem.config.js --env production

# Status
pm2 status

# Logs
pm2 logs

# Monitor
pm2 monit

# Restart
pm2 reload all

# Stop
pm2 stop all

# Delete
pm2 delete all

# Save
pm2 save

# Startup
pm2 startup && pm2 save
```

---

## 📚 Resources

- **PM2 Documentation**: https://pm2.keymetrics.io/docs/
- **PM2 GitHub**: https://github.com/Unitech/pm2
- **PM2 Cheat Sheet**: https://devhints.io/pm2

---

**Last Updated**: 2025-10-14 21:45:00
**Status**: Ready for PM2 deployment ✅
