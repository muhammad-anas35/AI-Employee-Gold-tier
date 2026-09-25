# Nexus Architecture Documentation

**Version:** 1.0
**Last Updated:** 2026-09-25
**Status:** Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Component Diagram](#component-diagram)
4. [Data Flow](#data-flow)
5. [Deployment Architecture](#deployment-architecture)
6. [Security Architecture](#security-architecture)
7. [Scalability & Performance](#scalability--performance)

---

## System Overview

Nexus is an autonomous personal AI assistant that monitors multiple input channels (email, WhatsApp, files, social media), processes tasks using Claude AI, integrates with business systems (Odoo accounting), and executes actions with human-in-the-loop approval for sensitive operations.

### Key Characteristics

- **Autonomous:** Runs continuously without human intervention for safe actions
- **Multi-Domain:** Integrates personal, business, and accounting domains
- **Approval-Based:** Human approval required for sensitive actions
- **Audit-Ready:** Complete audit trail for compliance
- **Self-Healing:** Automatic error recovery with exponential backoff
- **Extensible:** Plugin-based skill system

---

## Architecture Layers

### 1. Perception Layer (Input)

**Purpose:** Monitor external systems for events and changes

**Components:**
- Gmail Watcher (`gmail_watcher`)
- WhatsApp Watcher (`whatsapp_watcher`)
- File System Watcher (`filesystem_watcher.py`)
- Odoo Event Monitor (future)

**Technology:**
- Gmail API for email monitoring
- Playwright for WhatsApp Web automation
- Python watchdog for file system events

**Output:** Creates action files in `workspace/inbox/` folder

### 2. Knowledge Layer (Storage)

**Purpose:** Central knowledge base and state management

**Components:**
- Obsidian Vault (`workspace/`)
- Markdown files for all state
- JSON logs for audit trail

**Folder Structure:**
```
workspace/
├── dashboard.md              # Real-time metrics
├── Company_Handbook.md       # Rules and policies
├── inbox/                    # Manual drops / Needs_Action
├── pending/                  # Pending approval
├── approved/                 # Approved actions
├── rejected/                 # Rejected actions
├── archive/                  # Completed tasks
├── reports/                  # Business reports
├── accounting/               # Financial records
└── logs/                     # Audit trail (JSON)
```

### 3. Reasoning Layer (Processing)

**Purpose:** Analyze tasks and create execution plans

**Components:**
- Claude Code CLI (primary AI)
- VaultManager (`src/integration/claude_integration.py`)
- Ralph Wiggum Loop (autonomous processor)
- Workflow Orchestrator (cross-domain)

**Process:**
1. Read task from `workspace/inbox/`
2. Analyze requirements
3. Create execution plan
4. Determine if approval needed
5. Execute or request approval

### 4. Action Layer (Output)

**Purpose:** Execute approved actions across domains

**Components:**
- Email Sender (`email_sender`)
- Social Media Posters (`linkedin_poster`, `facebook_poster`)
- Odoo Integration (`odoo_client`)
- File Operations (built-in)

**Technology:**
- Gmail API for email sending
- Playwright for social media posting
- Odoo XML-RPC API for accounting
- Python file operations

### 5. Orchestration Layer (Coordination)

**Purpose:** Coordinate all components and manage lifecycle

**Components:**
- Orchestrator (`core/orchestrator`)
- Ralph Wiggum Loop (`core/autonomy/ralph_wiggum_loop`)
- Workflow Orchestrator (`core/workflows/workflow_orchestrator`)
- Business Audit (`core/intelligence/business_audit`)

**Responsibilities:**
- Start/stop watchers
- Process approvals
- Execute workflows
- Generate reports
- Health monitoring
- Auto-restart on failure

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  Gmail Watcher  │  WhatsApp  │  File System  │  Odoo Events │
│   (Gmail API)   │ (Playwright)│  (Watchdog)   │  (XML-RPC)   │
└────────┬────────┴─────┬──────┴──────┬────────┴──────┬───────┘
         │              │             │               │
         └──────────────┴─────────────┴───────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │      KNOWLEDGE LAYER              │
          │   (Obsidian Vault - Markdown)     │
          │                                   │
          │  /inbox → /plans →                │
          │  /pending → /approved →           │
          │  /archive                         │
          └───────────────┬───────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │      REASONING LAYER              │
          ├───────────────────────────────────┤
          │  Claude Code CLI                  │
          │  VaultManager                     │
          │  Ralph Wiggum Loop                │
          │  Workflow Orchestrator            │
          └───────────────┬───────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │      ACTION LAYER                 │
          ├───────────────────────────────────┤
          │  Email  │  Social  │  Odoo  │ File│
          │  Sender │  Posters │  API   │ Ops │
          └───────────────┬───────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │   ORCHESTRATION LAYER             │
          ├───────────────────────────────────┤
          │  Orchestrator (Master Process)    │
          │  Health Monitoring                │
          │  Auto-Restart                     │
          │  Business Audit                   │
          └───────────────────────────────────┘
```

---

## Data Flow

### 1. Email Processing Flow

```
Gmail → Gmail Watcher → workspace/inbox/EMAIL_*.md
                          ↓
                Ralph Wiggum Loop reads
                          ↓
                Analyzes: "Reply needed"
                          ↓
                Creates draft response
                          ↓
                workspace/pending/EMAIL_*.md
                          ↓
                Human reviews & approves
                          ↓
                Moves to workspace/approved/
                          ↓
                Email Sender executes
                          ↓
                Moves to workspace/archive/ + logs
```

### 2. Invoice Workflow

```
Email: "Need invoice for Project X"
                ↓
        workspace/inbox/EMAIL_*.md
                ↓
        Ralph Wiggum Loop
                ↓
        Workflow Orchestrator: "client_invoice"
                ↓
        Step 1: Create invoice in Odoo (auto)
                ↓
        Step 2: Send invoice email (approval)
                ↓
        Step 3: Post LinkedIn update (approval)
                ↓
        Step 4: Update dashboard (auto)
                ↓
        workspace/archive/ + audit log
```

### 3. Social Media Publishing Flow

```
File drop: blog_post.md
                ↓
        File Watcher → workspace/inbox/FILE_*.md
                ↓
        Ralph Wiggum Loop
                ↓
        Workflow: "content_publish"
                ↓
        Creates drafts:
        - workspace/pending/POST_LINKEDIN_*.md
        - workspace/pending/POST_FACEBOOK_*.md
                ↓
        Human approves all
                ↓
        Posters execute in parallel
                ↓
        Screenshots saved to workspace/archive/
```

---

## Deployment Architecture

### Local Development

```
Windows 10/11 / Linux / macOS
├── Python 3.11+ (Nexus code)
├── Node.js 18+ (MCP servers)
├── Docker Desktop (Odoo + PostgreSQL)
├── Chrome/Chromium (Playwright)
└── Obsidian (optional, for vault viewing)
```

### Production Deployment

```
Cloud VM (AWS/Azure/GCP) or Local Server
├── Ubuntu 22.04 LTS
├── Python 3.11+ with systemd services
├── Docker for Odoo + PostgreSQL
├── Nginx reverse proxy (for Odoo)
├── Automated backups (vault + logs)
└── Monitoring (health checks)
```

### Systemd Services

```ini
# /etc/systemd/system/nexus.service
[Unit]
Description=Nexus AI Assistant
After=network.target

[Service]
Type=simple
User=nexus
WorkingDirectory=/opt/nexus
ExecStart=/opt/nexus/venv/bin/nexus daemon start --foreground
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Security Architecture

### 1. Credential Management

- **Environment Variables:** All credentials in `config/` (gitignored)
- **Never Committed:** `.gitignore` excludes `config/`, `workspace/`, `browser_data/`
- **Encryption:** OAuth tokens encrypted at rest
- **Rotation:** Regular credential rotation policy

### 2. Approval Workflow

**Safe Actions (Auto-Execute):**
- Reading emails
- Creating drafts
- Organizing files
- Updating dashboard
- Generating reports

**Sensitive Actions (Require Approval):**
- Sending emails to new contacts
- Posting on social media
- Making payments
- Deleting files
- Finalizing invoices

### 3. Audit Trail

- **Complete Logging:** Every action logged to JSON
- **Immutable:** Logs are append-only
- **Timestamped:** ISO 8601 timestamps
- **Structured:** JSON format for easy parsing
- **Retention:** 90-day retention policy

### 4. Access Control

- **File Permissions:** Vault readable only by Nexus user
- **API Keys:** Scoped to minimum required permissions
- **OAuth:** Gmail uses OAuth2 with refresh tokens
- **Browser Sessions:** Playwright sessions isolated per skill

---

## Scalability & Performance

### Current Capacity

- **Emails:** 100+ per day
- **Files:** 50+ per day
- **Social Posts:** 20+ per day
- **Invoices:** 10+ per day
- **Response Time:** < 5 minutes for safe actions

### Bottlenecks

1. **Claude API Rate Limits:** 50 requests/minute
2. **Gmail API Quota:** 250 quota units/user/second
3. **Playwright:** Sequential browser operations (5-10s each)
4. **Disk I/O:** Vault operations (minimal impact)

### Optimization Strategies

1. **Batch Processing:** Group similar tasks
2. **Caching:** Cache frequently accessed data
3. **Parallel Execution:** Run independent tasks concurrently
4. **Rate Limiting:** Built-in rate limiters for APIs
5. **Async Operations:** Use async/await for I/O

### Scaling Options

**Vertical Scaling:**
- Increase VM resources (CPU, RAM)
- Faster disk (SSD)

**Horizontal Scaling:**
- Multiple Ralph Wiggum loops (domain-specific)
- Separate watchers on different machines
- Load balancer for Odoo

---

## Monitoring & Observability

### Health Checks

- **Watcher Status:** Process alive checks every 5 minutes
- **API Connectivity:** Test API endpoints every 10 minutes
- **Disk Space:** Alert if < 10% free
- **Error Rate:** Alert if > 5% error rate

### Metrics

- **Dashboard.md:** Real-time metrics updated every cycle
- **Business Audit:** Weekly comprehensive reports
- **Logs:** JSON logs for detailed analysis

### Alerting

- **Email Alerts:** Critical errors emailed to admin
- **Slack Integration:** (future) Real-time notifications
- **PagerDuty:** (future) On-call escalation

---

## Technology Stack

### Core
- **Python 3.11+** - Main programming language
- **Claude Code CLI** - AI reasoning engine
- **Obsidian Vault** - Knowledge base (Markdown)

### APIs & Integrations
- **Gmail API** - Email monitoring and sending
- **Odoo XML-RPC** - Accounting integration
- **Playwright** - Browser automation

### Infrastructure
- **Docker** - Odoo containerization
- **systemd** - Process management (Linux)
- **Git** - Version control

### Libraries
- **google-auth** - Gmail authentication
- **playwright** - Browser automation
- **watchdog** - File system monitoring
- **requests** - HTTP client
- **rich** - Beautiful CLI output
- **click** - CLI framework

---

## Future Enhancements

1. **Multi-Tenant:** Support multiple businesses
2. **AI Training:** Fine-tune on business-specific data
3. **Mobile App:** iOS/Android monitoring
4. **Voice Interface:** Alexa/Google Assistant integration
5. **Advanced Analytics:** ML-based insights
6. **API Gateway:** REST API for external integrations

---

## Technology Stack Summary

| Category | Technology |
|----------|------------|
| Language | Python 3.11+ |
| AI Engine | Claude Code CLI |
| Knowledge Base | Obsidian Vault (Markdown) |
| Email | Gmail API (OAuth2) |
| Accounting | Odoo XML-RPC |
| Browser Automation | Playwright |
| File Monitoring | watchdog |
| Containerization | Docker |
| Process Management | systemd |
| CLI Framework | Click + Rich |

---

*Document Version: 1.0*
*Last Updated: 2026-09-25*
*Maintained By: Nexus Development Team*
