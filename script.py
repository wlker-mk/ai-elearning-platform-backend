#!/usr/bin/env python3
"""
Script de génération Infrastructure Complète
- Détecte le répertoire courant
- Crée uniquement les fichiers/dossiers manquants
- Préserve les fichiers existants
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
        print("🚀 Génération Infrastructure Complète...")
        print(f"📂 Répertoire: {self.base_path.resolve()}\n")
        
        self.generate_docker_infrastructure()
        self.generate_kubernetes_manifests()
        self.generate_cicd_pipelines()
        self.generate_monitoring_stack()
        self.generate_utility_scripts()
        
        print(f"""
✅ Infrastructure générée avec succès!
📊 Statistiques:
   - Fichiers créés: {self.created}
   - Fichiers ignorés (déjà existants): {self.skipped}
   
📁 Emplacement: {self.base_path.resolve()}

🚀 Prochaines étapes:
   1. cd {self.base_path.resolve()}
   2. ./scripts/setup_dev.sh
        """)
        
    def create_file(self, path: Path, content: str):
        """Crée un fichier uniquement s'il n'existe pas"""
        # Créer les dossiers parents
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

    # ==================== DOCKER ====================
    
    def generate_docker_infrastructure(self):
        print("\n🐳 Docker Infrastructure")
        
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
      - DATABASE_URL=postgresql://\${{POSTGRES_USER}}:\${{POSTGRES_PASSWORD}}@postgres:5432/{service_name.replace('-', '_')}_db
      - REDIS_URL=redis://redis:6379
      - RABBITMQ_URL=amqp://\${{RABBITMQ_USER}}:\${{RABBITMQ_PASS}}@rabbitmq:5672
      - SECRET_KEY=\${{SECRET_KEY}}
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
        
        return f"""version: '3.8'

networks:
  elearning-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
  rabbitmq_data:

services:
  postgres:
    build: ./docker/postgres
    image: elearning/postgres:15
    container_name: elearning-postgres
    restart: always
    environment:
      POSTGRES_USER: \${{POSTGRES_USER}}
      POSTGRES_PASSWORD: \${{POSTGRES_PASSWORD}}
      POSTGRES_DB: elearning
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-scripts:/docker-entrypoint-initdb.d
    networks:
      - elearning-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${{POSTGRES_USER}}"]
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
      RABBITMQ_DEFAULT_USER: \${{RABBITMQ_USER}}
      RABBITMQ_DEFAULT_PASS: \${{RABBITMQ_PASS}}
    ports:
      - "5672:5672"
      - "15672:15672"
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
    depends_on:
{chr(10).join(f"      - {name}" for name in MICROSERVICES.keys())}
    networks:
      - elearning-network

{chr(10).join(services)}
"""

    def get_docker_compose_development(self) -> str:
        return """version: '3.8'

networks:
  elearning-dev-network:
    driver: bridge

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
    networks:
      - elearning-dev-network

  redis:
    image: redis:7-alpine
    container_name: elearning-redis-dev
    ports:
      - "6379:6379"
    networks:
      - elearning-dev-network
"""

    def get_dockerfile_multistage(self) -> str:
        return """FROM python:3.11-slim as builder
WORKDIR /build
RUN apt-get update && apt-get install -y gcc postgresql-client libpq-dev
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN useradd -m appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
"""

    def get_nginx_production_config(self) -> str:
        return """user nginx;
worker_processes auto;
events {
    worker_connections 1024;
}
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    upstream backend {
        server api-gateway:8019;
    }
    
    server {
        listen 80;
        server_name _;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
"""

    def get_nginx_dockerfile(self) -> str:
        return """FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""

    def get_postgres_dockerfile(self) -> str:
        return """FROM postgres:15-alpine
COPY init-scripts/ /docker-entrypoint-initdb.d/
EXPOSE 5432
"""

    def get_postgres_init_sql(self) -> str:
        dbs = [name.replace('-', '_') + '_db' for name in MICROSERVICES.keys()]
        sql = "-- Auto-generated databases\n\n"
        for db in dbs:
            sql += f"CREATE DATABASE {db};\n"
        return sql

    def get_redis_dockerfile(self) -> str:
        return """FROM redis:7-alpine
COPY redis.conf /usr/local/etc/redis/redis.conf
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
"""

    def get_redis_config(self) -> str:
        return """bind 0.0.0.0
port 6379
appendonly yes
"""

    def get_elasticsearch_dockerfile(self) -> str:
        return """FROM docker.elastic.co/elasticsearch/elasticsearch:8.11.0
COPY elasticsearch.yml /usr/share/elasticsearch/config/
EXPOSE 9200
"""

    def get_elasticsearch_config(self) -> str:
        return """cluster.name: elearning-cluster
network.host: 0.0.0.0
discovery.type: single-node
xpack.security.enabled: false
"""

    def get_rabbitmq_dockerfile(self) -> str:
        return """FROM rabbitmq:3-management-alpine
COPY rabbitmq.conf /etc/rabbitmq/
EXPOSE 5672 15672
"""

    def get_rabbitmq_config(self) -> str:
        return """listeners.tcp.default = 5672
management.tcp.port = 15672
"""

    # ==================== KUBERNETES ====================
    
    def generate_kubernetes_manifests(self):
        print("\n☸️  Kubernetes Manifests")
        
        self.create_file(self.base_path / 'k8s/base/namespace.yaml', self.get_k8s_namespace())
        self.create_file(self.base_path / 'k8s/base/configmap.yaml', self.get_k8s_configmap())
        self.create_file(self.base_path / 'k8s/base/secrets.yaml', self.get_k8s_secrets())
        
        for service_name, config in MICROSERVICES.items():
            service_dir = self.base_path / f'k8s/services/{service_name}'
            self.create_file(service_dir / 'deployment.yaml', self.get_k8s_deployment(service_name, config))
            self.create_file(service_dir / 'service.yaml', self.get_k8s_service(service_name, config))
            self.create_file(service_dir / 'hpa.yaml', self.get_k8s_hpa(service_name, config))

    def get_k8s_namespace(self) -> str:
        return """apiVersion: v1
kind: Namespace
metadata:
  name: elearning
"""

    def get_k8s_configmap(self) -> str:
        return """apiVersion: v1
kind: ConfigMap
metadata:
  name: elearning-config
  namespace: elearning
data:
  POSTGRES_HOST: postgres-service
  REDIS_HOST: redis-service
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
  POSTGRES_PASSWORD: changeme
  SECRET_KEY: changeme_secret
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
  maxReplicas: {config['replicas'] * 2}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
"""

    # ==================== CI/CD ====================
    
    def generate_cicd_pipelines(self):
        print("\n🔄 CI/CD Pipelines")
        
        workflows = {
            '.github/workflows/ci.yml': self.get_github_actions_ci(),
            '.github/workflows/cd.yml': self.get_github_actions_cd(),
        }
        
        for filepath, content in workflows.items():
            self.create_file(self.base_path / filepath, content)

    def get_github_actions_ci(self) -> str:
        return """name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Run tests
      run: |
        pip install pytest
        pytest
"""

    def get_github_actions_cd(self) -> str:
        return """name: CD Pipeline

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to K8s
      run: |
        kubectl apply -f k8s/
"""

    # ==================== MONITORING ====================
    
    def generate_monitoring_stack(self):
        print("\n📊 Monitoring Stack")
        
        self.create_file(
            self.base_path / 'monitoring/prometheus/prometheus.yml',
            self.get_prometheus_config()
        )
        self.create_file(
            self.base_path / 'monitoring/grafana/datasources/prometheus.yml',
            self.get_grafana_datasource()
        )

    def get_prometheus_config(self) -> str:
        return """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'services'
    static_configs:
      - targets: ['localhost:9090']
"""

    def get_grafana_datasource(self) -> str:
        return """apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
"""

    # ==================== SCRIPTS ====================
    
    def generate_utility_scripts(self):
        print("\n🛠️  Utility Scripts")
        
        scripts = {
            'scripts/setup_dev.sh': (self.get_setup_dev_script(), 0o755),
            'scripts/deploy.sh': (self.get_deploy_script(), 0o755),
            'scripts/health_check.py': (self.get_health_check_script(), 0o755),
        }
        
        for filepath, (content, perm) in scripts.items():
            script_path = self.base_path / filepath
            self.create_file(script_path, content)
            if script_path.exists():
                script_path.chmod(perm)

    def get_setup_dev_script(self) -> str:
        return """#!/bin/bash
echo "🛠️  Setting up development environment..."
docker-compose -f docker-compose.dev.yml up -d
echo "✅ Done!"
"""

    def get_deploy_script(self) -> str:
        return """#!/bin/bash
echo "🚀 Deploying..."
kubectl apply -f k8s/
echo "✅ Deployed!"
"""

    def get_health_check_script(self) -> str:
        return """#!/usr/bin/env python3
import requests

services = """ + str({name: config['port'] for name, config in MICROSERVICES.items()}) + """

for service, port in services.items():
    try:
        r = requests.get(f'http://localhost:{port}/health', timeout=2)
        print(f"✓ {service}: OK")
    except:
        print(f"✗ {service}: FAIL")
"""


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Générateur d\'infrastructure DevOps')
    parser.add_argument('path', nargs='?', default=None, help='Chemin du répertoire cible')
    parser.add_argument('--overwrite', action='store_true', help='Remplacer les fichiers existants')
    
    args = parser.parse_args()
    
    # Déterminer le chemin
    base_path = Path(args.path) if args.path else Path.cwd()
    
    # Créer le répertoire si nécessaire
    if not base_path.exists():
        print(f"📁 Création du répertoire: {base_path}")
        base_path.mkdir(parents=True, exist_ok=True)
    
    # Générer
    generator = InfrastructureGenerator(base_path=base_path, overwrite=args.overwrite)
    generator.generate_all()


if __name__ == '__main__':
    main()