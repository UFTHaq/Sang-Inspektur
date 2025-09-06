#!/bin/bash
sudo apt update
sudo apt install -y python3-venv python3-dev \
    gstreamer1.0-tools gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav \
    python3-gi python3-gst-1.0 libcamera-dev

python3 -m venv .venv
source .venv/bin/activate
pip install -r pi5/requirements-pi5.txt
echo "Pi 5 venv ready. Run 'source .venv/bin/activate'"
