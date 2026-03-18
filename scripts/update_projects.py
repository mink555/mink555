import os
import re
import requests

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = "mink555"
EXCLUDE = {USERNAME}  # 프로필 리포 자체는 제외

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def fetch_repos():
    repos = []
    page = 1
    while True:
        res = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            headers=headers,
            params={"per_page": 100, "page": page, "sort": "updated", "type": "owner"},
        )
        data = res.json()
        if not data:
            break
        for r in data:
            if not r["private"] and r["name"] not in EXCLUDE and not r["fork"]:
                repos.append(r)
        page += 1
    return repos


def build_table(repos):
    if not repos:
        return ""

    rows = []
    for i in range(0, len(repos), 2):
        pair = repos[i : i + 2]
        cells = []
        for r in pair:
            name = r["name"]
            url = r["html_url"]
            desc = r["description"] or ""
            cells.append(
                f'<td width="50%" valign="top">\n\n'
                f"**[{name}]({url})**\n"
                f"{desc}\n\n"
                f"</td>"
            )
        if len(cells) == 1:
            cells.append('<td width="50%"></td>')
        rows.append("<tr>\n" + "\n".join(cells) + "\n</tr>")

    return "<table>\n" + "\n".join(rows) + "\n</table>"


def update_readme(table):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    new_block = f"<!-- PROJECTS_START -->\n{table}\n<!-- PROJECTS_END -->"
    updated = re.sub(
        r"<!-- PROJECTS_START -->.*?<!-- PROJECTS_END -->",
        new_block,
        content,
        flags=re.DOTALL,
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)
    print("README.md updated.")


if __name__ == "__main__":
    repos = fetch_repos()
    print(f"Found {len(repos)} public repos.")
    table = build_table(repos)
    update_readme(table)
