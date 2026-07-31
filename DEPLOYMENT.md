# Deployment Guide

## 🚀 Production Deployment

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Rishurajgautam24/universal-memory-system.git
cd ums

# Create environment file
cp .env.example .env
# Edit .env with your production values

# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f ums
```

### Option 2: Direct Python

```bash
# Clone and install
git clone https://github.com/Rishurajgautam24/universal-memory-system.git
cd ums
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with production values

# Start with systemd (Linux)
sudo nano /etc/systemd/system/ums.service
```

Create `/etc/systemd/system/ums.service`:
```ini
[Unit]
Description=UMS Memory Gateway
After=network.target

[Service]
Type=simple
User=ums
WorkingDirectory=/opt/ums
Environment="PATH=/opt/ums/.venv/bin"
ExecStart=/opt/ums/.venv/bin/uvicorn ums.gateway.app:create_app --host 0.0.0.0 --port 8000 --factory
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable ums
sudo systemctl start ums
sudo systemctl status ums
```

### Option 3: Kubernetes

```yaml
# ums-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ums
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ums
  template:
    metadata:
      labels:
        app: ums
    spec:
      containers:
      - name: ums
        image: ums:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: ums-secrets
              key: openrouter-api-key
        - name: DATABASE_URL
          value: "postgresql+aiosqlite:///data/ums.db"
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: ums-data
---
apiVersion: v1
kind: Service
metadata:
  name: ums
spec:
  selector:
    app: ums
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | OpenRouter API key |
| `OPENROUTER_BASE_URL` | No | `https://openrouter.ai/api/v1` | OpenRouter base URL |
| `EXTRACTION_MODEL` | No | `openai/gpt-4o-mini` | Model for observation extraction |
| `SYNTHESIS_MODEL` | No | `openai/gpt-4o` | Model for memory synthesis |
| `EMBEDDING_MODEL` | No | `openai/text-embedding-3-small` | Model for embeddings |
| `DATABASE_URL` | No | `sqlite+aiosqlite://data/ums.db` | Database connection string |
| `ADMIN_API_KEY` | Yes* | - | API key for authentication (*required in production) |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Production Settings

```env
# .env.production
OPENROUTER_API_KEY=sk-or-v1-...
ADMIN_API_KEY=your-secure-api-key-here
DATABASE_URL=postgresql+aiosqlite://ums:password@db:5432/ums
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=WARNING
RELOAD=false
```

## 🗄️ Database

### SQLite (Development)

```env
DATABASE_URL=sqlite+aiosqlite://data/ums.db
```

### PostgreSQL (Production)

```env
DATABASE_URL=postgresql+aiosqlite://user:pass@host:5432/ums
```

## 🔒 Security

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name ums.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ums.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/ums.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ums.yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring

### Health Check

```bash
curl https://ums.yourdomain.com/health
```

### Logs

```bash
# Docker
docker-compose logs -f ums

# Systemd
journalctl -u ums -f
```

## 🔄 Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Or with systemd
sudo systemctl restart ums