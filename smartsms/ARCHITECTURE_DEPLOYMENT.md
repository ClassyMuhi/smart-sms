# Architecture & Deployment Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│              (Web/Mobile App,Postman)                    │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS/REST API
                       ▼
┌─────────────────────────────────────────────────────────┐
│              API GATEWAY / REVERSE PROXY                 │
│                  (Nginx / Apache)                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│               DJANGO APPLICATION LAYER                   │
├─────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────┐     │
│  │ AUTHENTICATION MIDDLEWARE (JWT Validation)     │     │
│  └────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────┐     │
│  │ AUTH MODULE VIEWS & SERIALIZERS/Validation      │     │
│  │ - Register, Login, OTP, Password Reset         │     │
│  └────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────┐     │
│  │ SECURITY & VALIDATION LAYER                    │     │
│  │ - Password hashing, OTP generation, validation │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│             DATABASE LAYER (PostgreSQL)                  │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────────┐ ┌────────────────────────────┐  │
│  │ auth_customuser   │ │ auth_otpverification       │  │
│  │ - id (PK)         │ │ - id (PK)                  │  │
│  │ - phone (unique)  │ │ - user_id (FK, unique)     │  │
│  │ - email (unique)  │ │ - otp_code                 │  │
│  │ - password_hash   │ │ - expires_at               │  │
│  │ - full_name       │ │ - is_verified              │  │
│  │ - created_at      │ │ - attempts                 │  │
│  └───────────────────┘ └────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐ │
│  │ auth_userloginhistory                              │ │
│  │ - id (PK)                                          │ │
│  │ - user_id (FK)                                     │ │
│  │ - ip_address, user_agent                          │ │
│  │ - login_at                                         │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                   │        │        │
           ┌───────┴────────┴────────┴────────┐
           │  INDEXES (Performance)            │
           │ - phone, email, created_at        │
           └──────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│           EXTERNAL SERVICES (Future)                      │
├──────────────────────────────────────────────────────────┤
│ - Email Service (SendGrid, AWS SES)                      │
│ - SMS Service (Twilio, AWS SNS)                          │
│ - Analytics/Logging (Sentry, LogRocket)                 │
│ - Caching (Redis)                                        │
└──────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Registration Flow
```
User Input
   │
   ▼
Validate (Phone, Email, Password)
   │
   ▼ (Valid)
Hash Password
   │
   ▼
Create User (is_phone_verified = False)
   │
   ▼
Generate OTP (6 digits)
   │
   ▼
Store OTP Record (expires in 5 min)
   │
   ▼
Send OTP (Console/SMS/Email)
   │
   ▼
Return: user_id + success message
```

### Login Flow
```
User Credentials (phone/email + password)
   │
   ▼
Find User (by phone or email)
   │
   ├─ Not Found → 404 Error
   │
   ▼ (Found)
Verify Password Hash
   │
   ├─ Invalid → 400 Error
   │
   ▼ (Valid)
Check Phone Verified?
   │
   ├─ No → 403 Forbidden
   │
   ▼ (Yes)
Generate JWT Tokens (access + refresh)
   │
   ▼
Update last_login_at timestamp
   │
   ▼
Log Login History (IP, user-agent)
   │
   ▼
Return: User data + Tokens
```

### Password Reset Flow
```
Forgot Password Request (phone/email)
   │
   ▼
Find User
   │
   ├─ Not Found → Security: Don't reveal
   │
   ▼ (Found)
Generate Reset OTP
   │
   ▼
Store OTP (purpose=password_reset)
   │
   ▼
Send OTP to User
   │
   ▼
User Submits Reset Form (phone/email + OTP + new password)
   │
   ▼
Validate OTP
   │
   ├─ Invalid/Expired → 400 Error
   │
   ▼ (Valid)
Validate New Password Strength
   │
   ├─ Weak → 400 Error
   │
   ▼ (Strong)
Update Password Hash
   │
   ▼
Mark OTP as Verified
   │
   ▼
Return: Success message
```

---

## Deployment Options

### Option 1: Development (Local)
```
Environment: Machine
Database: SQLite (local file)
Server: Django dev server (python manage.py runserver)
Suitable for: Learning, testing, development
```

### Option 2: Testing/Staging
```
Environment: Staging server
Database: PostgreSQL (separate instance)
Server: Gunicorn + Nginx reverse proxy
Suitable for: Pre-production testing, integration testing
```

### Option 3: Production
```
Environment: Production server (AWS EC2, DigitalOcean, etc.)
Database: PostgreSQL (managed RDS or dedicated instance)
Server: Gunicorn/uWSGI + Nginx + Load Balancer
Security:
  - HTTPS/SSL certificates (Let's Encrypt)
  - Firewall rules
  - WAF (Web Application Firewall)
  - Rate limiting
  - DDoS protection

Services:
  - Email gateway (SendGrid, AWS SES)
  - SMS gateway (Twilio, AWS SNS)
  - Monitoring (New Relic, DataDog)
  - Logging (ELK Stack, Splunk)
  - Error tracking (Sentry)
  - CDN for static files
```

---

## Production Deployment Checklist

### Security
- [ ] Change SECRET_KEY to random 50+ character string
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS with actual domain
- [ ] Enable HTTPS/SSL/TLS certificates
- [ ] Configure CORS for production domains only
- [ ] Set secure cookies (CSRF, Session, etc.)
- [ ] Enable HSTS headers
- [ ] Configure Content Security Policy (CSP)
- [ ] Setup firewall rules
- [ ] Enable API rate limiting

### Database
- [ ] Setup PostgreSQL with strong password
- [ ] Enable database backups (daily)
- [ ] Setup read replicas for scaling
- [ ] Configure SSL connections to database
- [ ] Setup database monitoring/alerts
- [ ] Regular database optimization

### Application
- [ ] Run collectstatic command
- [ ] Setup gunicorn/uWSGI workers
- [ ] Configure Nginx reverse proxy
- [ ] Setup PM2 or Supervisor for auto-restart
- [ ] Configure logging (file + centralized)
- [ ] Setup monitoring/alerting

### Email/SMS
- [ ] Configure actual email service
- [ ] Configure SMS gateway
- [ ] Setup templates
- [ ] Configure retry logic
- [ ] Monitor delivery rates

### Monitoring & Logging
- [ ] Setup application monitoring (uptime, performance)
- [ ] Setup error tracking (Sentry)
- [ ] Setup log aggregation (ELK, Splunk)
- [ ] Configure alerts for critical errors
- [ ] Monitor database performance

### Backups & Disaster Recovery
- [ ] Daily database backups
- [ ] Test backup restoration
- [ ] Document recovery procedures
- [ ] Setup replication for HA

---

## Deployment Guide: AWS EC2 + RDS

### 1. Launch EC2 Instance
```bash
# Choose Ubuntu 20.04 LTS
# Instance type: t3.micro (free tier) or t3.small (production)
# Security group: Allow 80, 443, 22, 5432 as needed
# Create key pair for SSH access
```

### 2. Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. Install System Dependencies
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql-client git nginx
```

### 4. Clone Project
```bash
git clone <your-repo-url> smartsms
cd smartsms
```

### 5. Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Create RDS Database
```bash
# AWS Console → RDS → Create DB instance
# Engine: PostgreSQL
# Instance type: db.t3.micro or db.t3.small
# DB name: smartsms_db
# Master username: postgres
# Master password: Strong password
# Save connection details
```

### 7. Update Django Settings
```bash
# Update DATABASES in settings.py with RDS endpoint
# Update ALLOWED_HOSTS with EC2 IP/domain
# Set DEBUG = False
# Set SECRET_KEY to random value
```

### 8. Run Initial Setup
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 9. Setup Gunicorn
```bash
pip install gunicorn
gunicorn smartsms.wsgi:application --bind 0.0.0.0:8000
```

### 10. Setup Nginx Reverse Proxy
```bash
# Create /etc/nginx/sites-available/smartsms:

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/smartsms/staticfiles/;
    }
}
```

### 11. Enable Site & Restart Nginx
```bash
sudo ln -s /etc/nginx/sites-available/smartsms /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 12. Setup SSL/TLS (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 13. Setup Process Manager (Supervisor)
```bash
sudo apt install supervisor
# Create supervisor config to auto-restart gunicorn
```

---

## Scaling Considerations

### Horizontal Scaling
- Load balancer (AWS ELB, nginx)
- Multiple application instances
- Read replicas for database

### Vertical Scaling
- Increase instance size
- Increase database resources
- Optimize database indexes

### Caching
- Use Redis for sessions
- Cache OTP lookups
- Cache user profiles

### Database Optimization
- Add indexes on frequently queried fields
- Partition OTP table by created_at
- Archive old login history

---

## Monitoring Commands

```bash
# Check application status
sudo systemctl status gunicorn

# Check Nginx status
sudo systemctl status nginx

# Monitor system resources
top
htop
free -h
df -h

# Check database connections
psql -h <rds-endpoint> -U postgres -d smartsms_db -c "SELECT * FROM pg_stat_activity;"

# Check logs
tail -f /var/log/gunicorn/smartsms.log
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## Database Backup Strategy

```bash
# Manual backup
pg_dump -h <rds-endpoint> -U postgres smartsms_db > backup-$(date +%Y%m%d).sql

# Restore from backup
psql -h <rds-endpoint> -U postgres smartsms_db < backup-20240115.sql

# AWS RDS automated backups
# Enable automated backups (retention: 30 days)
# Enable backup to S3
```

---

## Performance Targets

- API Response Time: < 200ms
- Database Query Time: < 50ms  
- OTP Generation: < 10ms
- Password Hashing: < 500ms
- Concurrent Users: 1000+
- QPS (Queries Per Second): 100+

---

**Production deployment requires careful planning. Follow this guide for secure, scalable deployment.**
