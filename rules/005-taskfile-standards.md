### 005 Taskfile Standards

#### Core Principles

- **Use Taskfiles for Common Tasks**: All common project tasks should be defined in Taskfiles
- **Compose/Cascade Pattern**: Break large Taskfiles into smaller, focused files using includes
- **Self-Documenting**: Every task should have a clear description
- **Idempotent**: Tasks should be safe to run multiple times

#### File Organization

Use the compose/cascade pattern to organize Taskfiles by domain:

```yaml
# Taskfile.yml (root)
version: "3"

includes:
  dev: ./taskfiles/Taskfile.dev.yml
  build: ./taskfiles/Taskfile.build.yml
  test: ./taskfiles/Taskfile.test.yml
  infra: ./taskfiles/Taskfile.infra.yml
  docker: ./taskfiles/Taskfile.docker.yml

tasks:
  default:
    desc: Show available task namespaces
    cmds:
      - task --list
```

**Directory Structure:**

```
project/
├── Taskfile.yml              # Root taskfile with includes
└── taskfiles/
    ├── Taskfile.dev.yml      # Development tasks (run, watch, lint)
    ├── Taskfile.build.yml    # Build tasks (compile, package)
    ├── Taskfile.test.yml     # Testing tasks (unit, integration, e2e)
    ├── Taskfile.infra.yml    # Infrastructure tasks (terraform, deploy)
    └── Taskfile.docker.yml   # Docker tasks (build, push, compose)
```

#### Task Design

**Good Task Structure:**

```yaml
tasks:
  start:
    desc: Start the development server
    summary: |
      Starts the development server with hot reload enabled.
      Requires: Python 3.11+, dependencies installed
      Port: 8000 (configurable via DEV_PORT env var)
    deps:
      - install-deps
    vars:
      PORT: '{{.DEV_PORT | default "8000"}}'
    env:
      ENVIRONMENT: development
    cmds:
      - echo "Starting server on port {{.PORT}}"
      - python -m uvicorn app.main:app --reload --port {{.PORT}}
    sources:
      - src/**/*.py
      - pyproject.toml
    generates:
      - .dev-server.pid
```

**Key Elements:**

- **desc**: Short one-line description (shows in `task --list`)
- **summary**: Detailed multi-line description (shows in `task --summary <task>`)
- **deps**: Dependencies that run before this task
- **vars**: Task-specific variables with defaults
- **env**: Environment variables for the task
- **sources/generates**: For incremental builds (task skips if up-to-date)

#### Naming Conventions

**Task Names:**

- Use kebab-case: `build-docker`, `run-tests`, `deploy-prod`
- Use verb-noun pattern: `start-server`, `clean-cache`, `install-deps`
- Group related tasks with prefixes when not using includes:
  - `test:unit`, `test:integration`, `test:e2e`
  - `docker:build`, `docker:push`, `docker:run`

**Namespace Names (includes):**

- Short, clear names: `dev`, `test`, `build`, `infra`, `docker`
- Use singular form: `build` not `builds`

#### Common Patterns

**1. Development Workflow:**

```yaml
# taskfiles/Taskfile.dev.yml
version: "3"

tasks:
  setup:
    desc: Set up development environment
    cmds:
      - task: install-deps
      - task: setup-git-hooks
      - task: create-env-file

  run:
    desc: Run the application in development mode
    deps: [install-deps]
    cmds:
      - python -m app.main

  watch:
    desc: Run with auto-reload on file changes
    deps: [install-deps]
    cmds:
      - watchexec -e py,yaml task dev:run

  lint:
    desc: Run linters and formatters
    cmds:
      - ruff check .
      - ruff format --check .
      - mypy src/

  format:
    desc: Auto-format code
    cmds:
      - ruff format .
      - ruff check --fix .
```

**2. Testing Workflow:**

```yaml
# taskfiles/Taskfile.test.yml
version: "3"

tasks:
  unit:
    desc: Run unit tests
    cmds:
      - pytest tests/unit -v --cov=src

  integration:
    desc: Run integration tests
    deps: [docker:up]
    cmds:
      - pytest tests/integration -v

  e2e:
    desc: Run end-to-end tests
    deps: [docker:up]
    cmds:
      - pytest tests/e2e -v

  all:
    desc: Run all tests
    cmds:
      - task: unit
      - task: integration
      - task: e2e

  coverage:
    desc: Generate test coverage report
    cmds:
      - pytest --cov=src --cov-report=html --cov-report=term
      - echo "Coverage report: htmlcov/index.html"
```

**3. Build Workflow:**

```yaml
# taskfiles/Taskfile.build.yml
version: "3"

vars:
  VERSION:
    sh: git describe --tags --always --dirty
  BUILD_TIME:
    sh: date -u +"%Y-%m-%dT%H:%M:%SZ"

tasks:
  clean:
    desc: Clean build artifacts
    cmds:
      - rm -rf dist/ build/ *.egg-info
      - find . -type d -name __pycache__ -exec rm -rf {} +

  compile:
    desc: Compile source code
    deps: [clean]
    cmds:
      - python -m build

  package:
    desc: Create distribution package
    deps: [compile]
    cmds:
      - python -m build --wheel
      - echo "Built version {{.VERSION}}"

  verify:
    desc: Verify build artifacts
    deps: [package]
    cmds:
      - twine check dist/*
```

**4. Infrastructure Workflow:**

```yaml
# taskfiles/Taskfile.infra.yml
version: "3"

tasks:
  init:
    desc: Initialize Terraform
    dir: terraform/
    cmds:
      - terraform init

  plan:
    desc: Plan infrastructure changes
    dir: terraform/
    deps: [init]
    cmds:
      - terraform plan -out=tfplan

  apply:
    desc: Apply infrastructure changes
    dir: terraform/
    deps: [plan]
    prompt: This will modify infrastructure. Continue?
    cmds:
      - terraform apply tfplan

  destroy:
    desc: Destroy infrastructure
    dir: terraform/
    prompt: This will DESTROY infrastructure. Are you sure?
    cmds:
      - terraform destroy

  validate:
    desc: Validate Terraform configuration
    dir: terraform/
    cmds:
      - terraform fmt -check
      - terraform validate
```

**5. Docker Workflow:**

```yaml
# taskfiles/Taskfile.docker.yml
version: "3"

vars:
  IMAGE_NAME: ehub-core
  REGISTRY: ghcr.io/yourorg

tasks:
  build:
    desc: Build Docker image
    cmds:
      - docker build -t {{.IMAGE_NAME}}:latest .
      - docker tag {{.IMAGE_NAME}}:latest {{.IMAGE_NAME}}:{{.VERSION}}

  push:
    desc: Push Docker image to registry
    deps: [build]
    cmds:
      - docker tag {{.IMAGE_NAME}}:latest {{.REGISTRY}}/{{.IMAGE_NAME}}:latest
      - docker push {{.REGISTRY}}/{{.IMAGE_NAME}}:latest

  up:
    desc: Start Docker Compose services
    cmds:
      - docker compose up -d

  down:
    desc: Stop Docker Compose services
    cmds:
      - docker compose down

  logs:
    desc: Show Docker Compose logs
    cmds:
      - docker compose logs -f
```

#### Environment Variables

**Use .env files for configuration:**

```yaml
# Taskfile.yml
version: "3"

dotenv: [".env", ".env.local"]

tasks:
  example:
    desc: Task using environment variables
    cmds:
      - echo "Environment: $ENVIRONMENT"
      - echo "Database: $DATABASE_URL"
```

**Provide defaults:**

```yaml
tasks:
  deploy:
    desc: Deploy application
    vars:
      ENVIRONMENT: '{{.ENVIRONMENT | default "development"}}'
      REGION: '{{.AWS_REGION | default "us-east-1"}}'
    cmds:
      - echo "Deploying to {{.ENVIRONMENT}} in {{.REGION}}"
```

#### Best Practices

1. **Always Add Descriptions**: Every task should have a `desc` field
2. **Use Dependencies**: Leverage `deps` to ensure prerequisites are met
3. **Make Tasks Idempotent**: Safe to run multiple times without side effects
4. **Use Prompts for Destructive Operations**: Add `prompt` for dangerous tasks
5. **Leverage sources/generates**: For incremental builds and caching
6. **Keep Tasks Focused**: Each task should do one thing well
7. **Document Complex Tasks**: Use `summary` for detailed explanations
8. **Use Variables**: Make tasks configurable with `vars` and env vars
9. **Group Related Tasks**: Use includes to organize by domain
10. **Provide a Default Task**: Show available tasks or common starting point

#### Anti-Patterns to Avoid

❌ **Monolithic Taskfile**: Don't put all tasks in one file
❌ **No Descriptions**: Tasks without `desc` are hard to discover
❌ **Hardcoded Values**: Use variables and environment variables
❌ **Silent Tasks**: Always provide feedback on what's happening
❌ **No Error Handling**: Use `ignore_error: true` or proper error handling
❌ **Duplicate Logic**: Extract common patterns into reusable tasks
