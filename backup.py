import os
from dotenv import load_dotenv
from github import Github, Auth, Repository, PaginatedList
import subprocess
import logging
import datetime

# Get the github object reference and check if token is valid
def get_github(token:str):
    try:
        g = Github(auth=Auth.Token(token))
        g.get_user().login
        return g
    except:
        raise ValueError("Invalid token")


def backup_repo(token: str, repo: Repository.Repository, dir: str, remote:str = "origin")-> bool:  
    """
    Docstring for backup_repo
    
    :param token: Github token
    :type token: str
    :param repo: Github repository object
    :type repo: Repository.Repository
    :param dir: Directory to store repositories in, relative to the python script
    :type dir: str
    :param remote: The remote string, default = origin
    :type remote: str
    :return: True when the repo updated, false otherwise
    :rtype: bool
    """
    # Check if repository is present in dir relative to the file location
    repoPath = os.path.join(dir, repo.owner.login, repo.name + ".git")
    url: str = f"https://{token}@github.com/{repo.full_name}.git"
    
    # Clone the repo for the first time, then update incrementally
    if (not os.path.exists(repoPath)):
        # Ensure the owner dir exists
        ownerDir = os.path.dirname(repoPath)        
        if (not os.path.exists(ownerDir)):
            os.mkdir(ownerDir)
        
        # git clone --mirror
        subprocess.run(["git", "-C", f"{ownerDir}", "clone", url, "--mirror"], check=True)
        logging.info(f"New target repo '{repo.full_name}' (Private: {repo.private}) cloned")
        return True
    else:
        # Update remote url in-case access token changed
        subprocess.run(["git", "-C", repoPath, "remote", "set-url", remote, url], check=True)
        # Update repository and store output
        result = subprocess.run(["git", "-C", f"{repoPath}", "remote", "update" , "--prune"], check=True, capture_output=True, text=True)
        if result.stdout.strip() or result.stderr.strip():
            # If the output is not empty, log that the repo updated
            logging.info(f"Updated '{repo.full_name}' with new content")
            return True
    return False


def handle_log_file(log_file:str):
    if (not os.path.isabs(log_file)):
        # Path is relative
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(base_dir, log_file)
        
    logging.basicConfig(
        filename=log_file, 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def get_repo_dir(dir:str) -> str:
    if (not os.path.isabs(dir)):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dir = os.path.join(base_dir, dir)
    # Create directory folder if it does not exist
    if (not os.path.exists(dir)):
        os.makedirs(dir)
    return dir
    
    
def main():
    parsed: int = 0
    updated: int = 0
    repoCount: int = 0
    
    load_dotenv()
    # create logging
    handle_log_file(os.getenv("LOG_FILE") or "logfile.log")
    
    start: datetime.datetime = datetime.datetime.now()
    logging.info(f"Backup started")
    try:
        # Get environment variables
        token: str = os.getenv('GITHUB_TOKEN') or ""
        # Get github repositories and back them up
        g = get_github(token)
        
        dir = get_repo_dir(os.getenv('BACKUP_DIR') or "repos")
        repos: PaginatedList.PaginatedList[Repository.Repository] = g.get_user().get_repos()
        repoCount = repos.totalCount
        for repo in repos:
            updated += 1 if backup_repo(token, repo, dir) else 0
            parsed += 1
        
    except Exception as e:
        logging.error(f"Backup failed: {e}")
        raise e
    finally:
        end: datetime.datetime = datetime.datetime.now()
        diff: datetime.timedelta = end - start
        
        if (repoCount == parsed):
            logging.info(f"Backup completed. Parsed {parsed} " + 
                f"repos and updated {updated} in {diff.total_seconds()} seconds.")
        else:
            logging.warning(f"Could not parse all {repoCount} repos. Parsed {parsed} " + 
                f"repos and updated {updated} in {diff.total_seconds()} seconds.")

    
if __name__ == "__main__":
    main()