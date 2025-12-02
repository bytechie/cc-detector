# Project Overview: Credit Card Detector with Claude + Presidio + n8n

This project detects and redacts credit card numbers in log files using a modular AI-powered pipeline. It combines Claude Code, Claude Skills, Claude Subagents, Microsoft Presidio, and n8n automation.

## Architecture Summary

- **Claude Subagent**: Processes log files line by line, delegates detection and redaction to Claude Skills.
- **Claude Skills**: Modular functions for credit card detection and redaction using Presidio.
- **Presidio**: Microsoft’s open-source PII detection engine.
- **n8n**: Workflow automation platform that triggers the pipeline and handles alerts/storage.

## Workflow

1. A log file is uploaded or sent to n8n.
2. n8n sends the file content to the Claude Subagent.
3. The Subagent uses Claude Skills to detect and redact credit card numbers.
4. n8n receives the results and sends alerts or stores redacted logs.

## Technologies Used

- Claude Code (Subagent logic)
- Claude Skills (modular AI functions)
- Presidio Analyzer + Anonymizer (Dockerized)
- n8n (automation and orchestration)


Security note: Never log or commit raw PII. Use environment variables and secret stores for production.
