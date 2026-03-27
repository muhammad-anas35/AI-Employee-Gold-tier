# Gold Tier Architecture Documentation

**Version:** 1.0
**Last Updated:** 2026-03-27
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

The Gold Tier AI Employee is an autonomous business automation system that monitors multiple input channels (email, WhatsApp, files, social media), processes tasks using Claude AI, integrates with business systems (Odoo accounting), and executes actions with human-in-the-loop approval for sensitive operations.

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
- Gmail Watcher (`gmail-watcher`)
- WhatsApp Watcher (`whatsapp-watcher`)
- File System Watcher (`filesystem_watcher.py`)
- Odoo Event Monitor (future)

**Technology:**
- Gmail API for email monitoring
- Playwright for WhatsApp Web automation
- Python watchdog for file system events

**Output:** Creates action files in `/Needs_Action` folder

### 2. Knowledge Layer (Storage)

**Purpose:** Central knowledge base and state management

**Components:**
- Obsidian Vault (`AI_Employee_Vault/`)
- Markdown files for all state
- JSON logs for audit trail

**Folder Structure:**
```
AI_Employee_Vault/
├── Dashboard.md              # Real-time metrics
├── Company_Handbook.md       # Rules and policies
├── Inbox/                    # Manual drops
├── Needs_Action/             # Pending tasks
├── Plans/                    # Execution plans
├── Pending_Approval/         # Awaiting approval
├── Approved/                 # Approved actions
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
├── Reports/                  # Business reports
├── Accounting/               # Financial records
└── Logs/                     # Audit trail (JSON)
```

### 3. Reasoning Layer (Processing)

**Purpose:** Analyze tasks and create execution plans

**Components:**
- Claude Code CLI (primary AI)
- VaultManager (`claude_integration.py`)
- Ralph Wiggum Loop (autonomous processor)
- Workflow Orchestrator (cross-domain)

**Process:**
1. Read task from `/Needs_Action`
2. Analyze requirements
3. Create execution plan
4. Determine if approval needed
5. Execute or request approval

### 4. Action Layer (Output)

**Purpose:** Execute approved actions across domains

**Components:**
- Email Sender (`send-email`)
- Social Media Posters (`facebook-poster`, `twitter-poster`, `linkedin-poster`)
- Odoo Integration (`odoo-integration`)
- File Operations (built-in)

**Technology:**
- Gmail API for email sending
- Playwright for social media posting
- Odoo XML-RPC API for accounting
- Python file operations

### 5. Orchestration Layer (Coordination)

**Purpose:** Coordinate all components and manage lifecycle

**Components:**
- Orchestrator (`orchestrator`)
- Ralph Wiggum Loop (`ralph-wiggum-loop`)
- Workflow Orchestrator (`workflow-orchestrator`)
- Business Audit (`business-audit`)

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
         │  /Needs_Action → /Plans →         │
         │  /Pending_Approval → /Approved →  │
         │  /Done                            │
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
Gmail → Gmail Watcher → /Needs_Action/EMAIL_*.md
                              ↓
                    Ralph Wiggum Loop reads
                              ↓
                    Analyzes: "Reply needed"
                              ↓
                    Creates draft response
                              ↓
                    /Pending_Approval/EMAIL_*.md
                              ↓
                    Human reviews & approves
                              ↓
                    Moves to /Approved/
                              ↓
                    Email Sender executes
                              ↓
                    Moves to /Done/ + logs
```

### 2. Invoice Workflow

```
Email: "Need invoice for Project X"
                ↓
        /Needs_Action/EMAIL_*.md
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
        /Done/ + audit log
```

### 3. Social Media Publishing Flow

```
File drop: blog_post.md
                ↓
        File Watcher → /Needs_Action/FILE_*.md
                ↓
        Ralph Wiggum Loop
                ↓
        Workflow: "content_publish"
                ↓
        Creates drafts:
        - /Pending_Approval/POST_LINKEDIN_*.md
        - /Pending_Approval/TWEET_*.md
        - /Pending_Approval/POST_FACEBOOK_*.md
                ↓
        Human approves all
                ↓
        Posters execute in parallel
                ↓
        Screenshots saved to /Done/
```

---

## Deployment Architecture

### Local Development

```
Windows 10/11 Machine
├── Python 3.13+ (AI Employee code)
├── Node.js 24+ (MCP servers)
├── Docker Desktop (Odoo)
├── Claude Code CLI
└── Obsidian (optional, for vault viewing)
```

### Production Deployment

```
Cloud VM (AWS/Azure/GCP)
├── Ubuntu 22.04 LTS
├── Python 3.13+ with systemd services
├── Docker for Odoo
├── Nginx reverse proxy (for Odoo)
├── Automated backups (vault + logs)
└── Monitoring (health checks)
```

### Systemd Services

```bash
# /etc/systemd/system/ai-employee-orchestrator.service
[Unit]
Description=AI Employee Orchestrator
After=network.target

[Service]
Type=simple
User=aiemployee
WorkingDirectory=/opt/ai-employee
ExecStart=/usr/bin/python3 .claude/skills/orchestrator/scripts/orchestrator.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Security Architecture

### 1. Credential Management

- **Environment Variables:** All credentials in `.env` file
- **Never Committed:** `.env` in `.gitignore`
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

- **File Permissions:** Vault readable only by AI Employee user
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
- **Python 3.13+** - Main programming language
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

---

## Future Enhancements

1. **Multi-Tenant:** Support multiple businesses
2. **AI Training:** Fine-tune on business-specific data
3. **Mobile App:** iOS/Android monitoring
4. **Voice Interface:** Alexa/Google Assistant integration
5. **Advanced Analytics:** ML-based insights
6. **API Gateway:** REST API for external integrations

---

**Document Version:** 1.0
**Last Updated:** 2026-03-27
**Maintained By:** AI Employee Development Team
