# Contributing

Thanks for your interest in contributing.

## Before You Start

- Read [README.md](README.md)
- Read [SECURITY.md](SECURITY.md)
- Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Setup

1. Fork the repository
2. Create a feature branch from `main`
3. Install and run locally using the README instructions

## Workflow

1. Open an issue first for large changes
2. Keep PRs focused and small
3. Add or update tests for behavior changes
4. Update docs when user-facing behavior changes

## Coding Standards

- Prioritize readability and maintainability
- Validate external inputs
- Never hardcode secrets
- Keep changes scoped to one concern per PR

## Commit Messages

Use conventional commit prefixes:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `refactor:` code refactor
- `test:` tests
- `chore:` maintenance

Example:

```text
feat: add README language switcher and russian docs
```

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No secrets in code or logs
- [ ] Backward compatibility considered

## Review Process

Maintainers review for correctness, security, and maintainability. Feedback should be addressed before merge.
