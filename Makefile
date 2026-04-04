.PHONY: install run-analytics run-advanced docker-build docker-up-analytics docker-up-advanced docker-down docker-logs help

# Local development commands
install:
	@echo "Installing dependencies with Poetry..."
	poetry install

run-analytics:
	@echo "Running game analytics dashboard..."
	poetry run streamlit run game_dashboard/game_analytics.py

run-advanced:
	@echo "Running advanced Streamlit dashboard..."
	poetry run streamlit run game_dashboard/advanced.py

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker-compose build

docker-up-analytics:
	@echo "Starting analytics dashboard in Docker..."
	docker-compose up streamlit-analytics

docker-up-advanced:
	@echo "Starting advanced dashboard in Docker..."
	docker-compose up streamlit-advanced

docker-up:
	@echo "Starting all services in Docker..."
	docker-compose up -d

docker-down:
	@echo "Stopping all Docker services..."
	docker-compose down

docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

docker-restart:
	@echo "Restarting Docker services..."
	docker-compose restart

# Help command
help:
	@echo "Available commands:"
	@echo "  make install                - Install dependencies with Poetry"
	@echo "  make run-analytics          - Run game analytics dashboard locally"
	@echo "  make run-advanced           - Run advanced dashboard locally"
	@echo "  make docker-build           - Build Docker images"
	@echo "  make docker-up-analytics    - Start analytics dashboard in Docker"
	@echo "  make docker-up-advanced     - Start advanced dashboard in Docker"
	@echo "  make docker-up              - Start all services in Docker (detached)"
	@echo "  make docker-down            - Stop all Docker services"
	@echo "  make docker-logs            - Show Docker logs"
	@echo "  make docker-restart         - Restart Docker services"
