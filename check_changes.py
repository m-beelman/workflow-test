import os
import requests

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# Dateien und Muster, nach denen gesucht wird
TARGET_EXTENSIONS = (".cmake", "CMakeLists.txt", ".bb")
COMMENT_IDENTIFIER = "⚠️ CMake- oder .bb-Änderungen erkannt"  # Eindeutiger Text im Kommentar

def get_pr_files(repo, pr_number, token):
    """
    Holt die geänderten Dateien eines Pull-Requests.
    """
    headers = {"Authorization": f"Bearer {token}"}
    files_url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}/files"
    response = requests.get(files_url, headers=headers)
    response.raise_for_status()
    return response.json()

def check_file_changes(files):
    """
    Überprüft, ob relevante Dateien geändert oder umbenannt wurden.
    """
    for file in files:
        if any(file["filename"].endswith(ext) for ext in TARGET_EXTENSIONS) or file.get("status") == "renamed":
            return True
    return False

def get_existing_comments(repo, pr_number, token):
    """
    Holt alle Kommentare für den Pull-Request.
    """
    headers = {"Authorization": f"Bearer {token}"}
    comments_url = f"{GITHUB_API_URL}/repos/{repo}/issues/{pr_number}/comments"
    response = requests.get(comments_url, headers=headers)
    response.raise_for_status()
    return response.json()

def post_pr_comment(repo, pr_number, token, comment):
    """
    Fügt einen Kommentar in den Pull-Request ein.
    """
    headers = {"Authorization": f"Bearer {token}"}
    comments_url = f"{GITHUB_API_URL}/repos/{repo}/issues/{pr_number}/comments"
    payload = {"body": comment}
    response = requests.post(comments_url, headers=headers, json=payload)
    response.raise_for_status()

def check_and_comment(repo, pr_number, token):
    """
    Überprüft die Änderungen und fügt bei Bedarf einen Kommentar hinzu.
    """
    # PR-Dateien abrufen
    files = get_pr_files(repo, pr_number, token)

    # Überprüfen, ob relevante Änderungen vorliegen
    if check_file_changes(files):
        # Bestehende Kommentare prüfen
        comments = get_existing_comments(repo, pr_number, token)
        for comment in comments:
            if COMMENT_IDENTIFIER in comment["body"]:
                print("Relevanter Kommentar existiert bereits.")
                return  # Kommentar ist bereits vorhanden

        # Kommentar erstellen, wenn keiner existiert
        comment = (
            f"{COMMENT_IDENTIFIER}\n\n"
            "Es wurden Änderungen an Dateien mit CMake-Konfiguration (.cmake, CMakeLists.txt) oder .bb-Dateien festgestellt. "
            "Bitte sicherstellen, dass diese Änderungen überprüft werden. Dieser Kommentar muss gelöst werden."
        )
        post_pr_comment(repo, pr_number, token, comment)
        print("Kommentar erfolgreich hinzugefügt.")
    else:
        print("Keine relevanten Änderungen gefunden.")

def main():
    # Umgebungsvariablen für GitHub Actions
    repo = os.getenv("GITHUB_REPOSITORY")  # Format: "owner/repo"
    pr_number = os.getenv("GITHUB_PULL_REQUEST_NUMBER")  # PR-Nummer
    github_token = os.getenv("GITHUB_TOKEN")  # GitHub Token

    if not all([repo, pr_number, github_token]):
        print("Fehlende Umgebungsvariablen: GITHUB_REPOSITORY, GITHUB_PULL_REQUEST_NUMBER oder GITHUB_TOKEN.")
        exit(1)

    # Änderungen prüfen und kommentieren
    check_and_comment(repo, pr_number, github_token)

if __name__ == "__main__":
    main()
