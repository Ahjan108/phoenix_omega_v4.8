# GitHub Backup Setup

## What is already set up
- Git repository initialized at `/Users/ahjan/phoenix_omega`
- Manual backup helper: `scripts/git_manual_backup.sh`
- Auto backup script: `scripts/git_autobackup.sh`
- Hourly launchd job installed: `com.ahjan.phoenix_omega.autobackup`

## One-time required commands
Run these once:

```bash
git config --global user.name "YOUR_NAME"
git config --global user.email "YOUR_EMAIL"
cd /Users/ahjan/phoenix_omega
git remote add origin <YOUR_GITHUB_REPO_URL>
```

If the remote already exists, use:

```bash
git remote set-url origin <YOUR_GITHUB_REPO_URL>
```

## First push (recommended)

```bash
cd /Users/ahjan/phoenix_omega
./scripts/git_manual_backup.sh "chore(backup): initial backup"
```

## Daily manual flow

```bash
cd /Users/ahjan/phoenix_omega
./scripts/git_manual_backup.sh "your commit message"
```

## Auto backup behavior
- Runs every 60 minutes via launchd.
- If no changes, it exits without commit.
- Logs:
  - `artifacts/backup_logs/autobackup.log`
  - `artifacts/backup_logs/launchd_stdout.log`
  - `artifacts/backup_logs/launchd_stderr.log`

## Check status

```bash
cd /Users/ahjan/phoenix_omega
./scripts/backup_status.sh
```

## Disable/uninstall auto backup

```bash
cd /Users/ahjan/phoenix_omega
./scripts/uninstall_autobackup_launchd.sh
```
