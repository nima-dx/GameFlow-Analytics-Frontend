# GameFlow Analytics Dashboard

A Streamlit dashboard for Formula 1 analytics powered by Google BigQuery.

## Prerequisites

- Python 3.12+
- Poetry for dependency management (local development)
- Docker & Docker Compose (for containerized deployment)
- Google Cloud Platform account with BigQuery enabled
- Service account credentials JSON file

## Setup

### 1. Google Cloud Credentials

Ensure your service account JSON file is located at:
```
~/.gcp_keys/le-wagon-de-bootcamp.json
```

### 2. Environment Configuration

Copy `.env.sample` to `.env`:
```bash
cp .env.sample .env
```

Update `.env` with your BigQuery details:
```env
GCP_PROJECT_ID=le-wagon-data-atelier
GCP_DATASET_ID=sales_mart
GOOGLE_APPLICATION_CREDENTIALS=/home/nima.lewagon.de/.gcp_keys/le-wagon-de-bootcamp.json
```

### 3. Streamlit Secrets

The `.streamlit/secrets.toml` file is already configured with:
```toml
[bigquery]
project_id = "le-wagon-data-atelier"
dataset_id = "sales_mart"
credentials_path = "/home/nima.lewagon.de/.gcp_keys/le-wagon-de-bootcamp.json"
```

Update if needed for your environment.

## Running the Dashboard

### Option 1: Local Development (with Poetry)

#### Install dependencies:
```bash
make install
# or
poetry install
```

#### Run Game Analytics Dashboard:
```bash
make run-analytics
# or
poetry run streamlit run game_dashboard/game_analytics.py
```

#### Run Advanced Dashboard (Multi-page):
```bash
make run-advanced
# or
poetry run streamlit run game_dashboard/advanced.py
```

### Option 2: Docker Deployment

#### Build the Docker image:
```bash
make docker-build
# or
docker-compose build
```

#### Run Analytics Dashboard (port 8501):
```bash
make docker-up-analytics
# or
docker-compose up streamlit-analytics
```

#### Run Advanced Dashboard (port 8502):
```bash
make docker-up-advanced
# or
docker-compose up streamlit-advanced
```

#### Run all services in detached mode:
```bash
make docker-up
# or
docker-compose up -d
```

#### View logs:
```bash
make docker-logs
# or
docker-compose logs -f
```

#### Stop services:
```bash
make docker-down
# or
docker-compose down
```

## Access the Dashboard

- **Local Development**:
  - Analytics: http://localhost:8501
  - Advanced: http://localhost:8501
- **Docker**:
  - Analytics: http://localhost:8501
  - Advanced: http://localhost:8502

## Project Structure

```
game_dashboard/
├── game_analytics.py           # Game analytics dashboard
├── advanced.py                 # Multi-page dashboard entry point
├── pages/
│   ├── 01_descriptives.py     # Descriptive statistics page
│   └── 02_visualizations.py   # Data visualizations page
└── advanced/
    ├── database.py            # BigQuery connection handler
    ├── queries.py             # SQL queries for BigQuery
    ├── state.py               # Session state management
    └── constants.py           # Constants (table names, etc.)
```

## Features

- **Table Explorer**: Browse and analyze all tables in your BigQuery dataset
- **Summary Statistics**: View descriptive statistics for any table
- **Top Drivers Analysis**: Bar chart showing top 5 drivers by points
- **Historical Trends**: Line chart tracking driver performance over time
- **Session State Caching**: Improved performance with intelligent data caching

## BigQuery Configuration

The dashboard connects to:
- **Project ID**: `le-wagon-data-atelier`
- **Dataset ID**: `sales_mart`

Update these values in `.env` and `.streamlit/secrets.toml` to connect to a different dataset.

## Available Make Commands

Run `make help` to see all available commands:

```bash
make install                # Install dependencies with Poetry
make run-analytics          # Run game analytics dashboard locally
make run-advanced           # Run advanced dashboard locally
make docker-build           # Build Docker images
make docker-up-analytics    # Start analytics dashboard in Docker
make docker-up-advanced     # Start advanced dashboard in Docker
make docker-up              # Start all services in Docker (detached)
make docker-down            # Stop all Docker services
make docker-logs            # Show Docker logs
make docker-restart         # Restart Docker services
```

## Troubleshooting

### Credentials Issues
If you encounter authentication errors:
1. Verify credentials file exists: `ls -l ~/.gcp_keys/le-wagon-de-bootcamp.json`
2. Check file permissions: Should be readable
3. Verify the path in `.streamlit/secrets.toml` matches your actual credential location

### Docker Volume Mounting
The Docker setup mounts your Google Cloud credentials from your home directory. If running on a different system, update the volume path in `docker-compose.yml`:
```yaml
volumes:
  - /your/path/to/credentials.json:/app/credentials/gcp-key.json:ro
```

### Port Conflicts
If ports 8501 or 8502 are already in use, update the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "9501:8501"  # Change left side to available port
```
