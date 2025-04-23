import asyncio
import aiohttp
import pandas as pd
import argparse
from aiohttp import ClientSession
from urllib.parse import urlparse
from tqdm.asyncio import tqdm_asyncio
import csv
import os
import sys
from datetime import datetime

# === ARGUMENT PARSER ===
parser = argparse.ArgumentParser(description="GitLab repo metadata extractor")
parser.add_argument("--url", required=True, help="GitLab instance URL")
parser.add_argument("--token", required=True, help="GitLab personal access token")
parser.add_argument("--fetch-file-count", action="store_true", help="Count total files in each repo")
args = parser.parse_args()

GITLAB_URL = args.url.rstrip("/")
TOKEN = args.token
FETCH_FILE_COUNT = args.fetch_file_count
HOSTNAME = urlparse(GITLAB_URL).hostname.replace(".", "_")

OUTPUT_CSV = f"{HOSTNAME}_gitlab_repos.csv"
OUTPUT_HTML = f"{HOSTNAME}_gitlab_repos.html"
HEADERS = {"PRIVATE-TOKEN": TOKEN}
FIELDS = [
    "Project Name", "Project ID", "Description", "Default Branch", "Repo URL",
    "Languages", "Contributors", "Contributor User IDs",
    "Contributor Usernames", "Contributor Emails", "File Count"
]

# === TOKEN VERIFICATION ===
async def verify_token():
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{GITLAB_URL}/api/v4/user") as resp:
            user = await resp.json()
            print("🔐 Token is valid!")
            print(f"👤 User: {user.get('name')} ({user.get('username')})")
            print(f"📧 Email: {user.get('email')}")
            print(f"🆔 User ID: {user.get('id')}\n")

# === FETCH HELPERS ===
async def fetch_languages(session, project_id):
    try:
        async with session.get(f"{GITLAB_URL}/api/v4/projects/{project_id}/languages") as resp:
            return list((await resp.json()).keys())
    except:
        return []

async def fetch_file_count(session, project_id, ref):
    try:
        count = 0
        page = 1
        while True:
            async with session.get(
                f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/tree",
                params={"recursive": True, "per_page": 100, "page": page, "ref": ref}
            ) as resp:
                data = await resp.json()
                if not data:
                    break
                count += len(data)
                page += 1
        return count
    except:
        return -1

async def fetch_contributors_details(session, project_id):
    try:
        emails, names, ids = set(), set(), set()
        page = 1
        while True:
            async with session.get(
                f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/commits",
                params={"per_page": 100, "page": page}
            ) as resp:
                commits = await resp.json()
                if not commits:
                    break
                for c in commits:
                    email = c.get("author_email", "unknown")
                    name = c.get("author_name", "unknown")
                    emails.add(email)
                    names.add(name)
                    ids.add(f"{name}:{email}")
                page += 1
        return ", ".join(names), ", ".join(ids), ", ".join(names), ", ".join(emails)
    except:
        return "Error", "Error", "Error", "Error"

# === PER PROJECT FETCH ===
async def fetch_project_details(session, project):
    project_id = project["id"]
    default_branch = project.get("default_branch", "main")

    contributors_data, languages, file_count = await asyncio.gather(
        fetch_contributors_details(session, project_id),
        fetch_languages(session, project_id),
        fetch_file_count(session, project_id, default_branch) if FETCH_FILE_COUNT else asyncio.sleep(0, result="Skipped")
    )

    contributors, ids, usernames, emails = contributors_data

    return {
        "Project Name": project.get("name", ""),
        "Project ID": project_id,
        "Description": project.get("description", ""),
        "Default Branch": default_branch,
        "Repo URL": project.get("http_url_to_repo", ""),
        "Languages": ", ".join(languages),
        "Contributors": contributors,
        "Contributor User IDs": ids,
        "Contributor Usernames": usernames,
        "Contributor Emails": emails,
        "File Count": file_count,
    }

# === MAIN LOGIC ===
async def fetch_all_projects():
    projects = []
    completed_ids = set()

    if os.path.exists(OUTPUT_CSV):
        df_existing = pd.read_csv(OUTPUT_CSV)
        completed_ids = set(df_existing["Project ID"].astype(int))
        print(f"📂 Resuming: {len(completed_ids)} already fetched.")

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        page = 1
        while True:
            async with session.get(f"{GITLAB_URL}/api/v4/projects", params={"page": page, "per_page": 100, "simple": "true"}) as resp:
                batch = await resp.json()
                if not batch:
                    break
                projects.extend(batch)
                page += 1

        print(f"📦 Total projects to fetch: {len(projects)}\n")

        async def wrapper(project):
            pid = project["id"]
            if pid in completed_ids:
                return None
            try:
                result = await fetch_project_details(session, project)
                with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=FIELDS)
                    if f.tell() == 0:
                        writer.writeheader()
                    writer.writerow(result)
                return result
            except Exception as e:
                print(f"❌ Error with {project.get('name')}: {e}")
                return None

        await tqdm_asyncio.gather(*(wrapper(p) for p in projects))

        df_final = pd.read_csv(OUTPUT_CSV)
        df_final.to_html(OUTPUT_HTML, index=False)
        print(f"✅ Done. {len(df_final)} saved to {OUTPUT_CSV} and {OUTPUT_HTML}")

# === ENTRYPOINT ===
if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        start = datetime.now()
        print(f"🕒 Started: {start.strftime('%Y-%m-%d %H:%M:%S')}\n")
        asyncio.run(verify_token())
        asyncio.run(fetch_all_projects())
        end = datetime.now()
        print(f"\n✅ Completed: {end.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Duration: {end - start}")
    except KeyboardInterrupt:
        print("🛑 Interrupted — partial results saved.")
