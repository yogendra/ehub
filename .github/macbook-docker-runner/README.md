# GitHub Actions Self-Hosted Runner (Docker)

This directory contains the setup for running a GitHub Actions self-hosted runner in a Docker container on macOS.

## Prerequisites

- Docker Desktop for Mac installed and running
- GitHub Personal Access Token (PAT) with `repo` scope
- Task (taskfile) installed (`brew install go-task/tap/go-task`)

## Environment Variables

The runner requires the following environment variables, which are loaded from `../../.env`:

- `GITHUB_PAT`: Your GitHub Personal Access Token with `repo` scope
- `REPO_URL`: The URL of your GitHub repository (e.g., `https://github.com/yogendra/ehub`)

Optional variables:

- `RUNNER_NAME`: Name for the runner (default: `macbook-docker-runner`)
- `RUNNER_LABELS`: Comma-separated labels (default: `self-hosted,mac-docker,arm64`)

## Quick Start

### 1. Build and Run

```bash
cd .github/macbook-docker-runner
task run
```

This will:

- Build the Docker image
- Start the runner container
- Register the runner with your GitHub repository

### 2. Check Status

```bash
task status
```

### 3. View Logs

```bash
task logs
```

### 4. Stop the Runner

```bash
task stop
```

## Available Tasks

- `task build` - Build the Docker image
- `task run` - Build and run the runner container
- `task stop` - Stop the runner container
- `task remove` - Remove the runner container
- `task restart` - Restart the runner (stop, remove, run)
- `task logs` - View container logs (follows)
- `task shell` - Open a bash shell in the container
- `task status` - Check container status
- `task clean` - Remove container and Docker image

## How It Works

1. **Dockerfile**: Creates an Ubuntu-based image with the GitHub Actions runner installed
2. **entrypoint.sh**:
   - Obtains a registration token from GitHub API using your PAT
   - Configures the runner with your repository
   - Starts the runner process
   - Handles cleanup on exit
3. **Taskfile.yaml**: Provides convenient commands to manage the runner lifecycle

## Architecture

```
┌─────────────────────────────────────┐
│  macOS Host                         │
│  ┌───────────────────────────────┐  │
│  │  Docker Container             │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  GitHub Actions Runner  │  │  │
│  │  │  - Ubuntu 22.04         │  │  │
│  │  │  - Runner Agent         │  │  │
│  │  │  - Git, curl, jq, etc.  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
         ↕
    GitHub API
    (Registration & Jobs)
```

## Troubleshooting

### Runner not appearing in GitHub

1. Check the logs: `task logs`
2. Verify your `GITHUB_PAT` has the correct permissions
3. Ensure `REPO_URL` is correct in `.env`

### Container exits immediately

Check logs for error messages:

```bash
task logs
```

Common issues:

- Invalid GitHub PAT
- Network connectivity issues
- Incorrect repository URL

### Rebuild from scratch

```bash
task clean
task run
```

## Security Notes

- The runner runs as a non-root user (`runner`) inside the container
- The GitHub PAT is only used to obtain a short-lived registration token
- The runner is automatically removed from GitHub when the container stops
- Never commit your `.env` file with real credentials

## GitHub Repository Settings

After starting the runner, you can verify it in your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Actions** → **Runners**
3. You should see your runner listed with the configured labels

## Using the Runner in Workflows

In your workflow files (`.github/workflows/*.yml`), specify the runner:

```yaml
jobs:
  my-job:
    runs-on: self-hosted
    # or with specific labels:
    # runs-on: [self-hosted, mac-docker, arm64]
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: ./run-tests.sh
```
