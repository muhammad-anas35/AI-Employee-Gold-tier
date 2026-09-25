"""Nexus CLI - Main command interface"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pathlib import Path
import sys

from nexus.config import (
    WORKSPACE, CONFIG_DIR, CREDENTIALS_FILE, TOKEN_FILE,
    ODOO_URL, ODOO_DB, DROP_FOLDER
)

console = Console()

@click.group(invoke_without_command=True)
@click.version_option(version="1.0.0", prog_name="Nexus")
@click.pass_context
def cli(ctx):
    """Nexus - Your Personal AI Assistant
    
    Automate email, accounting, social media, and workflows.
    """
    if ctx.invoked_subcommand is None:
        show_welcome()

def show_welcome():
    """Show welcome message"""
    title = Text("🔗 Nexus", style="bold cyan")
    subtitle = Text("Your Personal AI Assistant", style="dim")
    
    console.print(Panel.fit(
        f"{title}\n{subtitle}\n\n"
        "Automate email, accounting, social media, and workflows.\n\n"
        "Commands:\n"
        "  nexus init          - Interactive setup wizard\n"
        "  nexus daemon start  - Start background processing\n"
        "  nexus status        - Show system status\n"
        "  nexus email         - Email operations\n"
        "  nexus social        - Social media operations\n"
        "  nexus accounting    - Accounting operations\n"
        "  nexus workflow      - Workflow operations\n"
        "  nexus autonomy      - Autonomous task processing\n"
        "  nexus config        - Configuration management\n"
        "  nexus doctor        - Health checks\n",
        border_style="cyan"
    ))

# Email commands
@cli.group()
def email():
    """Email operations"""
    pass

@email.command()
@click.option('--to', required=True, help='Recipient email')
@click.option('--subject', required=True, help='Email subject')
@click.option('--body', required=True, help='Email body')
@click.option('--attach', multiple=True, help='Attachment paths')
def send(to, subject, body, attach):
    """Send an email (creates draft for approval)"""
    from skills.email.email_sender.scripts.send_email import EmailSender
    sender = EmailSender()
    sender.create_email_request(to=to, subject=subject, body=body, attachments=list(attach))
    console.print(f"[green]✓[/green] Email draft created. Review and approve in workspace/pending/")

@email.command()
def send_approved():
    """Send all approved emails"""
    from skills.email.email_sender.scripts.send_email import EmailSender
    sender = EmailSender()
    sender.process_approved_emails()
    console.print("[green]✓[/green] Approved emails processed")

@email.command()
def auth():
    """Authenticate with Gmail API"""
    from skills.email.email_sender.scripts.send_email import EmailSender
    sender = EmailSender()
    sender.authenticate()
    console.print("[green]✓[/green] Gmail authenticated")

# Social commands
@cli.group()
def social():
    """Social media operations"""
    pass

@social.command()
@click.option('--platform', type=click.Choice(['linkedin', 'facebook']), required=True)
@click.option('--content', required=True, help='Post content')
@click.option('--image', help='Image path')
@click.option('--schedule', help='Schedule time (ISO format)')
def post(platform, content, image, schedule):
    """Create a social media post draft"""
    if platform == 'linkedin':
        from skills.social.linkedin_poster.scripts.linkedin_poster import LinkedInPoster
        poster = LinkedInPoster()
        filepath = poster.create_post_draft(content, scheduled_for=schedule)
    elif platform == 'facebook':
        from skills.social.facebook_poster.scripts.facebook_poster import create_post_draft
        filepath = create_post_draft(content, image_path=image)
    console.print(f"[green]✓[/green] Post draft created: {filepath}")

@social.command()
@click.option('--platform', type=click.Choice(['linkedin', 'facebook']), required=True)
def publish(platform):
    """Publish all approved posts"""
    if platform == 'linkedin':
        from skills.social.linkedin_poster.scripts.linkedin_poster import LinkedInPoster
        poster = LinkedInPoster()
        poster.process_approved_posts()
    elif platform == 'facebook':
        from skills.social.facebook_poster.scripts.facebook_poster import publish_approved_posts
        publish_approved_posts()
    console.print(f"[green]✓[/green] Approved {platform} posts published")

@social.command()
@click.option('--platform', type=click.Choice(['linkedin', 'facebook', 'whatsapp']), required=True)
def setup(platform):
    """Initial setup - authenticate with platform"""
    if platform == 'linkedin':
        from skills.social.linkedin_poster.scripts.linkedin_poster import LinkedInPoster
        poster = LinkedInPoster()
        poster.setup_session()
    elif platform == 'facebook':
        from skills.social.facebook_poster.scripts.facebook_poster import test_setup
        test_setup()
    elif platform == 'whatsapp':
        from skills.whatsapp_watcher.scripts.whatsapp_watcher import WhatsAppWatcher
        watcher = WhatsAppWatcher()
        watcher.setup_session()
    console.print(f"[green]✓[/green] {platform} setup complete")

# Accounting commands
@cli.group()
def accounting():
    """Accounting operations (Odoo)"""
    pass

@accounting.command()
@click.option('--client', required=True, help='Client name')
@click.option('--email', required=True, help='Client email')
@click.option('--amount', type=float, required=True, help='Invoice amount')
@click.option('--description', required=True, help='Invoice description')
def invoice(client, email, amount, description):
    """Create an invoice in Odoo"""
    from skills.accounting.odoo_client.scripts.odoo_client import OdooClient
    from nexus.config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
    
    odoo = OdooClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
    if odoo.authenticate():
        partner_id = odoo.find_customer(email)
        if not partner_id:
            partner_id = odoo.create_customer(client, email)
        invoice_id = odoo.create_invoice(partner_id, [{'description': description, 'price': amount}])
        if invoice_id:
            console.print(f"[green]✓[/green] Invoice created: {invoice_id}")
        else:
            console.print("[red]✗[/red] Failed to create invoice")
    else:
        console.print("[red]✗[/red] Odoo authentication failed")

@accounting.command()
@click.option('--category', required=True, help='Expense category')
@click.option('--amount', type=float, required=True, help='Expense amount')
@click.option('--description', required=True, help='Expense description')
def expense(category, amount, description):
    """Record an expense in Odoo"""
    from skills.accounting.odoo_client.scripts.odoo_client import OdooClient
    from nexus.config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
    
    odoo = OdooClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
    if odoo.authenticate():
        expense_id = odoo.record_expense(amount, category, description)
        if expense_id:
            console.print(f"[green]✓[/green] Expense recorded: {expense_id}")
        else:
            console.print("[red]✗[/red] Failed to record expense")
    else:
        console.print("[red]✗[/red] Odoo authentication failed")

@accounting.command()
@click.option('--period', type=click.Choice(['this-month', 'last-month', 'this-year']), default='this-month')
def summary(period):
    """Get financial summary"""
    from skills.accounting.odoo_client.scripts.odoo_client import OdooClient
    from nexus.config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
    from datetime import datetime, timedelta
    
    odoo = OdooClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
    if odoo.authenticate():
        now = datetime.now()
        if period == 'this-month':
            start = now.replace(day=1).strftime('%Y-%m-%d')
            end = (now.replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
        elif period == 'last-month':
            first = now.replace(day=1)
            start = (first - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d')
            end = first.strftime('%Y-%m-%d')
        else:  # this-year
            start = now.replace(month=1, day=1).strftime('%Y-%m-%d')
            end = now.strftime('%Y-%m-%d')
        
        summary = odoo.get_financial_summary(start, end)
        console.print(f"[cyan]Financial Summary ({period})[/cyan]")
        console.print(f"  Revenue: ${summary.get('revenue', 0):,.2f}")
        console.print(f"  Expenses: ${summary.get('expenses', 0):,.2f}")
        console.print(f"  Profit: ${summary.get('profit', 0):,.2f}")
    else:
        console.print("[red]✗[/red] Odoo authentication failed")

# Workflow commands
@cli.group()
def workflow():
    """Workflow operations"""
    pass

@workflow.command()
@click.argument('name')
def run(name):
    """Run a workflow"""
    from core.workflows.workflow_orchestrator.scripts.workflow_orchestrator import WorkflowOrchestrator
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.execute_workflow(name)
    console.print(f"[green]✓[/green] Workflow '{name}' completed: {result['status']}")

@workflow.command()
def list():
    """List available workflows"""
    from core.workflows.workflow_orchestrator.scripts.workflow_orchestrator import WorkflowOrchestrator
    orchestrator = WorkflowOrchestrator()
    orchestrator.list_workflows()

# Autonomy commands
@cli.group()
def autonomy():
    """Autonomous task processing"""
    pass

@autonomy.command()
@click.option('--interval', default=10, help='Check interval in minutes')
def start(interval):
    """Start autonomous task processing (Ralph Wiggum Loop)"""
    console.print(f"[cyan]Starting autonomy engine (every {interval} min)...[/cyan]")
    console.print("Press Ctrl+C to stop")
    from core.autonomy.ralph_wiggum_loop.scripts.ralph_loop import RalphWiggumLoop
    loop = RalphWiggumLoop()
    try:
        while True:
            loop.run_cycle()
            import time
            time.sleep(interval * 60)
    except KeyboardInterrupt:
        console.print("\n[yellow]Autonomy engine stopped[/yellow]")

# Daemon command
@cli.group()
def daemon():
    """Background daemon management"""
    pass

@daemon.command()
@click.option('--foreground', is_flag=True, help='Run in foreground')
def start(foreground):
    """Start the Nexus daemon (orchestrator + all watchers)"""
    from core.orchestrator.orchestrator_main.scripts.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    if foreground:
        console.print("[cyan]Starting Nexus daemon in foreground...[/cyan]")
        orchestrator.run()
    else:
        console.print("[yellow]Background mode not yet implemented. Use --foreground[/yellow]")

# Status command
@cli.command()
def status():
    """Show system status and dashboard"""
    from nexus.config import WORKSPACE
    
    dashboard_path = WORKSPACE / "dashboard.md"
    dashboard = ""
    if dashboard_path.exists():
        dashboard = dashboard_path.read_text()
    else:
        dashboard = "No dashboard found. Run nexus init to create."
    
    console.print(Panel.fit(
        f"[bold cyan]Nexus Status[/bold cyan]\n\n"
        f"Workspace: {WORKSPACE}\n"
        f"Dashboard: {WORKSPACE / 'dashboard.md'}\n\n"
        f"{dashboard}",
        border_style="cyan",
        title="🔗 Nexus Status"
    ))

# Config command
@cli.group()
def config():
    """Configuration management"""
    pass

@config.command()
def show():
    """Show current configuration"""
    from nexus.config import (
        WORKSPACE, CONFIG_DIR, CREDENTIALS_FILE, TOKEN_FILE,
        ODOO_URL, ODOO_DB, DROP_FOLDER
    )
    console.print(f"[cyan]Workspace:[/cyan] {WORKSPACE}")
    console.print(f"[cyan]Config Dir:[/cyan] {CONFIG_DIR}")
    console.print(f"[cyan]Gmail Credentials:[/cyan] {CREDENTIALS_FILE}")
    console.print(f"[cyan]Gmail Token:[/cyan] {TOKEN_FILE}")
    console.print(f"[cyan]Odoo URL:[/cyan] {ODOO_URL}")
    console.print(f"[cyan]Odoo DB:[/cyan] {ODOO_DB}")
    console.print(f"[cyan]Drop Folder:[/cyan] {DROP_FOLDER}")

# Doctor command
@cli.command()
def doctor():
    """Run health checks"""
    console.print("[cyan]Running health checks...[/cyan]\n")
    
    checks = [
        ("Python 3.11+", lambda: sys.version_info >= (3, 11)),
        ("Workspace exists", lambda: Path(WORKSPACE).exists()),
        ("Config dir exists", lambda: Path(CONFIG_DIR).exists()),
        ("Gmail credentials", lambda: Path(CREDENTIALS_FILE).exists()),
        ("Gmail token", lambda: Path(TOKEN_FILE).exists()),
        ("Odoo accessible", lambda: check_odoo()),
        ("Docker running", lambda: check_docker()),
    ]
    
    all_pass = True
    for name, check in checks:
        try:
            result = check()
            status = "[green]✓[/green]" if result else "[red]✗[/red]"
            if not result:
                all_pass = False
            console.print(f"  {status} {name}")
        except Exception as e:
            console.print(f"  [red]✗[/red] {name} - {e}")
            all_pass = False
    
    if all_pass:
        console.print("\n[green]All checks passed![/green]")
    else:
        console.print("\n[red]Some checks failed[/red]")

def check_odoo():
    try:
        import xmlrpc.client
        from nexus.config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        return uid is not None
    except:
        return False

def check_docker():
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps'], capture_output=True)
        return result.returncode == 0
    except:
        return False

# Init command
@cli.command()
def init():
    """Interactive setup wizard"""
    console.print(Panel.fit(
        "[bold cyan]Welcome to Nexus![/bold cyan]\n\n"
        "Let's get you set up in a few steps.",
        border_style="cyan"
    ))
    
    # Check workspace
    from nexus.config import WORKSPACE, CONFIG_DIR, ensure_workspace, CREDENTIALS_FILE, TOKEN_FILE, ODOO_URL, ODOO_DB, DROP_FOLDER
    ensure_workspace()
    
    console.print(f"[green]✓[/green] Workspace created at {WORKSPACE}")
    console.print(f"[green]✓[/green] Config directory at {CONFIG_DIR}")
    
    # Gmail setup
    console.print("\n[cyan]Gmail Setup[/cyan]")
    if not Path(CREDENTIALS_FILE).exists():
        console.print(f"[yellow]![/yellow] Gmail credentials not found at {CREDENTIALS_FILE}")
        console.print("  Download from Google Cloud Console and place there")
    else:
        console.print(f"[green]✓[/green] Gmail credentials found")
    
    if not Path(TOKEN_FILE).exists():
        console.print("[yellow]![/yellow] Gmail token not found - run 'nexus email auth' to authenticate")
    else:
        console.print(f"[green]✓[/green] Gmail token exists")
    
    # Odoo setup
    console.print("\n[cyan]Odoo Setup[/cyan]")
    console.print(f"  URL: {ODOO_URL}")
    console.print(f"  Database: {ODOO_DB}")
    console.print("  Run 'nexus accounting invoice --help' to test")
    
    # Drop folder
    console.print("\n[cyan]Drop Folder[/cyan]")
    console.print(f"  Location: {DROP_FOLDER}")
    DROP_FOLDER.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Drop folder ready at {DROP_FOLDER}")
    
    console.print("\n[bold green]Setup complete![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. nexus email auth          # Authenticate Gmail")
    console.print("  2. nexus social setup linkedin  # Setup LinkedIn")
    console.print("  3. nexus daemon start --foreground  # Start processing")
    console.print("  4. nexus status              # Check status")

if __name__ == '__main__':
    cli()
