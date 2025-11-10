# Presidio Integration Notes

This folder contains notes for integrating Microsoft Presidio for analysis and anonymization.

If you prefer Presidio:
- Run the analyzer and anonymizer services (see `docker-compose.yml`).
- Replace the `detect_credit_cards` and `redact_credit_cards` skills with clients that call Presidio APIs.

Presidio analyzer docs: https://microsoft.github.io/presidio/
