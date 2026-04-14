import argparse
import json
import os
import subprocess
import urllib.request
from pathlib import Path

def load_environment_variables(env_file_path: Path) -> None:
    if not env_file_path.exists():
        return
    with open(env_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"\'')

def load_ignored_repositories(ignore_file_path: Path) -> set:
    if not ignore_file_path.exists():
        return set()
    with open(ignore_file_path, 'r', encoding='utf-8') as file:
        return {line.strip() for line in file if line.strip() and not line.startswith('#')}

def fetch_github_repositories(github_token: str) -> list:
    repositories = []
    page_number = 1
    
    while True:
        request = urllib.request.Request(
            f"https://api.github.com/user/repos?per_page=100&page={page_number}",
            headers={
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        with urllib.request.urlopen(request) as response:
            page_data = json.loads(response.read().decode())
            if not page_data:
                break
            repositories.extend(repository["full_name"] for repository in page_data)
        page_number += 1
        
    return repositories

def backup_repository(repository_full_name: str, backup_directory: Path, github_token: str) -> None:
    repository_path = backup_directory / repository_full_name
    repository_path.parent.mkdir(parents=True, exist_ok=True)
    
    clone_url = f"https://oauth2:{github_token}@github.com/{repository_full_name}.git"

    if repository_path.exists() and (repository_path / "HEAD").exists():
        subprocess.run(["git", "remote", "update"], cwd=repository_path, check=True)
    else:
        subprocess.run(["git", "clone", "--mirror", clone_url, str(repository_path)], check=True)

def main():
    load_environment_variables(Path(".env"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--backup-dir", type=Path, required=True)
    parser.add_argument("--specific-repos", nargs="*", default=[])
    arguments = parser.parse_args()

    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")

    ignore_file_path = Path(".backupignore")
    ignored_repositories = load_ignored_repositories(ignore_file_path)

    if arguments.specific_repos:
        repositories_to_backup = arguments.specific_repos
    else:
        repositories_to_backup = fetch_github_repositories(github_token)

    for repository in repositories_to_backup:
        if repository in ignored_repositories:
            continue
        print(f"Backing up: {repository}")
        backup_repository(repository, arguments.backup_dir, github_token)

if __name__ == "__main__":
    main()