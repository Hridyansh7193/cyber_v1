#!/usr/bin/env bash
# Build all BugHunter Docker images sequentially
# Designed for execution on Ubuntu runtime.

set -e

echo "[*] Building Base Image..."
docker build -t bughunter-base:latest ./docker/containers/base

echo "[*] Building Recon Image..."
docker build -t bughunter-recon:latest ./docker/containers/recon

echo "[*] Building Vuln Image..."
docker build -t bughunter-vuln:latest ./docker/containers/vuln

echo "[*] Building JS Image..."
docker build -t bughunter-js:latest ./docker/containers/js

echo "[*] Building API Image..."
docker build -t bughunter-api:latest ./docker/containers/api

echo "[*] All images built successfully!"
