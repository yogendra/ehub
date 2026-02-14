### 006 Python & Local Development Standards

#### Python Environment Management

**Use Conda for Python Environment Management**

Conda provides consistent, reproducible Python environments across different platforms and simplifies dependency management.

**Environment Setup:**

```yaml
# environment.yml
name: ehub
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - pip:
      - -r requirements.txt
```

**Best Practices:**

- **One Environment Per Project**: Create isolated conda environments for each project
- **Pin Python Version**: Specify exact Python version in `environment.yml`
- **Use environment.yml**: Define conda dependencies in `environment.yml`
- **Use requirements.txt for pip**: Keep pip-only packages in `requirements.txt`
- **Lock Dependencies**: Generate `conda-lock.yml` or `requirements-lock.txt` for reproducibility

**Common Commands:**

```bash
# Create environment
conda env create -f environment.yml

# Activate environment
conda activate ehub

# Update environment
conda env update -f environment.yml --prune

# Export environment (for sharing)
conda env export --no-builds > environment-lock.yml

# Remove environment
conda env remove -n ehub
```

**Directory Structure:**

```
project/
├── environment.yml           # Conda environment definition
├── requirements.txt          # Pip dependencies
├── requirements-dev.txt      # Development dependencies
├── requirements-lock.txt     # Locked versions (optional)
└── .python-version          # Python version for pyenv compatibility
```

#### Dependency Management

**Separate Production and Development Dependencies:**

```txt
# requirements.txt (production)
temporalio>=1.5.0,<2.0.0
pydantic>=2.0.0,<3.0.0
httpx>=0.25.0,<1.0.0

# requirements-dev.txt (development)
-r requirements.txt
pytest>=7.4.0
pytest-cov>=4.1.0
ruff>=0.1.0
mypy>=1.7.0
black>=23.0.0
```

**Version Pinning Strategy:**

- **Production**: Use compatible release (`>=1.5.0,<2.0.0`) for flexibility
- **Lock Files**: Pin exact versions in lock files for reproducibility
- **Development**: Can be more lenient, but test with production constraints

#### Local Testing with Docker

**Use Docker and Docker Compose for Local Testing**

Docker ensures consistency between development, testing, and production environments.

**Docker Compose Structure:**

```yaml
# docker-compose.yml
version: "3.8"

services:
  # Temporal server for workflow testing
  temporal:
    image: temporalio/auto-setup:latest
    ports:
      - "7233:7233"
      - "8233:8233"
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=temporal
      - POSTGRES_PWD=temporal
      - POSTGRES_SEEDS=postgres
    depends_on:
      - postgres
    networks:
      - ehub-network

  # PostgreSQL for Temporal
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: temporal
      POSTGRES_PASSWORD: temporal
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - ehub-network

  # Application service
  ehub-core:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - TEMPORAL_HOST=temporal:7233
      - DATABASE_URL=postgresql://temporal:temporal@postgres:5432/temporal
    depends_on:
      - temporal
      - postgres
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
    networks:
      - ehub-network
    command: python -m pytest tests/

networks:
  ehub-network:
    driver: bridge

volumes:
  postgres-data:
```

**Multi-Stage Dockerfile:**

```dockerfile
# Dockerfile
FROM continuumio/miniconda3:latest AS base

WORKDIR /app

# Copy environment files
COPY environment.yml requirements.txt ./

# Create conda environment
RUN conda env create -f environment.yml && \
    conda clean -afy

# Activate environment
SHELL ["conda", "run", "-n", "ehub", "/bin/bash", "-c"]

# Development stage
FROM base AS development
COPY requirements-dev.txt ./
RUN conda run -n ehub pip install -r requirements-dev.txt
COPY . .
CMD ["conda", "run", "-n", "ehub", "python", "-m", "app.main"]

# Production stage
FROM base AS production
COPY . .
RUN conda run -n ehub pip install --no-cache-dir -r requirements.txt
CMD ["conda", "run", "-n", "ehub", "python", "-m", "app.main"]
```

#### Local Testing Workflow

**1. Development Setup:**

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Run tests in container
docker compose run --rm ehub-core pytest

# Stop services
docker compose down
```

**2. Integration Testing:**

```yaml
# docker-compose.test.yml
version: "3.8"

services:
  test-runner:
    build:
      context: .
      target: development
    environment:
      - TEMPORAL_HOST=temporal:7233
      - TEST_MODE=integration
    depends_on:
      - temporal
      - postgres
    command: pytest tests/integration -v
    networks:
      - ehub-network
```

**3. Taskfile Integration:**

```yaml
# taskfiles/Taskfile.dev.yml
version: "3"

tasks:
  setup:
    desc: Set up local development environment
    cmds:
      - conda env create -f environment.yml
      - task: docker:build

  test:local:
    desc: Run tests locally (no Docker)
    cmds:
      - conda run -n ehub pytest tests/unit -v

  test:integration:
    desc: Run integration tests with Docker
    cmds:
      - docker compose up -d temporal postgres
      - sleep 5 # Wait for services to be ready
      - docker compose run --rm ehub-core pytest tests/integration -v
      - docker compose down

  test:all:
    desc: Run all tests in Docker environment
    cmds:
      - docker compose -f docker-compose.test.yml up --abort-on-container-exit
      - docker compose -f docker-compose.test.yml down
```

#### Best Practices

**Conda:**

- ✅ Use `conda-forge` channel for most packages
- ✅ Keep `environment.yml` minimal (core dependencies only)
- ✅ Use pip for Python-only packages within conda environment
- ✅ Document environment setup in README
- ✅ Add `.conda/` to `.gitignore`

**Docker:**

- ✅ Use multi-stage builds to optimize image size
- ✅ Separate development and production stages
- ✅ Use `.dockerignore` to exclude unnecessary files
- ✅ Pin base image versions (`postgres:15-alpine`, not `postgres:latest`)
- ✅ Use volumes for development (hot reload)
- ✅ Use health checks for service dependencies
- ✅ Clean up containers and volumes regularly

**Docker Compose:**

- ✅ Use named volumes for persistent data
- ✅ Define custom networks for service isolation
- ✅ Use environment files (`.env`) for configuration
- ✅ Separate compose files for different purposes:
  - `docker-compose.yml` - Development
  - `docker-compose.test.yml` - Testing
  - `docker-compose.prod.yml` - Production-like local testing
- ✅ Use `depends_on` with health checks for proper startup order
- ✅ Document all services and their purposes

#### Environment Variables

**Use .env file for local configuration:**

```bash
# .env (gitignored)
TEMPORAL_HOST=localhost:7233
AWS_REGION=us-east-1
LOG_LEVEL=DEBUG

# .env.example (committed to git)
TEMPORAL_HOST=localhost:7233
AWS_REGION=us-east-1
LOG_LEVEL=INFO
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
```

**Load in Docker Compose:**

```yaml
services:
  ehub-core:
    env_file:
      - .env
    environment:
      - ENVIRONMENT=development
```

#### Testing Strategy

**Test Pyramid:**

1. **Unit Tests** (70%): Run locally with conda, no Docker needed
2. **Integration Tests** (20%): Run with Docker Compose (Temporal + DB)
3. **E2E Tests** (10%): Run with full Docker Compose stack

**Example Test Structure:**

```
tests/
├── unit/                    # Fast, no external dependencies
│   ├── test_workflows.py
│   └── test_activities.py
├── integration/             # Requires Docker services
│   ├── test_temporal_integration.py
│   └── test_database.py
└── e2e/                     # Full stack tests
    └── test_complete_workflow.py
```

#### Anti-Patterns to Avoid

❌ **Don't use virtualenv/venv**: Use conda for consistency  
❌ **Don't use `latest` tags**: Pin versions in Docker images  
❌ **Don't commit .env files**: Use `.env.example` instead  
❌ **Don't run tests without isolation**: Always use conda or Docker  
❌ **Don't mix package managers**: Choose conda or pip, document clearly  
❌ **Don't skip Docker cleanup**: Regularly prune unused containers/volumes  
❌ **Don't hardcode localhost**: Use service names in Docker Compose
