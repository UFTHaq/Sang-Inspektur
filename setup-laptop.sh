#!/bin/bash
set -e

# --- Install dependency global ---
sudo apt update
sudo apt install -y python3-venv python3-dev \
    gstreamer1.0-tools gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav \
    python3-gi python3-gst-1.0

# --- Buat virtual environment ---
python3 -m venv .venv
source .venv/bin/activate

# --- Install package Python di venv ---
pip install --upgrade pip
pip install -r laptop/requirements-laptop.txt

echo "✅ Laptop venv ready (Linux). Run 'source .venv/bin/activate'"
