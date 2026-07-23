#!/bin/bash

echo "Stopping Spy Turtle..."

pkill -f "robot.startup.main" 2>/dev/null
pkill -f "robot.api.server" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
pkill -f "python.*spy_turtle" 2>/dev/null
pkill -f "rpicam-vid" 2>/dev/null
pkill -f "rpicam-still" 2>/dev/null
pkill -f "libcamera" 2>/dev/null

sleep 1

echo "Cleaning camera locks..."

sudo fuser -k /dev/video0 2>/dev/null
sudo fuser -k /dev/media0 2>/dev/null
sudo fuser -k /dev/media1 2>/dev/null

echo "Spy Turtle stopped."