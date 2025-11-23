import os
from dotenv import load_dotenv
from github import Github, Auth, Repository
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

def backup_repo(token: str, repo: Repository.Repository, owner: str, dir: str):
    logging.info(f"Working on target repo '{repo.name}' (Private: {repo.private})")
    # Check if repository is present in dir relative to the file location
    path = os.path.join(base_dir, dir, repo.name + ".git")
    if (os.path.exists(path)):
        # git remote update
        logging.info(f"Updating repo with 'git remote update'")
        subprocess.run(["git", "-C", f"{path}", "remote", "update"], check=True)
    else:
        # git clone --mirror
        logging.info(f"New repo, creating mirror clone")
        subprocess.run(["git", "-C", f"{os.path.join(base_dir, dir)}", "clone", f"https://{token}@github.com/{owner}/{repo.name}.git", "--mirror"], check=True)
    logging.info(f"Successfully backed up the repo '{repo.name}'")

def main():
    load_dotenv()
    log_file = os.path.join(base_dir, os.getenv("LOG_FILE") or "logfile.log")
    logging.basicConfig(filename=log_file, level=logging.INFO)
    
    try:
        logging.info(f"Backup started at {datetime.datetime.now().isoformat()}")
        
        token: str = os.getenv('GIT_TOKEN_CLASSIC') or ""
        dir: str = os.getenv('BACKUP_DIR') or ""
        
        if (not os.path.exists(os.path.join(base_dir, dir))):
            os.mkdir(os.path.join(base_dir, dir))
        g = get_github(token)
        
        for repo in g.get_user().get_repos():
            backup_repo(token, repo, repo.owner.login, dir)        

        logging.info(f"Backup completed successfully at {datetime.datetime.now().isoformat()}")
    except Exception as e:
        logging.error(f"Backup failed: {e}")
    
    
if __name__ == "__main__":
    main()