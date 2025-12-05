#!/usr/bin/env python3
"""
Credit Card Detector - Application Entry Point

Compatibility layer for start.sh script expecting --mode and --port arguments.
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api import create_app
from src.utils.config import load_config


def main():
    """Main application entry point with start.sh compatibility."""
    parser = argparse.ArgumentParser(description="Credit Card Detector API")
    parser.add_argument(
        "--mode",
        help="Application mode (basic, metrics, production, enterprise)",
        default="basic"
    )
    parser.add_argument(
        "--port",
        help="Port to bind to",
        type=int,
        default=5000
    )
    parser.add_argument(
        "--config",
        help="Configuration file path",
        default=None
    )
    parser.add_argument(
        "--environment",
        help="Environment (default, development, production)",
        default="default"
    )
    parser.add_argument(
        "--host",
        help="Host to bind to",
        default=None
    )
    parser.add_argument(
        "--debug",
        help="Enable debug mode",
        action="store_true"
    )

    args = parser.parse_args()

    # Map mode to environment for configuration
    mode_to_env = {
        "basic": "development",
        "metrics": "development",
        "production": "production",
        "enterprise": "production"
    }

    environment = mode_to_env.get(args.mode, args.environment)

    # Load configuration
    config = load_config(args.config, environment)

    # Override config with command line arguments
    if args.host:
        config.config["app"]["host"] = args.host
    if args.port:
        config.config["app"]["port"] = args.port
    if args.debug:
        config.config["app"]["debug"] = True

    # Enable features based on mode
    if args.mode in ["metrics", "production", "enterprise"]:
        config.config["features"]["metrics"] = True
    if args.mode in ["production", "enterprise"]:
        config.config["features"]["monitoring"] = True
    if args.mode == "enterprise":
        config.config["features"]["ai_features"] = True
        config.config["features"]["comprehensive_testing"] = True

    # Create Flask app
    app = create_app(config)

    # Get configuration values
    host = config.get('app.host', '0.0.0.0')
    port = config.get('app.port', args.port)
    debug = config.get('app.debug', False)

    # Print startup message
    print(f"🚀 Starting Credit Card Detector")
    print(f"   Mode: {args.mode}")
    print(f"   Environment: {environment}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print(f"   Health: http://{host}:{port}/health")
    if config.get('features.metrics', False):
        print(f"   Metrics: http://{host}:{port}/metrics")
    print()

    # Run the application
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Credit Card Detector...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()