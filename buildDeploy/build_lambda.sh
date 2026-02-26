#!/bin/bash
set -euo pipefail

# Project root is one level up from this script
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

SRC_HANDLERS_DIR="handlers/custom_lists"
SRC_CORE_DIR="core"

OUT_DIR="dist"
ZIP_NAME="custom_listings_entrypoint_lambda.zip"
BUILD_DIR=".lambda_build"

if [[ ! -d "$SRC_HANDLERS_DIR" ]]; then
  echo "ERROR: missing $SRC_HANDLERS_DIR"
  exit 1
fi

if [[ ! -d "$SRC_CORE_DIR" ]]; then
  echo "ERROR: missing $SRC_CORE_DIR"
  exit 1
fi

rm -rf "$OUT_DIR" "$BUILD_DIR"
mkdir -p "$BUILD_DIR" "$OUT_DIR"

echo "Installing dependencies"
uv pip install . \
  --target "$BUILD_DIR"

echo "Copying handlers"
mkdir -p "$BUILD_DIR/handlers"
cp -R "$SRC_HANDLERS_DIR" "$BUILD_DIR/handlers/"

echo "Copying core"
cp -R "$SRC_CORE_DIR" "$BUILD_DIR/core"

echo "Copying config"
cp config.py "$BUILD_DIR/config.py"

echo "Creating zip"
(
  cd "$BUILD_DIR"
  zip -r "../$OUT_DIR/$ZIP_NAME" .
)

echo "Lambda zip built:"
ls -lh "$OUT_DIR/$ZIP_NAME"
