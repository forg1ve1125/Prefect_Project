import os
import subprocess
from prefect import flow, get_run_logger
from prefect.blocks.system import Secret
from utils.exchange_rate_fetcher import fetch_last_month_rates


def push_to_github(file_path, logger):
    """
    Push the generated file back to GitHub.
    Requires a Prefect Secret block named 'github-pat' containing a GitHub Personal Access Token.
    """
    try:
        # Try to load the secret
        try:
            github_token_block = Secret.load("github-pat")
            token = github_token_block.get()
        except ValueError:
            logger.warning("Secret 'github-pat' not found. Skipping push to GitHub.")
            logger.warning("To enable auto-save to Git, create a Secret block named 'github-pat' with your GitHub Personal Access Token.")
            return

        # Construct remote URL with authentication
        # Note: Using the specific repo URL
        repo_url = f"https://oauth2:{token}@github.com/forg1ve1125/Prefect_Project.git"
        
        # Configure git (required for commit in CI/CD)
        subprocess.run(["git", "config", "user.email", "prefect-bot@prefect.io"], check=True)
        subprocess.run(["git", "config", "user.name", "Prefect Bot"], check=True)
        
        # Add file
        # Ensure we use a path relative to the repo root if possible, or absolute
        subprocess.run(["git", "add", file_path], check=True)
        
        # Check status to see if there's anything to commit
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            logger.info("No changes to commit (file might be unchanged).")
            return

        # Commit
        filename = os.path.basename(file_path)
        subprocess.run(["git", "commit", "-m", f"Auto-update data: {filename}"], check=True)
        
        # Push
        subprocess.run(["git", "push", repo_url, "main"], check=True)
        logger.info(f"Successfully pushed {filename} to GitHub.")

    except Exception as e:
        logger.error(f"Failed to push to GitHub: {e}")


@flow(name="currency_acquisition_flow")
def currency_acquisition_flow():
    """
    Fetch last month's FX rates (idempotent).
    Scheduled monthly via Prefect Cloud.
    """
    logger = get_run_logger()
    logger.info("Running monthly FX acquisition task...")

    fx_path = fetch_last_month_rates()

    logger.info(f"FX acquisition complete: {fx_path}")
    
    # Attempt to push to GitHub
    push_to_github(fx_path, logger)
    
    return fx_path


if __name__ == "__main__":
    currency_acquisition_flow()
