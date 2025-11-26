# Archived Startup Scripts

This directory contains individual startup scripts that have been consolidated into the unified `start.sh` script.

## Replaced by Unified Script

All functionality from these scripts is now available through the main startup script:

```bash
./start.sh [COMMAND] [MODE] [PORT]
```

## Mode Equivalents

- `start-basic.sh` → `./start.sh start basic`
- `start-enterprise.sh` → `./start.sh start enterprise`
- `start-production.sh` → `./start.sh start production`
- `start-local-monitoring.sh` → `./start.sh start metrics`

## Archive Contents

- `start-basic.sh` - Basic functionality startup
- `start-enterprise.sh` - Full-featured enterprise startup
- `start-production.sh` - Production environment startup
- `start-local-monitoring.sh` - Local monitoring setup

These scripts are preserved for reference but should not be used in new deployments.