# 🐳 Docker Directory

This directory contains Docker configurations for the Gold Tier AI Employee project.

---

## 📁 Folder Structure

### odoo/
Docker configuration for Odoo Community Edition 19

**Files:**
- `docker-compose.yml` - Docker Compose configuration

---

## 🚀 Quick Start

### Start Odoo
```bash
cd docker/odoo
docker-compose up -d
```

### Stop Odoo
```bash
cd docker/odoo
docker-compose down
```

### View Logs
```bash
cd docker/odoo
docker-compose logs -f odoo
```

### Restart Odoo
```bash
cd docker/odoo
docker-compose restart
```

---

## 📋 docker-compose.yml

### Services

#### PostgreSQL Database
- **Image:** postgres:15
- **Environment:**
  - POSTGRES_DB=postgres
  - POSTGRES_USER=odoo
  - POSTGRES_PASSWORD=odoo
- **Volume:** odoo-db-data (persistent storage)

#### Odoo Application
- **Image:** odoo:19
- **Port:** 8069 (mapped to host)
- **Environment:**
  - HOST=db
  - USER=odoo
  - PASSWORD=odoo
- **Volume:** odoo-web-data (persistent storage)
- **Depends on:** PostgreSQL database

---

## 🔧 Configuration

### Ports
- **8069** - Odoo web interface
  - Access at: http://localhost:8069

### Volumes
- **odoo-db-data** - PostgreSQL data (persistent)
- **odoo-web-data** - Odoo data (persistent)

### Network
- Services communicate via Docker internal network
- Database accessible to Odoo as `db` hostname

---

## 📝 First Time Setup

### 1. Start Services
```bash
cd docker/odoo
docker-compose up -d
```

### 2. Wait for Startup
Wait 2-3 minutes for services to initialize.

### 3. Access Odoo
Open browser: http://localhost:8069

### 4. Create Database
- **Master Password:** admin
- **Database Name:** odoo
- **Email:** your-email@example.com
- **Password:** admin
- **Language:** English
- **Country:** Your country
- **Demo data:** No (uncheck)

### 5. Install Accounting Module
1. Go to Apps menu
2. Search "Accounting"
3. Click Install
4. Wait for installation

---

## 🔍 Troubleshooting

### Odoo Won't Start
```bash
# Check if containers are running
docker ps

# View logs
docker-compose logs odoo

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose down
docker-compose up -d --build
```

### Port 8069 Already in Use
```bash
# Find what's using the port
netstat -ano | findstr :8069

# Kill the process or change port in docker-compose.yml
# Change: "8069:8069" to "8070:8069"
```

### Database Connection Failed
```bash
# Check database is running
docker ps | grep postgres

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Slow Performance
```bash
# Allocate more resources in Docker Desktop
# Settings → Resources → Advanced
# Increase CPU and Memory

# Or use production-grade setup with separate servers
```

---

## 🔒 Security

### Development (Current Setup)
- ✅ Isolated in Docker containers
- ✅ Not exposed to internet
- ⚠️ Default passwords (change for production)

### Production Recommendations
- ❌ Don't use default passwords
- ❌ Don't expose port 8069 directly
- ✅ Use reverse proxy (nginx)
- ✅ Enable HTTPS
- ✅ Use strong passwords
- ✅ Regular backups

---

## 💾 Data Management

### Backup Data
```bash
# Backup database
docker exec odoo-db pg_dump -U odoo postgres > backup.sql

# Backup Odoo files
docker cp odoo:/var/lib/odoo ./odoo-backup
```

### Restore Data
```bash
# Restore database
cat backup.sql | docker exec -i odoo-db psql -U odoo postgres

# Restore Odoo files
docker cp ./odoo-backup odoo:/var/lib/odoo
```

### Reset Everything
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker volume rm odoo_odoo-db-data odoo_odoo-web-data

# Start fresh
docker-compose up -d
```

---

## 📊 Resource Usage

### Typical Usage
- **CPU:** 1-2 cores
- **Memory:** 2-4 GB
- **Disk:** 5-10 GB

### Minimum Requirements
- **CPU:** 1 core
- **Memory:** 2 GB
- **Disk:** 5 GB

### Recommended
- **CPU:** 2+ cores
- **Memory:** 4+ GB
- **Disk:** 10+ GB

---

## 🔄 Updates

### Update Odoo
```bash
# Pull latest image
docker-compose pull

# Restart with new image
docker-compose down
docker-compose up -d
```

### Update PostgreSQL
```bash
# Backup first!
docker exec odoo-db pg_dump -U odoo postgres > backup.sql

# Update image in docker-compose.yml
# Change: postgres:15 to postgres:16

# Restart
docker-compose down
docker-compose up -d
```

---

## 🎯 Advanced Configuration

### Custom Odoo Configuration
Create `odoo.conf`:
```ini
[options]
admin_passwd = admin
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = /mnt/extra-addons
```

Update docker-compose.yml:
```yaml
odoo:
  volumes:
    - ./odoo.conf:/etc/odoo/odoo.conf
```

### Multiple Odoo Instances
```yaml
# docker-compose.yml
services:
  odoo-dev:
    ports:
      - "8069:8069"

  odoo-test:
    ports:
      - "8070:8069"
```

---

## 📚 Related Documentation

- **Setup Guide:** `docs/guides/SETUP_INSTRUCTIONS.md`
- **Odoo Documentation:** https://www.odoo.com/documentation/19.0/
- **Docker Documentation:** https://docs.docker.com/

---

## 🚀 Production Deployment

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml odoo
```

### Using Kubernetes
```bash
# Convert to Kubernetes
kompose convert -f docker-compose.yml

# Deploy to cluster
kubectl apply -f .
```

---

**Last Updated:** 2026-03-26
**Status:** Development setup ready
**Production:** Not configured (development only)
