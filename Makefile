# Makefile pour AI E-Learning Platform

.PHONY: help build up down logs test migrate shell clean

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construit tous les conteneurs
	docker-compose build

up: ## Démarre tous les services
	docker-compose up -d

down: ## Arrête tous les services
	docker-compose down

logs: ## Affiche les logs
	docker-compose logs -f

test: ## Lance les tests
	pytest tests/

migrate: ## Applique les migrations Prisma
	./scripts/migrate_all.sh

shell: ## Ouvre un shell dans un service
	@read -p "Service name: " service; \
	docker-compose exec $$service bash

clean: ## Nettoie les volumes et conteneurs
	docker-compose down -v
	docker system prune -f

restart: down up ## Redémarre tous les services

ps: ## Liste les services actifs
	docker-compose ps

backup: ## Backup de la base de données
	./scripts/backup.sh

health: ## Vérifie la santé des services
	python scripts/health_check.py
