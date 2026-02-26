# KL Custom Listings Server

## Local Install (uv)

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Build & Deploy (CLI)

All commands run from the `KL_custom_listings_server/` directory.

### Build the Lambda zip

```bash
bash buildDeploy/build_lambda.sh
```

Output: `dist/custom_listings_entrypoint_lambda.zip`

### Deploy to AWS (build + deploy)

```bash
bash buildDeploy/deploy.sh
```

### Deploy only (skip build)

```bash
bash buildDeploy/deploy.sh --skip-build
```

### One-liner: build and deploy

```bash
bash buildDeploy/build_lambda.sh && bash buildDeploy/deploy.sh --skip-build
```

