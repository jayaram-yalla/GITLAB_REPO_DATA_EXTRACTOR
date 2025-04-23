
# 🔍 GitLab Repository Metadata Extractor

A fully asynchronous, resumable, and scalable Python script to extract metadata from all repositories in a GitLab instance (SaaS or self-hosted).

---

## 📦 Features

- ✅ Fetches: Project name, ID, description, default branch, languages, file count, and contributor info (name, email, ID)
- ✅ Supports GitLab SaaS and Self-Hosted
- ✅ Fully asynchronous with `aiohttp` and `asyncio`
- ✅ Progress bar via `tqdm`
- ✅ Resumable execution (skips already fetched repos)
- ✅ Output to CSV and HTML formats
- ✅ Execution start/end time tracking

---

## 🚀 How to Run

### 1. 📥 Install Dependencies

```bash
pip install aiohttp pandas tqdm
```

### 2. ▶️ Run the Script

```bash
python gitlab_repo_data_extractor.py \
  --url https://gitlab.yourcompany.com \
  --token glpat-xxxxxxxxxxxxxxxxxxxx \
  --fetch-file-count
```

### 3. 🧾 Output Files

- `gitlab_yourcompany_com_gitlab_repos.csv`: CSV with all metadata
- `gitlab_yourcompany_com_gitlab_repos.html`: HTML table view of same
- Resumable by checking existing CSV and skipping completed project IDs

---

## 🖥️ Sample Console Output

```
🔐 Token is valid!
👤 User: Jayaram Yalla (jayaram.yal)
📧 Email: jayaramyalla@gg.com
🆔 User ID: 1622

📂 Resuming: 1031 already fetched.
📦 Total projects to fetch: 14903

100%|█████████████████████████████████████████| 14903/14903 [07:12<00:00, 34.5it/s]

✅ Completed: 2025-04-23 17:40:12
⏱️ Duration: 0:07:12
✅ Done. 14903 saved to gitlab_yourcompany_com_gitlab_repos.csv and gitlab_yourcompany_com_gitlab_repos.html
```

---

## 📝 Resumability

If you stop the script midway (CTRL+C), it will **preserve all previously fetched data** in the CSV file.  
On re-run, it checks `Project ID` in the existing file and skips them to avoid duplication.

---

## 📑 Sample Output Table

| Project Name     | Project ID | Contributors         | File Count |
|------------------|------------|----------------------|------------|
| invoice-service  | 101        | Ramana, Sheela       | 124        |
| log-analyzer     | 102        | Praveen              | 287        |

---

## 🔗 Links to connect with me
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://in.linkedin.com/in/jayaramyalla)
[![medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://jayaramyalla.medium.com/)
