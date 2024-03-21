import os
import requests

# Load your GitHub Personal Access Token and OpenAI API key from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# GitHub API URL for fetching PR details (example)
GITHUB_PR_URL = 'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}'

# OpenAI API URL for making requests
OPENAI_URL = 'https://api.openai.com/v1/completions'


def fetch_pr_details(owner, repo, pull_number):
    """
    Fetch details of a given pull request from GitHub.
    """
    url = GITHUB_PR_URL.format(owner=owner, repo=repo, pull_number=pull_number)
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


def analyze_pr_with_openai(pr_description):
    """
    Use OpenAI to analyze the pull request description and suggest improvements.
    """


    data = {
        "model": "text-davinci-003",  # You can choose the model you prefer
        "prompt": f"Review the following GitHub pull request description and provide a summary and suggestions for improvement:\n\n'{pr_description}'",
        "temperature": 0.7,
        "max_tokens": 150,
    }
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.post(OPENAI_URL, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    owner = 'exampleOwner'  # GitHub repository owner
    repo = 'exampleRepo'  # GitHub repository name
    pull_number = 1  # Pull request number

    # Fetch PR details
    pr_details = fetch_pr_details(owner, repo, pull_number)
    pr_description = pr_details.get('body', 'No description provided.')

    # Analyze PR with OpenAI
    analysis_result = analyze_pr_with_openai(pr_description)
    print("OpenAI Analysis Result:", analysis_result['choices'][0]['text'])


if __name__ == "__main__":
    main()
