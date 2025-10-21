#!/usr/bin/env bash
# Build script for Render

# Upgrade pip
pip install --upgrade pip

# Install production dependencies only (no heavy ML packages)
pip install -r requirements-render.txt

# Create necessary directories
mkdir -p db uploads exports

echo "Build complete!"
