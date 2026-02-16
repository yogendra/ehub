# Use Ubuntu 22.04 as base image
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install prerequisites for the runner
RUN apt-get update && apt-get install -y \
    curl \
    git \
    jq \
    libgbm-dev \
    libnss3 \
    libsecret-1-0 \
    libxshmfence1 \
    libasound2 \
    libgtk-3-0 \
    libnspr4 \
    libxcb1 \
    libxss1 \
    wget \
    gnupg \
    lsb-release \
    ca-certificates \
    sudo \
    && rm -rf /var/lib/apt/lists/*


# Create a non-root user for running the runner
RUN useradd -m -s /bin/bash runner && \
    usermod -aG sudo runner && \
    echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Download and install the GitHub Actions runner application
WORKDIR /actions-runner

# Get the latest runner version and download it

RUN RUNNER_VERSION=$(curl --silent "https://api.github.com/repos/actions/runner/releases/latest" | jq -r '.tag_name' | sed 's/v//') && \
    ARCH=$(uname -m) && \
    case ${ARCH} in \
    x86_64) RUNNER_ARCH="x64" ;; \
    aarch64) RUNNER_ARCH="arm64" ;; \
    *) echo "Unsupported architecture: ${ARCH}"; exit 1 ;; \
    esac && \
    curl -O -L "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" && \
    tar xzf "./actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" && \
    rm -f "./actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"

# Change ownership to runner user
RUN chown -R runner:runner /actions-runner

# Switch to runner user
USER runner

# Copy and set up the entrypoint script
COPY --chown=runner:runner entrypoint.sh /actions-runner/entrypoint.sh
RUN chmod +x /actions-runner/entrypoint.sh

ENTRYPOINT ["/actions-runner/entrypoint.sh"]
