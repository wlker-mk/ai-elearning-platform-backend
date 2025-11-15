.PHONY: help install migrate test run docker-up docker-down docker-logs

help:
	@echo "Commandes disponibles:"
	@echo "  make install          - Installer les dépendances"
	@echo "  make migrate          - Appliquer les migrations"
	@echo "  make test             - Lancer les tests"
	@echo "  make run              - Lancer le serveur de développement"
	@echo "  make docker-up        - Démarrer les services Docker"
	@echo "  make docker-down      - Arrêter les services Docker"
	@echo "  make docker-logs      - Voir les logs Docker"
	@echo "  make prisma-generate  - Générer le client Prisma"
	@echo "  make celery-worker    - Lancer le worker Celery"

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

prisma-generate:
	prisma generate

prisma-migrate:
	prisma migrate dev

test:
	pytest

run:
	python manage.py runserver 8003

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

celery-worker:
	celery -A config worker --loglevel=info -Q payments
