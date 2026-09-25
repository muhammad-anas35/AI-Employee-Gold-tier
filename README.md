# 🔗 Nexus

> **Your Personal AI Assistant** — Automate email, accounting, social media, and workflows locally.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

---

## ✨ Features

| Domain | Capabilities |
|--------|--------------|
| **📧 Email** | Gmail monitoring, smart drafting, approval workflow, sending |
| **💰 Accounting** | Odoo integration: invoices, expenses, payments, P&L, aged receivables |
| **📱 Social Media** | LinkedIn & Facebook posting with approval, scheduling, media support |
| **🤖 Autonomy** | Ralph Wiggum Loop — continuous task processing every 10 minutes |
| **🔄 Workflows** | Cross-domain automation: invoice → email → social, file → multi-platform |
| **📊 Intelligence** | Weekly business audits, CEO briefings, financial reports |
| **🔒 Security** | Human-in-the-loop approval, local-first, encrypted credentials |

---

## 🚀 Quick Start

```bash
# 1. Clone and enter
git clone <your-repo> nexus
cd nexus

# 2. Install dependencies
pip install -e ".[dev]"
playwright install chromium

# 3. Run setup wizard
nexus init

# 4. Authenticate services
nexus email auth
nexus social setup linkedin
nexus social setup facebook

# 4. Start the daemon
nexus daemon start --foreground
```

---

## 📖 Commands

### Email
```bash
nexus email send --to "client@example.com" --subject "Invoice" --body "Please find attached..."
nexus email send-approved          # Send all approved drafts
nexus email auth                   # Authenticate Gmail
```

### Social Media
```bash
nexus social post linkedin --content "Excited to announce..." --schedule "2024-01-15T09:00:00"
nexus social post facebook --content "New blog post!" --image ./banner.png
nexus social publish linkedin      # Publish approved posts
nexus social setup linkedin        # First-time LinkedIn auth
nexus social setup facebook        # First-time Facebook auth
```

### Accounting (Odoo)
```bash
nexus accounting invoice --client "Acme Corp" --email "billing@acme.com" --amount 5000 --description "Q1 Consulting"
nexus accounting expense --category "Software" --amount 99 --description "Monthly subscription"
nexus accounting summary --period this-month
```

### Workflows
```bash
nexus workflow run client_invoice    # Email → Invoice → Email → Social
nexus workflow run content_publish   # File → LinkedIn → Facebook → Email
nexus workflow list                  # Show all workflows
```

### Autonomy
```bash
nexus autonomy start --interval 10   # Ralph Wiggum Loop (every 10 min)
```

### Daemon & Status
```bash
nexus daemon start --foreground      # Start all watchers + orchestrator
nexus status                         # Dashboard view
nexus doctor                         # Health checks
```

### Configuration
```bash
nexus config show                    # View current config
nexus init                           # Interactive setup wizard
```

---

## 🏗 Architecture

```
nexus/
├── nexus/                 # Main package
│   ├── cli.py            # Command interface (Click + Rich)
│   ├── config.py         # Centralized configuration
│   └── __main__.py       # Entry point
├── skills/               # Domain skills
│   ├── email/            # Gmail watcher + sender
│   ├── social/           # LinkedIn, Facebook, scheduler
│   └── accounting/       # Odoo XML-RPC client
├── core/                 # Core engines
│   ├── autonomy/         # Ralph Wiggum Loop
│   ├── intelligence/     # Business audit, CEO briefings
│   ├── workflows/        # Cross-domain workflow orchestrator
│   └── orchestrator/     # Master daemon
├── src/                  # Shared libraries
│   ├── integrations/     # VaultManager (Obsidian vault ops)
│   ├── utils/            # Rate limiter, retry, audit logger
│   └── watchers/         # File system watcher
├── workspace/            # Local vault (gitignored)
│   ├── inbox/            # Needs_Action
│   ├── pending/          # Pending_Approval
│   ├── approved/         # Approved
│   ├── archive/          # Done
│   ├── reports/          # Business reports
│   └── logs/             # Audit trail
├── infra/                # Docker Compose (Odoo + PostgreSQL)
├── config/               # Config files (credentials, tokens)
└── tests/                # Test suite
```

---

## 🔐 Security

- **Local-first**: All data stays on your machine
- **Approval workflow**: Sensitive actions (sending email, posting social, payments) require human approval
- **Credential storage**: OAuth tokens in `config/`, never committed
- **Audit trail**: Every action logged to `workspace/logs/YYYY-MM-DD.json`

---

## 📚 Documentation

- [Getting Started](docs/GETTING_STARTED.md) — 5-minute setup
- [Configuration](docs/CONFIGURATION.md) — All config options
- [Skills Reference](docs/SKILLS.md) — Skill catalog with examples
- [Workflows](docs/WORKFLOWS.md) — Built-in workflows + custom creation
- [Architecture](docs/ARCHITECTURE.md) — Technical deep dive
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues & fixes

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_odoo_api.py -v

# Health check
nexus doctor
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `ruff check . && black nexus/ && mypy nexus/`
5. Submit PR

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [Claude Code](https://claude.ai/code) — AI reasoning
- [Odoo](https://odoo.com) — Accounting backend
- [Playwright](https://playwright.dev) — Browser automation
- [Rich](https://rich.readthedocs.io) — Beautiful CLI
- [Click](https://click.palletsprojects.com) — CLI framework

---

### 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      AI Employee     │
                         │    Agentic Brain     │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              ┌──────────┐   ┌───────────┐   ┌───────────┐
              │   MCP    │   │ Workflow  │   │  Agent    │
              │ Servers  │   │Orchestrator│  │  Skills   │
              └────┬─────┘   └─────┬─────┘   └─────┬─────┘
                   │               │               │
                   └───────────────┼───────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
     ┌──────────┐             ┌──────────┐             ┌──────────┐
     │  Gmail   │             │  Odoo    │             │ Social   │
     │          │             │Accounting│             │  Media   │
     └──────────┘             └──────────┘             └──────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ Approval System  │
                         │ Human-in-Loop    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Audit & Reports  │
                         └──────────────────┘

---
**Nexus** — Your Personal AI Assistant, running locally, under your control.
