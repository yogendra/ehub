#!/bin/bash
set -e

# Required environment variables: GITHUB_PAT, REPO_URL, RUNNER_NAME, RUNNER_LABELS

echo "Configuring GitHub Actions Runner..."
echo "Repository: ${REPO_URL}"
echo "Runner Name: ${RUNNER_NAME}"
echo "Runner Labels: ${RUNNER_LABELS}"

# Validate required environment variables
if [ -z "${GITHUB_PAT}" ]; then
  echo "ERROR: GITHUB_PAT environment variable is not set"
  exit 1
fi

if [ -z "${REPO_URL}" ]; then
  echo "ERROR: REPO_URL environment variable is not set"
  exit 1
fi

# Extract owner and repo from REPO_URL (e.g., https://github.com/owner/repo)
OWNER_REPO=$(echo "${REPO_URL}" | sed 's|https://github.com/||')
echo "Owner/Repo: ${OWNER_REPO}"

# Cleanup function to remove the runner on exit
cleanup() {
  echo ""
  echo "Shutting down runner..."
  
  # Stop the runner process if it's still running
  if [ -n "${RUNNER_PID}" ]; then
    kill -TERM "${RUNNER_PID}" 2>/dev/null || true
    wait "${RUNNER_PID}" 2>/dev/null || true
  fi
  
  # Remove runner using PAT directly (simpler than getting a removal token)
  echo "Removing runner from GitHub..."
  ./config.sh remove --pat "${GITHUB_PAT}" 2>&1 || echo "Runner removal completed with warnings"
  
  echo "Cleanup complete"
  exit 0
}

# Trap SIGTERM (docker stop) and SIGINT (Ctrl+C) for graceful shutdown
trap cleanup SIGTERM SIGINT EXIT

# Check if runner is already configured and remove it
if [ -f ".runner" ]; then
  echo "Runner is already configured, removing old configuration..."
  ./config.sh remove --pat "${GITHUB_PAT}" 2>&1 || echo "Old configuration removed"
fi

# Configure the runner using PAT directly (--replace will remove any existing runner with the same name)
echo "Configuring runner..."
./config.sh \
  --url "${REPO_URL}" \
  --pat "${GITHUB_PAT}" \
  --name "${RUNNER_NAME}" \
  --labels "${RUNNER_LABELS}" \
  --unattended \
  --replace

echo "Starting runner..."
# Start the runner in background
./run.sh &

# Store the PID of the runner process
RUNNER_PID=$!

# Wait for the runner process
wait $RUNNER_PID
