# Configuration Directory

This directory contains all configuration files for Nexus.

## Files

| File | Description |
|------|-------------|
| `.env` | Environment variables (not committed to git) |
| `credentials.json` | Gmail OAuth2 credentials (not committed to git) |
| `token.json` | Gmail OAuth2 token (not committed to git) |
| `mcp_config.json` | MCP server configuration |
| `rate_limits.json` | API rate limit configuration |

## Setup

1. Copy `.env.example` to `.env` and fill in your values
2. Download Gmail OAuth2 credentials from Google Cloud Console and save as `config/credentials.json`
3. Run `nexus init` to create workspace and authenticate services

## Security

- Never commit `.env`, `credentials.json`, or `token.json` to git
- These files are already in `.gitignore`
- Rotate credentials periodically
