from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.progress import track
import os
import datetime
import re
import requests

from datetime import datetime, timezone

console = Console()

ASCII_ART = """███████╗███████╗██████╗ ██╗ █████╗ ██╗         ██╗      ██████╗  ██████╗ ██╗  ██╗██╗   ██╗██████╗ 
██╔════╝██╔════╝██╔══██╗██║██╔══██╗██║         ██║     ██╔═══██╗██╔═══██╗██║ ██╔╝██║   ██║██╔══██╗
███████╗█████╗  ██████╔╝██║███████║██║         ██║     ██║   ██║██║   ██║█████╔╝ ██║   ██║██████╔╝
╚════██║██╔══╝  ██╔══██╗██║██╔══██║██║         ██║     ██║   ██║██║   ██║██╔═██╗ ██║   ██║██╔═══╝ 
███████║███████╗██║  ██║██║██║  ██║███████╗    ███████╗╚██████╔╝╚██████╔╝██║  ██╗╚██████╔╝██║     
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝    ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     
                                                                                                  """  # raccourci ici pour éviter de répéter, à insérer identique

def print_banner():
    colors = ["#00FF22", "#70FF37", "#00FF88", "#5bffad", "#45ffe6"]
    lines = ASCII_ART.strip().split("\n")
    for i, line in enumerate(lines):
        console.print(Text(line, style=colors[i % len(colors)]))
    console.print(Text("🎨 Author: serial_checker", style="grey50"))

def ask_repository():
    while True:
        path = Prompt.ask(Text("🛤️ Chemin du répertoire à scanner ?", style="grey50"))
        console.print()
        if not os.path.isdir(path):
            console.print(Text("❌ Répertoire introuvable. Réessayez.", style="red"))
        else:
            return path

def ask_webhook():
    while True:
        webhook = Prompt.ask(Text("🔗 Entrez le lien du webhook Discord (laisser vide pour ignorer) :", style="grey50"))
        console.print()
        if not webhook:
            return None
        if not webhook.startswith("https://discord.com/api/webhooks/"):
            console.print(Text("❌ Lien webhook invalide. Réessayez.", style="red"))
        else:
            return webhook

def search_in_files(repo, query):
    results = []
    all_files = [os.path.join(dp, f) for dp, _, filenames in os.walk(repo) for f in filenames]

    for filepath in track(all_files, description="🔍 Recherche en cours..."):
        try:
            with open(filepath, 'r', errors='ignore') as file:
                for num, line in enumerate(file, 1):
                    if query in line:
                        results.append((filepath, num, line.strip()))
        except Exception as e:
            console.print(f"[red]Erreur dans {filepath} : {e}[/red]")
    return results, len(all_files)

def save_results(results):
    if not results:
        return None
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"résultats_{now}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for file, line, content in results:
            f.write(f"{file} (Ligne {line}) : {content}\n")
    return filename

def send_file_to_webhook(webhook, file_path):
    if not webhook or not file_path:
        return
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f)}
            response = requests.post(webhook, files=files)
            if response.status_code in [200, 204]:
                console.print("[green]✅ Fichier envoyé avec succès au webhook.[/green]")
            else:
                console.print(f"[red]❌ Erreur webhook : {response.status_code}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Erreur lors de l'envoi du fichier : {e}[/red]")

def main():
    print_banner()
    repo = ask_repository()
    webhook = ask_webhook()

    while True:
        query = Prompt.ask(Text("🕵️ Quel info cherchez-vous ?", style="grey50"))
        results, scanned = search_in_files(repo, query)
        console.print(f"[cyan]📁 Nombre de fichiers parcourus : {scanned}[/cyan]")

        if results:
            console.print(f"[green]✅ {len(results)} résultats trouvés.[/green]")
            filename = save_results(results)
            if filename:
                console.print(f"[yellow]💾 Résultats enregistrés dans: {filename}[/yellow]")
                send_file_to_webhook(webhook, filename)
                console.print()
        else:
            console.print(f"[red]❌ Aucun résultat trouvé pour : {query}[/red]")

        if not Confirm.ask(Text("❓ Souhaitez-vous relancer une recherche ?", style="grey50")):
            break

        if not Confirm.ask(Text("❓ Réutiliser le même répertoire ?", style="grey50")):
            console.print()
            repo = ask_repository()

        if not Confirm.ask(Text("❓ Réutiliser le même webhook ?", style="grey50")):
            console.print()
            webhook = ask_webhook()

if __name__ == "__main__":
    main()
