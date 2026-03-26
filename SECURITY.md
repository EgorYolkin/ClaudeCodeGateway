# Security Policy

## Supported Versions

Security fixes are applied to the latest `main` branch.

## Reporting a Vulnerability

Please do not open public issues for suspected vulnerabilities.

Report privately via the support channel in [SUPPORT.md](SUPPORT.md) with:

- Description of the issue
- Reproduction steps
- Impact assessment
- Suggested mitigation (if known)

## Response Process

- Acknowledge receipt as soon as possible
- Validate and triage severity
- Implement and test a fix
- Coordinate responsible disclosure when needed

## Security Expectations for Contributors

- No hardcoded secrets
- Validate all external input
- Prefer safe defaults and least privilege
- Avoid leaking sensitive details in errors/logs

If you accidentally expose credentials, rotate them immediately.
