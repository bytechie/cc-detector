# Claude Integration Notes

This document describes the high-level rationale for integrating Claude Subagents and Skills for credit card detection and redaction.

- Subagent: small HTTP microservice that receives text and uses Skills to analyze and redact sensitive data.
- Skills: modular Python functions for detection and anonymization; can be replaced with Presidio-based implementations.
- n8n: orchestrates ingestion and alerts when PII is found.

Security note: Never log or commit raw PII. Use environment variables and secret stores for production.
