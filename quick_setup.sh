#!/bin/bash
# Quick Setup Script for cyclicpeptide MCP
# cyclicpeptide: Python package for cyclic peptides drug design
# Provides PropertyAnalysis, Sequence2Structure, Structure2Sequence, and more
# Source: https://github.com/dfwlab/cyclicpeptide

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up cyclicpeptide MCP ==="

# Step 1: Create Python environment
echo "[1/5] Creating Python 3.12 environment..."
(command -v mamba >/dev/null 2>&1 && mamba create -p ./env python=3.12 -y) || \
(command -v conda >/dev/null 2>&1 && conda create -p ./env python=3.12 -y) || \
(echo "Warning: Neither mamba nor conda found, creating venv instead" && python3 -m venv ./env)

# Step 2: Install core dependencies via conda/mamba
echo "[2/5] Installing core dependencies..."
(command -v mamba >/dev/null 2>&1 && mamba install -c conda-forge rdkit=2025.09.3 matplotlib=3.10.8 networkx=3.6.1 pandas=2.3.3 numpy=2.4.0 scipy=1.16.3 loguru=0.7.3 click=8.3.1 tqdm=4.67.1 -y -p ./env) || \
(./env/bin/pip install rdkit matplotlib==3.10.8 networkx==3.6.1 pandas==2.3.3 numpy==2.4.0 scipy==1.16.3 loguru==0.7.3 click==8.3.1 tqdm==4.67.1)

# Step 3: Install fastmcp and ipython
echo "[3/5] Installing fastmcp and ipython..."
./env/bin/pip install --ignore-installed fastmcp==2.14.1 ipython==9.8.0

# Step 4: Copy cyclicpeptide package to site-packages
echo "[4/5] Installing cyclicpeptide package..."
cp -r repo/cyclicpeptide/cyclicpeptide env/lib/python3.12/site-packages/

# Step 5: Copy states directory
echo "[5/5] Copying states directory..."
cp -r repo/cyclicpeptide/states env/lib/python3.12/site-packages/cyclicpeptide/

echo ""
echo "=== cyclicpeptide MCP Setup Complete ==="
echo "Documentation: https://dfwlab.github.io/cyclicpeptide/"
echo "To run the MCP server: ./env/bin/python src/server.py"
