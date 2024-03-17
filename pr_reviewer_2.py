#!/usr/bin/env python

import os
from dotenv import load_dotenv
from github import Github
from openai import OpenAI
import argparse
import time

# Load environment variables
load_dotenv()

# Extract the secrets
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
# Initialize OpenAI and GitHub clients
client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)
github = Github(GITHUB_TOKEN)


def review_pull_request(repo_name, pr_number):
    # Fetch the pull request
    repo = github.get_repo(repo_name)
    pull_request = repo.get_pull(pr_number)

    # Extract PR details
    pr_body = pull_request.body
    pr_files = pull_request.get_files()

    # Concatenate file changes to send to OpenAI
    changes = ""
    for file in pr_files[:3]:  # Limit to first 3 files to stay within token limits
        changes += f"File: {file.filename}\n+++ {file.patch}\n\n"

    # Construct the prompt for OpenAI
    prompt = (
        f"Review the following GitHub Pull Request changes:\n{changes}\nProvide a brief description of the changes"
        f" and make a suggestion for improvement of the code in the PR request,\n "
        f"because your comment will be posted as a PR comment, Give me code snippet suggestion on how it the "
        f"changes can be better, how can the code be improved, like more comment, less variables or something "
        f"like that. Thanks.")

    run = client.beta.threads.create_and_run(
        assistant_id=ASSISTANT_ID,
        thread={
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(1)  # Wait for 1 second
        run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id,
            run_id=run.id
        )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=run.thread_id
        )
        print(messages)
    else:
        print(run.status)

    # # Extract and post the OpenAI response as a PR comment
    pull_request.create_issue_comment(messages.data[0].content[0].text.value)


def main(repo_name, pr_number):
    # Your existing logic here
    print(f"Reviewing PR {pr_number} in repo {repo_name}")
    review_pull_request(repo_name, pr_number)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Review a GitHub PR.")
    parser.add_argument("--repo", type=str, required=True, help="Repository name in the format 'owner/repo'")
    parser.add_argument("--pr", type=int, required=True, help="Pull Request number")

    args = parser.parse_args()

    main(args.repo, args.pr)
