# --- Build Stage ---
# Use an official Python runtime as a parent image (builder stage)
FROM python:3.11.6-slim as builder

# Set environment variables
# Python won't try to write .pyc files
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.0 \
    POETRY_HOME="/opt/poetry" \
    PATH="$POETRY_HOME/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=taskmanager.production

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev build-essential procps
RUN pip install "poetry==$POETRY_VERSION"

# Copy the project files into the builder stage
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# Copy the rest of the application's code
COPY taskmanager /app

# Collect static files
RUN poetry run python manage.py collectstatic --noinput

# --- Production Stage ---
# Define the base image for the production stage
FROM python:3.11.6-slim as production

# Copy virtual env and other necessary files from builder stage
# Copy installed packages and binaries from builder stage
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Set the working directory in the container
WORKDIR /app

# Set user to use when running the image
# UID 1000 is often the default user
RUN groupadd -r django && useradd --no-log-init -r -g django django && \
    chown -R django:django /app
USER django

# Start Gunicorn with a configuration file
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "taskmanager.wsgi"]

# Inform Docker that the container listens on the specified network ports at runtime
EXPOSE 8000
