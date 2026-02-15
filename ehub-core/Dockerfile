# Stage 1: Build the environment
FROM continuumio/miniconda3:latest AS build

# Set working directory
WORKDIR /build

# Copy environment and requirements from root (context is root)
COPY environment.yml requirements.txt requirements-dev.txt ./

# Create the environment
RUN conda env create -f environment.yml && \
    conda clean -afy

# Stage 2: Production image
FROM continuumio/miniconda3:latest

# Install runtime dependencies and Terraform
RUN apt update && apt install -y curl unzip && \
    curl -o terraform.zip https://releases.hashicorp.com/terraform/1.7.4/terraform_1.7.4_linux_$(dpkg --print-architecture).zip && \
    unzip terraform.zip -d /usr/local/bin && \
    rm terraform.zip && \
    rm -rf /var/lib/apt/lists/*  &&\
    curl -sSf https://temporal.download/cli.sh | sh -s -- --install-dir /usr/local/bin


# Copy the environment from the build stage
COPY --from=build /opt/conda/envs/ehub /opt/conda/envs/ehub

# Workdir
WORKDIR /app

# Copy ehub-core source (context is root)
COPY ehub-core/src ./src

# Set environment variables
ENV PATH="/opt/conda/envs/ehub/bin:$PATH"
ENV TEMPORAL_HOST="temporal:7233"
ENV PYTHONPATH="/app/src"
ENV CONDA_DEFAULT_ENV=ehub
ENV PROJECT_ROOT="/app"

VOLUME [ "/app/tf_states" ]
# Run the worker directly using python from the environment
CMD ["python", "src/main.py"]
