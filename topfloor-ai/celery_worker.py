#!/usr/bin/env python
"""
Celery Worker Entry Point

Run this script to start the Celery worker for background task processing.

Usage:
    python celery_worker.py

Or with custom options:
    celery -A app.core.celery_app worker --loglevel=info --concurrency=4
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app import celery_app

if __name__ == "__main__":
    # Start the worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=2",  # Process 2 tasks concurrently
        "--pool=solo" if sys.platform == "win32" else "--pool=prefork",  # Use solo pool on Windows
    ])
