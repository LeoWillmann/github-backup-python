import os
from dotenv import load_dotenv
from github import Github, Auth, Repository, PaginatedList
import subprocess
import logging
import datetime

base_dir = os.path.dirname(os.path.abspath(__file__))

# Get the github object reference and check if token is valid
def get_github(token:str):
    try:
        g = Github(auth=Auth.Token(token))
        g.get_user().login
        return g
    except:
        raise ValueError("Invalid token")

def backup_repo(token: str, repo: Repository.Repository, owner: str, dir: str)-> bool:  
    # Check if repository is present in dir relative to the file location
    path = os.path.join(base_dir, dir, repo.name + ".git")
    if (not os.path.exists(path)):
        # git clone --mirror once
        url: str = f"https://{token}@github.com/{repo.full_name}.git"
        logging.info(f"New target repo '{repo.full_name}' (Private: {repo.private}) cloned")
        subprocess.run(["git", "-C", f"{os.path.join(base_dir, dir)}", "clone", url, "--mirror"], check=True)
        return True
    else:
        # Dry-run fetch to see if anything new
        result = subprocess.run(["git", "-C", f"{path}", "fetch", "--dry-run"], capture_output=True, text=True)
        if result.stdout.strip() or result.stderr.strip():
            # Only log if something new
            subprocess.run(["git", "-C", f"{path}", "remote", "update" , "--prune"], check=True)
            logging.info(f"Updated '{repo.full_name}' with new content")
            return True
    return False

def main():
    parsed: int = 0
    updated: int = 0
    repoCount: int = 0
    
    load_dotenv()
    # create logging
    log_file = (os.path.join(base_dir, os.getenv("LOG_FILE") or "logfile")) + ".log"
    logging.basicConfig(
        filename=log_file, 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    start: datetime.datetime = datetime.datetime.now()
    logging.info(f"Backup started")
    try:
        # Get environment variables
        token: str = os.getenv('GIT_TOKEN_CLASSIC') or ""
        dir: str = os.getenv('BACKUP_DIR') or ""
        
        # Create directory folder if it does not exist
        if (not os.path.exists(os.path.join(base_dir, dir))):
            os.mkdir(os.path.join(base_dir, dir))
        
        # Get github repositories and back them up
        g = get_github(token)
        repos: PaginatedList.PaginatedList[Repository.Repository] = g.get_user().get_repos()
        repoCount = repos.totalCount
        for repo in repos:
            parsed += 1
            updated += 1 if backup_repo(token, repo, repo.owner.login, dir) else 0
        
    except Exception as e:
        logging.error(f"Backup failed: {e}")
    finally:
        end: datetime.datetime = datetime.datetime.now()
        diff: datetime.timedelta = end - start
        
        if (repoCount == parsed):
            logging.info(f"Backup completed successfully. Elapsed {diff.total_seconds()} seconds with" +
                f" {parsed} repos parsed and {updated} updated")
        else:
            logging.warning(f"Could not parse all {repoCount} repos. Elapsed {diff.total_seconds()} seconds with" +
                f" {parsed} repos parsed and {updated} updated")

    
if __name__ == "__main__":
    main()