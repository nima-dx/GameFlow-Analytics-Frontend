FROM python:3.12.8-slim

# Do not use env as this would persist after the build and would impact your containers, children images
ARG DEBIAN_FRONTEND=noninteractive

# Force the stdout and stderr streams to be unbuffered
ENV PYTHONUNBUFFERED=1

# Set environment variable for Google credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json

# Setup workdir
WORKDIR /app

# Copy project configuration and code
COPY ./pyproject.toml ./pyproject.toml
COPY ./poetry.lock ./poetry.lock
COPY ./game_dashboard ./game_dashboard
COPY ./.streamlit ./.streamlit

# Install dependencies
RUN apt-get update \
    && apt-get -y upgrade \
    && pip3 install --no-cache-dir poetry \
    && poetry install --only main \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose Streamlit default port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default command
CMD ["poetry", "run", "streamlit", "run", "game_dashboard/game_analytics.py", "--server.port=8501", "--server.address=0.0.0.0"]
