# Github Backup Python script utility

For local backups of your GitHub repositories.

## Features

- **Clone all accessible GitHub repositories**: Clones all repositories accessible via the configured GitHub Access Token (owned, private, and collaborator repos).
- **Incremental updates:** Keeps backups up to date with incremental fetches, pruning deleted branches to maintain a true mirror.
- **Error handling and logging:** Logs errors, changes, and a summary of each backup run to a configurable log file.
- **Environment configuration (`.env` file):** Centralized configuration via .env for token, log path, and backup directory. Supports both absolute paths and paths relative to the script location.

## Backup Directory Structure

The script stores repositories in the following format `repos/<owner>/<repository>.git`

### Example

```txt
repos
├── owner1
│   └── repo1.git
└── owner2
    ├── repo2.git
    └── repo3.git
```

## Why the `.git` suffix?

Each repository is stored as a **bare repository**.

- Contains only Git’s internal data (commits, branches, tags).
- Lightweight and ideal for backups.
- Can be cloned later to recreate a full working copy.
  
## Restoring from Backup

To restore a working copy from a backup, use `git clone` on the bare repo:

```bash
git clone /path/to/repos/owner1/repo1.git
```

This produces a standard working directory with the full history.

## Setup

1. **Clone this repository**

2. **Configure environment variables**  
   Rename or copy `.env.change` to `.env` and update the following values:

   - **`GITHUB_TOKEN`** → your Personal Access Token.  
     Create a token via GitHub:
       - [Fine‑grained token](https://github.com/settings/personal-access-tokens):  
         Select the desired repository access level (public, all, or specific repos). For private repositories, grant: `Repository permissions → Contents: Read`.
       - [Classic token](https://github.com/settings/tokens):  
         Select the `repo` scope. This grants access to public and private repos, as well as repositories where you are a collaborator.

   - **`BACKUP_DIR`** → path to the backup directory.

   - **`LOG_FILE`** → path to the log file.

3. **Install dependencies**  
   Ensure Python 3 and Git are installed.  
   Verified to work with `Python 3.8.12` and `Python 3.13.5`.

Create a virtual environment

```shell
python3 -m venv .venv
```

Activate the virtual environment

```shell
#  on Windows
.venv\Scripts\activate.bat

# on macOS and Linux
source .venv/bin/activate
```

Install Dependencies

```shell
pip install -r requirements.txt
```

## Usage

Activate the virtual environment

```shell
#  on Windows
.venv\Scripts\activate

# on macOS and Linux
source .venv/bin/activate
```

Run `backup.py` file

```shell
python3 backup.py
```
