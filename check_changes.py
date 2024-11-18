import os
import requests

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# Files and patterns to look for
TARGET_EXTENSIONS = (".cmake", "CMakeLists.txt", ".bb")
COMMENT_IDENTIFIER = "<!-- 48f61f98664448a973e3fb00b28723ce170dac87 -->\n⚠️ CMake or .bb changes detected"

def get_pr_files(repo, pr_number, token):
    """
    Fetches the changed files of a pull request.
    """
    headers = {"Authorization": f"Bearer {token}"}
    files_url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}/files"
    response = requests.get(files_url, headers=headers)
    response.raise_for_status()
    return response.json()

def check_file_changes(files):
    """
    Checks if relevant files were changed or renamed.
    """
    for file in files:
        if any(file["filename"].endswith(ext) for ext in TARGET_EXTENSIONS) or file.get("status") == "renamed":
            return True
    return False

def get_existing_review_comments(repo, pr_number, token):
    """
    Fetches existing review comments on a pull request.
    """
    headers = {"Authorization": f"Bearer {token}"}
    comments_url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}/reviews"
    response = requests.get(comments_url, headers=headers)
    response.raise_for_status()
    return response.json()

def post_pr_review_comment(repo, pr_number, token, comment):
    """
    Adds a review comment to the pull request.
    """
    headers = {"Authorization": f"Bearer {token}"}
    review_url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}/reviews"
    payload = {
        "body": comment,
        "event": "REQUEST_CHANGES"
    }
    response = requests.post(review_url, headers=headers, json=payload)
    response.raise_for_status()

def check_and_comment(repo, pr_number, token):
    """
    Checks for changes and adds a comment if necessary.
    """
    files = get_pr_files(repo, pr_number, token)
    
    if check_file_changes(files):
        existing_comments = get_existing_review_comments(repo, pr_number, token)
        for comment in existing_comments:
            if COMMENT_IDENTIFIER in comment["body"]:
                print("Relevant comment already exists.")
                return

        comment = (
            f"{COMMENT_IDENTIFIER}\n\n"
            "Changes to CMake configuration files (.cmake, CMakeLists.txt) or .bb files detected. "
            "Please ensure these changes are reviewed. This comment must be resolved."
        )
        post_pr_review_comment(repo, pr_number, token, comment)
        print("Comment successfully added.")
    else:
        print("No relevant changes found.")

def main():
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("GITHUB_PULL_REQUEST_NUMBER")
    github_token = os.getenv("GH_TOKEN")
    check_and_comment(repo, pr_number, github_token)

if __name__ == "__main__":
    main()