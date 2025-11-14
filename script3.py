#!/usr/bin/env python3
"""
Script de génération Infrastructure Complète - VERSION CORRIGÉE
- Docker optimisé (multi-stage builds)
- Kubernetes (K8s) production-ready  
- CI/CD GitHub Actions (4 workflows)
- Monitoring (Prometheus + Grafana)
- Scripts utilitaires (10 scripts)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

MICROSERVICES = {
    'auth-service': {'port': 8001, 'replicas': 3},
    'user-service': {'port': 8002, 'replicas': 2},
    'courses-service': {'port': 8003, 'replicas': 3},
    'quizzes-service': {'port': 8004, 'replicas': 2},
    'bookings-service': {'port': 8005, 'replicas': 2},
    'payments-service': {'port': 8006, 'replicas': 3},
    'notifications-service': {'port': 8007, 'replicas': 2},
    'webinars-service': {'port': 8008, 'replicas': 2},
    'gamification-service': {'port': 8009, 'replicas': 2},
    'chatbot-service': {'port': 8010, 'replicas': 2},
    'analytics-service': {'port': 8011, 'replicas': 2},
    'communications-service': {'port': 8012, 'replicas': 2},
    'search-service': {'port': 8013, 'replicas': 2},
    'storage-service': {'port': 8014, 'replicas': 3},
    'security-service': {'port': 8015, 'replicas': 2},
    'monitoring-service': {'port': 8016, 'replicas': 1},
    'ai-gateway': {'port': 8017, 'replicas': 2},
    'cache-service': {'port': 8018, 'replicas': 2},
    'api-gateway': {'port': 8019, 'replicas': 3},
    'i18n-service': {'port': 8020, 'replicas': 1},
    'sponsors-service': {'port': 8021, 'replicas': 2},
}


class InfrastructureGenerator:
    def __init__(self, base_path: Optional[Path] = None, overwrite: bool = False):
        self.base_path = base_path if base_path else Path.cwd()
        self.overwrite = overwrite
        self.created = 0
        self.skipped = 0
        
    def generate_all(self):
        print("🚀 Génération Infrastructure Complète...\n")
        print(f"📂 Répertoire: {self.base_path.resolve()}\n")
        
        self.generate_docker_infrastructure()
        self.generate_kubernetes_manifests()
        self.generate_cicd_pipelines()
        self.generate_monitoring_stack()
        self.generate_utility_scripts()
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║                    ✅ TERMINÉ                             ║
╠════════════════════════════════════════════════════════════╣
║  📊 Fichiers créés: {self.created:<37} ║
║  ⏭️  Fichiers ignorés: {self.skipped:<34} ║
║                                                            ║
║  📁 Emplacement: {str(self.base_path.resolve())[:38]:<38} ║
║                                                            ║
║  🚀 Prochaines étapes:                                    ║
║     ./scripts/setup_dev.sh                                ║
╚════════════════════════════════════════════════════════════╝
        """)
        
    def create_file(self, path: Path, content: str):
        """Crée un fichier uniquement s'il n'existe pas"""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.exists() and not self.overwrite:
            self.skipped += 1
            print(f"⏭️  Existe: {path.relative_to(self.base_path)}")
            return
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.created += 1
        action = "🔄 Remplacé" if path.exists() and self.overwrite else "✓ Créé"
        print(f"{action}: {path.relative_to(self.base_path)}")

    # ==================== DOCKER INFRASTRUCTURE ====================
    
    def generate_docker_infrastructure(self):
        print("🐳 Docker Infrastructure")
        
        files = {
            'docker-compose.prod.yml': self.get_docker_compose_production(),
            'docker-compose.dev.yml': self.get_docker_compose_development(),
            'docker/Dockerfile.microservice': self.get_dockerfile_multistage(),
            'docker/nginx/nginx.conf': self.get_nginx_production_config(),
            'docker/nginx/Dockerfile': self.get_nginx_dockerfile(),
            'docker/postgres/Dockerfile': self.get_postgres_dockerfile(),
            'docker/postgres/init-scripts/01-create-databases.sql': self.get_postgres_init_sql(),
            'docker/redis/Dockerfile': self.get_redis_dockerfile(),
            'docker/redis/redis.conf': self.get_redis_config(),
            'docker/elasticsearch/Dockerfile': self.get_elasticsearch_dockerfile(),
            'docker/elasticsearch/elasticsearch.yml': self.get_elasticsearch_config(),
            'docker/rabbitmq/Dockerfile': self.get_rabbitmq_dockerfile(),
            'docker/rabbitmq/rabbitmq.conf': self.get_rabbitmq_config(),
        }
        
        for filepath, content in files.items():
            self.create_file(self.base_path / filepath, content)

    def get_docker_compose_production(self) -> str:
        services = []
        for service_name, config in MICROSERVICES.items():
            services.append(f"""  {service_name}:
    build:
      context: ./microservices/{service_name}
      dockerfile: ../../docker/Dockerfile.microservice
    image: elearning/{service_name}:latest
    container_name: {service_name}
    restart: always
    ports:
      - "{config['port']}:{config['port']}"
    environment:
      - DJANGO_ENV=production
      - DATABASE_URL=postgresql://${{POSTGRES_USER}}:${{POSTGRES_PASSWORD}}@postgres:5432/{service_name.replace('-', '_')}_db
      - REDIS_URL=redis://redis:6379
      - RABBITMQ_URL=amqp://${{RABBITMQ_USER}}:${{RABBITMQ_PASS}}@rabbitmq:5672
      - SECRET_KEY=${{SECRET_KEY}}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - elearning-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{config['port']}/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3""")
        
        services_str = '\n'.join(services)
        depends_on_str = '\n'.join(f"      - {name}" for name in MICROSERVICES.keys())
        
        return f"""version: '3.8'

networks:
  elearning-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
  rabbitmq_data:
  prometheus_data:
  grafana_data:

services:
  # ==================== INFRASTRUCTURE ====================
  
  postgres:
    build: ./docker/postgres
    image: elearning/postgres:15
    container_name: elearning-postgres
    restart: always
    environment:
      POSTGRES_USER: ${{POSTGRES_USER}}
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD}}
      POSTGRES_DB: elearning
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-scripts:/docker-entrypoint-initdb.d
      - ./backups/postgres:/backups
    networks:
      - elearning-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${{POSTGRES_USER}}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    build: ./docker/redis
    image: elearning/redis:7
    container_name: elearning-redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - elearning-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  rabbitmq:
    build: ./docker/rabbitmq
    image: elearning/rabbitmq:3-management
    container_name: elearning-rabbitmq
    restart: always
    environment:
      RABBITMQ_DEFAULT_USER: ${{RABBITMQ_USER}}
      RABBITMQ_DEFAULT_PASS: ${{RABBITMQ_PASS}}
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - elearning-network

  elasticsearch:
    build: ./docker/elasticsearch
    image: elearning/elasticsearch:8.11
    container_name: elearning-elasticsearch
    restart: always
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - elearning-network

  nginx:
    build: ./docker/nginx
    image: elearning/nginx:alpine
    container_name: elearning-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
{depends_on_str}
    networks:
      - elearning-network

  # ==================== MONITORING ====================
  
  prometheus:
    image: prom/prometheus:latest
    container_name: elearning-prometheus
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./monitoring/prometheus/alerts:/etc/prometheus/alerts:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - elearning-network

  grafana:
    image: grafana/grafana:latest
    container_name: elearning-grafana
    restart: always
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=${{GRAFANA_USER}}
      - GF_SECURITY_ADMIN_PASSWORD=${{GRAFANA_PASSWORD}}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    networks:
      - elearning-network
    depends_on:
      - prometheus

  # ==================== MICROSERVICES ====================

{services_str}
"""

    def get_docker_compose_development(self) -> str:
        return """version: '3.8'

networks:
  elearning-dev-network:
    driver: bridge

volumes:
  postgres_dev_data:
  redis_dev_data:

services:
  postgres:
    image: postgres:15-alpine
    container_name: elearning-postgres-dev
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: elearning_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    networks:
      - elearning-dev-network

  redis:
    image: redis:7-alpine
    container_name: elearning-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data
    networks:
      - elearning-dev-network

  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: elearning-rabbitmq-dev
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    networks:
      - elearning-dev-network

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elearning-elasticsearch-dev
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    networks:
      - elearning-dev-network

  mailhog:
    image: mailhog/mailhog
    container_name: elearning-mailhog
    ports:
      - "1025:1025"
      - "8025:8025"
    networks:
      - elearning-dev-network
"""

    def get_dockerfile_multistage(self) -> str:
        return """# ==================== Builder Stage ====================
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    g++ \\
    postgresql-client \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==================== Runtime Stage ====================
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && \\
    mkdir -p /app/logs /app/media /app/staticfiles && \\
    chown -R appuser:appuser /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \\
    postgresql-client \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Add .local/bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
"""

    def get_nginx_production_config(self) -> str:
        upstream_blocks = []
        location_blocks = []
        
        for service_name, config in MICROSERVICES.items():
            upstream_blocks.append(f"""upstream {service_name} {{
    least_conn;
    server {service_name}:{config['port']} max_fails=3 fail_timeout=30s;
    keepalive 32;
}}""")
            
            location_blocks.append(f"""    location /api/{service_name.replace('-service', '')}/ {{
        proxy_pass http://{service_name};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }}""")
        
        upstreams_str = '\n'.join(upstream_blocks)
        locations_str = '\n'.join(location_blocks)
        
        return f"""user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;

events {{
    worker_connections 4096;
    use epoll;
}}

http {{
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent"';
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    # Upstream blocks
{upstreams_str}

    # HTTPS Server
    server {{
        listen 443 ssl http2;
        server_name api.elearning.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;

        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;

        # Health check
        location /health {{
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }}

        # API Routes
{locations_str}

        # Static files
        location /static/ {{
            alias /var/www/static/;
            expires 30d;
        }}

        # Media files
        location /media/ {{
            alias /var/www/media/;
            expires 7d;
        }}
    }}
}}
"""

    def get_nginx_dockerfile(self) -> str:
        return """FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
RUN mkdir -p /var/www/static /var/www/media /etc/nginx/ssl
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
"""

    def get_postgres_dockerfile(self) -> str:
        return """FROM postgres:15-alpine
RUN apk add --no-cache postgresql-contrib
COPY init-scripts/ /docker-entrypoint-initdb.d/
EXPOSE 5432
"""

    def get_postgres_init_sql(self) -> str:
        databases = [name.replace('-', '_') + '_db' for name in MICROSERVICES.keys()]
        sql = "-- Create databases for all microservices\n\n"
        for db in databases:
            sql += f"CREATE DATABASE {db};\nGRANT ALL PRIVILEGES ON DATABASE {db} TO postgres;\n\n"
        sql += """\\c auth_service_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
"""
        return sql

    def get_redis_dockerfile(self) -> str:
        return """FROM redis:7-alpine
COPY redis.conf /usr/local/etc/redis/redis.conf
RUN mkdir -p /data && chown redis:redis /data
EXPOSE 6379
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
"""

    def get_redis_config(self) -> str:
        return """# Redis Configuration
bind 0.0.0.0
port 6379
appendonly yes
appendfilename "appendonly.aof"
maxmemory 512mb
maxmemory-policy allkeys-lru
"""

    def get_elasticsearch_dockerfile(self) -> str:
        return """FROM docker.elastic.co/elasticsearch/elasticsearch:8.11.0
RUN bin/elasticsearch-plugin install --batch analysis-icu
RUN bin/elasticsearch-plugin install --batch analysis-phonetic
COPY elasticsearch.yml /usr/share/elasticsearch/config/
EXPOSE 9200
"""

    def get_elasticsearch_config(self) -> str:
        return """cluster.name: elearning-cluster
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node
xpack.security.enabled: false
"""

    def get_rabbitmq_dockerfile(self) -> str:
        return """FROM rabbitmq:3-management-alpine
RUN rabbitmq-plugins enable --offline rabbitmq_management rabbitmq_prometheus
COPY rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
EXPOSE 5672 15672
"""

    def get_rabbitmq_config(self) -> str:
        return """listeners.tcp.default = 5672
management.tcp.port = 15672
vm_memory_high_watermark.relative = 0.6
"""

    # ==================== KUBERNETES ====================
    
    def generate_kubernetes_manifests(self):
        print("\n☸️  Kubernetes Manifests")
        
        # Base configs
        self.create_file(self.base_path / 'k8s/base/namespace.yaml', self.get_k8s_namespace())
        self.create_file(self.base_path / 'k8s/base/configmap.yaml', self.get_k8s_configmap())
        self.create_file(self.base_path / 'k8s/base/secrets.yaml', self.get_k8s_secrets())
        
        # Databases
        self.create_file(self.base_path / 'k8s/databases/postgres-statefulset.yaml', self.get_k8s_postgres_statefulset())
        self.create_file(self.base_path / 'k8s/databases/redis-statefulset.yaml', self.get_k8s_redis_statefulset())
        
        # Services
        for service_name, config in MICROSERVICES.items():
            service_dir = self.base_path / f'k8s/services/{service_name}'
            self.create_file(service_dir / 'deployment.yaml', self.get_k8s_deployment(service_name, config))
            self.create_file(service_dir / 'service.yaml', self.get_k8s_service(service_name, config))
            self.create_file(service_dir / 'hpa.yaml', self.get_k8s_hpa(service_name, config))
        
        # Ingress & Storage
        self.create_file(self.base_path / 'k8s/ingress/ingress.yaml', self.get_k8s_ingress())
        self.create_file(self.base_path / 'k8s/storage/pvc.yaml', self.get_k8s_pvc())

    def get_k8s_namespace(self) -> str:
        return """apiVersion: v1
kind: Namespace
metadata:
  name: elearning
  labels:
    name: elearning
    environment: production
"""

    def get_k8s_configmap(self) -> str:
        return """apiVersion: v1
kind: ConfigMap
metadata:
  name: elearning-config
  namespace: elearning
data:
  POSTGRES_HOST: postgres-service
  POSTGRES_PORT: "5432"
  REDIS_HOST: redis-service
  REDIS_PORT: "6379"
  RABBITMQ_HOST: rabbitmq-service
  DJANGO_ENV: production
  LOG_LEVEL: INFO
"""

    def get_k8s_secrets(self) -> str:
        return """apiVersion: v1
kind: Secret
metadata:
  name: elearning-secrets
  namespace: elearning
type: Opaque
stringData:
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: changeme_in_production
  SECRET_KEY: changeme_django_secret_key
  RABBITMQ_USER: guest
  RABBITMQ_PASS: guest
  JWT_SECRET_KEY: changeme_jwt_secret
"""

    def get_k8s_postgres_statefulset(self) -> str:
        return """apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: elearning
spec:
  ports:
    - port: 5432
  clusterIP: None
  selector:
    app: postgres
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: elearning
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: elearning-secrets
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: elearning-secrets
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: standard
      resources:
        requests:
          storage: 20Gi
"""

    def get_k8s_redis_statefulset(self) -> str:
        return """apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: elearning
spec:
  ports:
    - port: 6379
  clusterIP: None
  selector:
    app: redis
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
  namespace: elearning
spec:
  serviceName: redis-service
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server", "--appendonly", "yes"]
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: redis-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: standard
      resources:
        requests:
          storage: 5Gi
"""

    def get_k8s_deployment(self, service_name: str, config: Dict) -> str:
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
  namespace: elearning
spec:
  replicas: {config['replicas']}
  selector:
    matchLabels:
      app: {service_name}
  template:
    metadata:
      labels:
        app: {service_name}
    spec:
      containers:
      - name: {service_name}
        image: elearning/{service_name}:latest
        ports:
        - containerPort: {config['port']}
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: elearning-secrets
              key: SECRET_KEY
        - name: DATABASE_URL
          value: postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/{service_name.replace('-', '_')}_db
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health/
            port: {config['port']}
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/health/
            port: {config['port']}
          initialDelaySeconds: 30
          periodSeconds: 10
"""

    def get_k8s_service(self, service_name: str, config: Dict) -> str:
        return f"""apiVersion: v1
kind: Service
metadata:
  name: {service_name}
  namespace: elearning
spec:
  type: ClusterIP
  ports:
  - port: {config['port']}
    targetPort: {config['port']}
  selector:
    app: {service_name}
"""

    def get_k8s_hpa(self, service_name: str, config: Dict) -> str:
        return f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {service_name}-hpa
  namespace: elearning
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {service_name}
  minReplicas: {config['replicas']}
  maxReplicas: {config['replicas'] * 3}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""

    def get_k8s_ingress(self) -> str:
        rules = []
        for service_name, config in MICROSERVICES.items():
            path_prefix = service_name.replace('-service', '')
            rules.append(f"""          - path: /api/{path_prefix}
            pathType: Prefix
            backend:
              service:
                name: {service_name}
                port:
                  number: {config['port']}""")
        
        rules_str = '\n'.join(rules)
        
        return f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: elearning-ingress
  namespace: elearning
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.elearning.com
    secretName: elearning-tls
  rules:
  - host: api.elearning.com
    http:
      paths:
{rules_str}
"""

    def get_k8s_pvc(self) -> str:
        return """apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: media-pvc
  namespace: elearning
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: standard
  resources:
    requests:
      storage: 50Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: static-pvc
  namespace: elearning
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: standard
  resources:
    requests:
      storage: 10Gi
"""

    # ==================== CI/CD PIPELINES ====================
    
    def generate_cicd_pipelines(self):
        print("\n🔄 CI/CD Pipelines")
        
        workflows = {
            '.github/workflows/ci.yml': self.get_github_actions_ci(),
            '.github/workflows/cd.yml': self.get_github_actions_cd(),
            '.github/workflows/test.yml': self.get_github_actions_test(),
            '.github/workflows/security.yml': self.get_github_actions_security(),
        }
        
        for filepath, content in workflows.items():
            self.create_file(self.base_path / filepath, content)

    def get_github_actions_ci(self) -> str:
        return """name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install black flake8 isort mypy
    
    - name: Run Black
      run: black --check .
    
    - name: Run Flake8
      run: flake8 .
    
    - name: Run isort
      run: isort --check-only .

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
        ports:
          - 6379:6379
    
    strategy:
      matrix:
        service: [auth-service, user-service, courses-service]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Run Tests
      working-directory: ./microservices/${{ matrix.service }}
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-django pytest-cov
        pytest --cov=. --cov-report=xml
    
    - name: Upload Coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./microservices/${{ matrix.service }}/coverage.xml

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    strategy:
      matrix:
        service: [auth-service, user-service, courses-service]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Build Docker image
      uses: docker/build-push-action@v4
      with:
        context: ./microservices/${{ matrix.service }}
        file: ./docker/Dockerfile.microservice
        push: false
        tags: elearning/${{ matrix.service }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
"""

    def get_github_actions_cd(self) -> str:
        return """name: CD Pipeline

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        service: [
          auth-service, user-service, courses-service, quizzes-service,
          bookings-service, payments-service, notifications-service,
          webinars-service, gamification-service, chatbot-service,
          analytics-service, communications-service, search-service,
          storage-service, security-service, monitoring-service,
          ai-gateway, cache-service, api-gateway, i18n-service,
          sponsors-service
        ]
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}
        tags: |
          type=ref,event=branch
          type=semver,pattern={{version}}
          type=sha
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: ./microservices/${{ matrix.service }}
        file: ./docker/Dockerfile.microservice
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'latest'
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=./kubeconfig
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/base/
        kubectl apply -f k8s/databases/
        kubectl apply -f k8s/services/
        kubectl apply -f k8s/ingress/
        kubectl rollout status deployment -n elearning --timeout=5m
    
    - name: Verify Deployment
      run: |
        kubectl get pods -n elearning
        kubectl get services -n elearning
"""

    def get_github_actions_test(self) -> str:
        return """name: Tests

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Run Unit Tests
      run: |
        pip install pytest pytest-django
        pytest tests/unit/ -v

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
      rabbitmq:
        image: rabbitmq:3-management-alpine
        ports:
          - 5672:5672
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Run Integration Tests
      run: |
        pip install pytest pytest-django
        pytest tests/integration/ -v

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Start services
      run: docker-compose -f docker-compose.dev.yml up -d
    
    - name: Wait for services
      run: sleep 30
    
    - name: Run E2E Tests
      run: |
        pip install pytest requests
        pytest tests/e2e/ -v
    
    - name: Stop services
      run: docker-compose -f docker-compose.dev.yml down
"""

    def get_github_actions_security(self) -> str:
        return """name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'
  push:
    branches: [ main ]

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Safety Check
      run: |
        pip install safety
        safety check --json || true
    
    - name: Run Bandit
      run: |
        pip install bandit
        bandit -r . -f json -o bandit-report.json || true
    
    - name: Upload Reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: bandit-report.json

  docker-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [auth-service, user-service, courses-service]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build image
      run: |
        docker build -t ${{ matrix.service }} -f docker/Dockerfile.microservice ./microservices/${{ matrix.service }}
    
    - name: Run Trivy scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ matrix.service }}
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
"""

    # ==================== MONITORING ====================
    
    def generate_monitoring_stack(self):
        print("\n📊 Monitoring Stack")
        
        monitoring_files = {
            'monitoring/prometheus/prometheus.yml': self.get_prometheus_config(),
            'monitoring/prometheus/alerts/rules.yml': self.get_prometheus_alerts(),
            'monitoring/grafana/datasources/prometheus.yml': self.get_grafana_datasource(),
            'monitoring/grafana/dashboards/dashboard.json': self.get_grafana_dashboard(),
        }
        
        for filepath, content in monitoring_files.items():
            self.create_file(self.base_path / filepath, content)

    def get_prometheus_config(self) -> str:
        scrape_configs = []
        for service_name, config in MICROSERVICES.items():
            scrape_configs.append(f"""  - job_name: '{service_name}'
    static_configs:
      - targets: ['{service_name}:{config["port"]}']
        labels:
          service: '{service_name}'""")
        
        scrape_str = '\n'.join(scrape_configs)
        
        return f"""global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'elearning'
    environment: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - '/etc/prometheus/alerts/*.yml'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']

{scrape_str}
"""

    def get_prometheus_alerts(self) -> str:
        return """groups:
- name: service_alerts
  interval: 30s
  rules:
  - alert: ServiceDown
    expr: up == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Service {{ $labels.job }} is down"
      description: "{{ $labels.job }} has been down for more than 2 minutes."

  - alert: HighCPUUsage
    expr: rate(process_cpu_seconds_total[5m]) > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage on {{ $labels.job }}"
      description: "CPU usage is above 80% for 5 minutes."

  - alert: HighMemoryUsage
    expr: (process_resident_memory_bytes / 1024 / 1024) > 900
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.job }}"
      description: "Memory usage is above 900MB."

  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate on {{ $labels.job }}"
      description: "Error rate is above 5% for 5 minutes."

- name: database_alerts
  interval: 30s
  rules:
  - alert: PostgreSQLDown
    expr: pg_up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "PostgreSQL is down"
      description: "PostgreSQL database is not responding."

  - alert: HighDatabaseConnections
    expr: pg_stat_database_numbackends > 150
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High number of database connections"
      description: "Number of active connections is above 150."

  - alert: RedisDown
    expr: redis_up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Redis is down"
      description: "Redis cache is not responding."
"""

    def get_grafana_datasource(self) -> str:
        return """apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: "15s"
"""

    def get_grafana_dashboard(self) -> str:
        return """{
  "dashboard": {
    "title": "AI E-Learning Platform Overview",
    "tags": ["microservices", "django"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Services Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{ job }}"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ service }}"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total[5m])",
            "legendFormat": "{{ job }}"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes / 1024 / 1024",
            "legendFormat": "{{ job }}"
          }
        ]
      }
    ]
  }
}
"""

    # ==================== UTILITY SCRIPTS ====================
    
    def generate_utility_scripts(self):
        print("\n🛠️  Utility Scripts")
        
        scripts = {
            'scripts/deploy.sh': (self.get_deploy_script(), 0o755),
            'scripts/rollback.sh': (self.get_rollback_script(), 0o755),
            'scripts/backup.sh': (self.get_backup_script(), 0o755),
            'scripts/restore.sh': (self.get_restore_script(), 0o755),
            'scripts/scale.sh': (self.get_scale_script(), 0o755),
            'scripts/logs.sh': (self.get_logs_script(), 0o755),
            'scripts/health_check.py': (self.get_health_check_script(), 0o755),
            'scripts/load_test.py': (self.get_load_test_script(), 0o755),
            'scripts/db_migrate_all.sh': (self.get_db_migrate_script(), 0o755),
            'scripts/setup_dev.sh': (self.get_setup_dev_script(), 0o755),
        }
        
        for filepath, (content, perm) in scripts.items():
            script_path = self.base_path / filepath
            self.create_file(script_path, content)
            if script_path.exists():
                script_path.chmod(perm)

    def get_deploy_script(self) -> str:
        return """#!/bin/bash
set -e

echo "🚀 Deploying AI E-Learning Platform..."

# Colors
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

ENVIRONMENT=${1:-production}
NAMESPACE="elearning"

echo "${YELLOW}Environment: $ENVIRONMENT${NC}"

# Check prerequisites
check_prerequisites() {
    command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required"; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo "docker is required"; exit 1; }
    echo "${GREEN}✓ Prerequisites OK${NC}"
}

# Build images
build_images() {
    echo "🔨 Building Docker images..."
    docker-compose -f docker-compose.prod.yml build --parallel
    echo "${GREEN}✓ Images built${NC}"
}

# Deploy to K8s
deploy_k8s() {
    echo "☸️  Deploying to Kubernetes..."
    kubectl apply -f k8s/base/
    kubectl apply -f k8s/databases/
    kubectl apply -f k8s/services/
    kubectl apply -f k8s/ingress/
    echo "${GREEN}✓ Kubernetes deployment complete${NC}"
}

# Main
check_prerequisites

if [ "$ENVIRONMENT" = "production" ]; then
    read -p "Deploy to PRODUCTION? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Deployment cancelled"
        exit 0
    fi
fi

build_images
deploy_k8s

echo ""
echo "${GREEN}✨ Deployment complete!${NC}"
"""

    def get_rollback_script(self) -> str:
        return """#!/bin/bash
set -e

echo "⏪ Rolling back deployment..."

NAMESPACE="elearning"
REVISION=${1:-1}

echo "Rolling back to revision: $REVISION"

for deployment in $(kubectl get deployments -n $NAMESPACE -o name); do
    echo "Rolling back $deployment..."
    kubectl rollout undo $deployment -n $NAMESPACE --to-revision=$REVISION
done

echo "✅ Rollback complete!"
"""

    def get_backup_script(self) -> str:
        return """#!/bin/bash
set -e

echo "💾 Starting backup..."

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
echo "Backing up PostgreSQL..."
docker-compose exec -T postgres pg_dumpall -U postgres | gzip > $BACKUP_DIR/postgres.sql.gz

# Backup Redis
echo "Backing up Redis..."
docker-compose exec -T redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb $BACKUP_DIR/

echo "✅ Backup complete: $BACKUP_DIR"
"""

    def get_restore_script(self) -> str:
        return """#!/bin/bash
set -e

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: ./restore.sh <backup_directory>"
    exit 1
fi

echo "♻️  Restoring from: $BACKUP_DIR"

# Restore PostgreSQL
echo "Restoring PostgreSQL..."
gunzip < $BACKUP_DIR/postgres.sql.gz | docker-compose exec -T postgres psql -U postgres

# Restore Redis
echo "Restoring Redis..."
docker-compose exec -T redis redis-cli FLUSHALL
docker cp $BACKUP_DIR/dump.rdb $(docker-compose ps -q redis):/data/
docker-compose restart redis

echo "✅ Restore complete!"
"""

    def get_scale_script(self) -> str:
        return """#!/bin/bash
set -e

SERVICE=$1
REPLICAS=$2

if [ -z "$SERVICE" ] || [ -z "$REPLICAS" ]; then
    echo "Usage: ./scale.sh <service-name> <replicas>"
    exit 1
fi

echo "📈 Scaling $SERVICE to $REPLICAS replicas..."

kubectl scale deployment/$SERVICE -n elearning --replicas=$REPLICAS

echo "✅ Scaled $SERVICE to $REPLICAS replicas"
"""

    def get_logs_script(self) -> str:
        return """#!/bin/bash

SERVICE=$1
LINES=${2:-100}

if [ -z "$SERVICE" ]; then
    echo "Usage: ./logs.sh <service-name> [lines]"
    echo "Available services:"
    kubectl get deployments -n elearning -o name | sed 's/deployment.apps\\///'
    exit 1
fi

echo "📜 Fetching logs for $SERVICE (last $LINES lines)..."

kubectl logs -n elearning deployment/$SERVICE --tail=$LINES -f
"""

    def get_health_check_script(self) -> str:
        services_dict = {name: config['port'] for name, config in MICROSERVICES.items()}
        
        return f"""#!/usr/bin/env python3
\"\"\"Health Check Script for All Services\"\"\"
import requests
import sys

SERVICES = {services_dict}

def check_service_health(service, port):
    try:
        url = f'http://localhost:{{port}}/api/health/'
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"    Error: {{e}}")
        return False

def main():
    print("🏥 Health Check - AI E-Learning Platform\\n")
    
    healthy = []
    unhealthy = []
    
    for service, port in SERVICES.items():
        print(f"Checking {{service}}...", end=" ")
        
        if check_service_health(service, port):
            print("✅ HEALTHY")
            healthy.append(service)
        else:
            print("❌ UNHEALTHY")
            unhealthy.append(service)
    
    print(f"\\n{{'='*50}}")
    print(f"✅ Healthy: {{len(healthy)}}/{{len(SERVICES)}}")
    print(f"❌ Unhealthy: {{len(unhealthy)}}/{{len(SERVICES)}}")
    
    if unhealthy:
        print(f"\\n⚠️  Unhealthy services: {{', '.join(unhealthy)}}")
        sys.exit(1)
    else:
        print("\\n🎉 All services are healthy!")
        sys.exit(0)

if __name__ == '__main__':
    main()
"""

    def get_load_test_script(self) -> str:
        return """#!/usr/bin/env python3
\"\"\"Load Testing Script\"\"\"
import asyncio
import aiohttp
import time
import sys

async def make_request(session, url):
    start_time = time.time()
    try:
        async with session.get(url) as response:
            elapsed = time.time() - start_time
            return {
                'status': response.status,
                'elapsed': elapsed,
                'success': response.status == 200
            }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'status': 0,
            'elapsed': elapsed,
            'success': False,
            'error': str(e)
        }

async def load_test(url, num_requests, concurrency):
    print(f"🔥 Load Testing: {url}")
    print(f"Requests: {num_requests}, Concurrency: {concurrency}\\n")
    
    connector = aiohttp.TCPConnector(limit=concurrency)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [make_request(session, url) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    successful = sum(1 for r in results if r['success'])
    failed = num_requests - successful
    avg_time = sum(r['elapsed'] for r in results) / num_requests
    
    print(f"\\n{'='*50}")
    print(f"✅ Successful: {successful}/{num_requests}")
    print(f"❌ Failed: {failed}/{num_requests}")
    print(f"⏱️  Average Response Time: {avg_time:.3f}s")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python load_test.py <url> [num_requests] [concurrency]")
        sys.exit(1)
    
    url = sys.argv[1]
    num_requests = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    concurrency = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    asyncio.run(load_test(url, num_requests, concurrency))
"""

    def get_db_migrate_script(self) -> str:
        services = " ".join(MICROSERVICES.keys())
        
        return f"""#!/bin/bash
set -e

echo "🔄 Running database migrations for all services..."

SERVICES=({services})

for service in "${{SERVICES[@]}}"; do
    echo ""
    echo "📦 Migrating $service..."
    
    if command -v kubectl &> /dev/null; then
        kubectl exec -n elearning deployment/$service -- python manage.py migrate
    elif command -v docker-compose &> /dev/null; then
        docker-compose exec $service python manage.py migrate
    else
        echo "❌ Neither kubectl nor docker-compose found"
        exit 1
    fi
    
    echo "✅ $service migration complete"
done

echo ""
echo "✨ All migrations complete!"
"""

    def get_setup_dev_script(self) -> str:
        return """#!/bin/bash
set -e

echo "🛠️  Setting up development environment..."

# Check prerequisites
echo "Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required"; exit 1; }

# Create .env if not exists
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=elearning_dev

# Django
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
DJANGO_ENV=development

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
EOF
    echo "✅ Created .env file"
fi

# Start infrastructure
echo "Starting infrastructure services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services
echo "Waiting for services to be ready..."
sleep 15

echo ""
echo "✨ Development environment ready!"
echo ""
echo "📋 Services available:"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - RabbitMQ: localhost:5672 (Management: localhost:15672)"
echo "   - Elasticsearch: localhost:9200"
echo "   - MailHog: localhost:8025"
"""


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Générateur d\'infrastructure DevOps complète',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Générer dans le répertoire courant
  python3 generate_infrastructure.py
  
  # Générer dans un autre répertoire
  python3 generate_infrastructure.py /chemin/vers/projet
  
  # Mode remplacement (écrase les fichiers existants)
  python3 generate_infrastructure.py --overwrite
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default=None,
        help='Chemin du répertoire cible (défaut: répertoire courant)'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Remplacer les fichiers existants'
    )
    
    args = parser.parse_args()
    
    # Déterminer le chemin de base
    if args.path:
        base_path = Path(args.path).resolve()
    else:
        base_path = Path.cwd()
    
    # Vérifier/créer le répertoire
    if not base_path.exists():
        print(f"📁 Le répertoire {base_path} n'existe pas.")
        response = input("Voulez-vous le créer? (o/n): ").lower().strip()
        if response in ['o', 'oui', 'y', 'yes']:
            base_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Répertoire créé")
        else:
            print("Opération annulée")
            sys.exit(0)
    
    # Créer le générateur
    generator = InfrastructureGenerator(
        base_path=base_path,
        overwrite=args.overwrite
    )
    
    # Générer
    try:
        generator.generate_all()
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Opération annulée par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()