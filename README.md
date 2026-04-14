# GitHubBackup

GitHubBackup is a Python-based CLI tool designed to automate local backups of your GitHub repositories. It creates full mirrors, ensuring you have a complete local copy of your code, branches, and commit history.

The tool automatically discovers and backs up every repository you own or contribute to. This includes your personal private repositories and private repositories created by others where you have collaborator access, provided your token has the necessary permissions.

## Features

- **Automated Discovery**: Finds all repositories associated with your account.
- **Full Mirroring**: Uses `git clone --mirror` to back up all branches and tags.
- **Private Repo Support**: Fully supports private repositories via token authentication.
- **Exclusion System**: Easily ignore specific repositories using a `.backupignore` file.
- **Zero Dependencies**: Uses only Python standard libraries and the local Git installation.

## Prerequisites

- Python 3.x
- Git installed and added to your system PATH

## Setup

### 1. Authentication (Classic Token)

To back up all repositories (including private ones from other owners), you must use a **Classic Personal Access Token**.

1. Go to **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
2. Click **Generate new token (classic)**.
3. Give it a descriptive note (e.g., "GitHubBackup CLI").
4. Select the **`repo`** scope. This permission is required to see and clone private repositories you have access to.
5. Generate the token and copy it immediately.

### 2. Environment Configuration

Create a `.env` file in the root directory to store your token. Note that `.env` is already included in `.gitignore` to prevent accidental uploads.

```text
GITHUB_TOKEN="your_github_classic_token_here"
```

### 3. Ignoring Repositories

Create a `.backupignore` file to skip specific repositories. List them using the `owner/repo-name` format (one per line):

```text
# Example .backupignore
some-user/temp-project
old-org/deprecated-repo
```

## Usage

Run the script by providing a target backup directory.

### Backup All Repositories

To discover and backup everything (minus ignored items):

```powershell
python backup.py --backup-dir "C:\Path\To\Backups"
```


### Backup Specific Repositories Only

To bypass auto-discovery and target specific repositories:

```powershell
python backup.py --backup-dir "C:\Path\To\Backups" --specific-repos "owner/repo1" "owner/repo2"
```


## How it Works

- **Mirroring**: The tool uses `git clone --mirror`. This creates a bare repository containing the entire Git database. It does not extract a working directory (the files you see in a standard editor), making it a high-fidelity and space-efficient backup.
- **Updates**: If a repository directory already exists, the script runs `git remote update` to fetch new commits, branches, or tags.
- **Restoration**: To restore a repository from your backup, simply clone the local `.git` folder:
  `git clone C:\Path\To\Backup\owner\repo.git C:\Path\To\Restore`

## Automation

You can automate this on Windows 11 using Task Scheduler for example. 

Example PowerShell command to create a daily task at 2:00 AM:

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Path\To\backup.py --backup-dir D:\Backups"
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
Register-ScheduledTask -TaskName "GitHubBackup" -Action $action -Trigger $trigger
```