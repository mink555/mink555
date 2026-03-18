import os
import re
import requests

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = "mink555"
EXCLUDE = {USERNAME}  # 프로필 리포 자체는 제외

# 리포별 커스텀 설명 (없으면 GitHub description 사용)
CUSTOM_DESC = {
    "insurance-compare":        "보험 PDF 파싱 → 당사·타사 암보험 특약 자동 비교 및 인사이트 리포트 생성",
    "agent-mvp-eval":           "RAG-MCP 패턴으로 54개 보험 도구 중 필요한 것만 동적 선택 — 오호출·비용·지연 개선",
    "lina-bench":               "폐쇄망 LLM 선정 벤치마크 — 106턴 멀티턴으로 5개 모델의 Tool Calling 정확도 비교",
    "BFCL-V4-Bench":            "BFCL V4 기반 Function Calling 벤치마크 — AST 채점으로 주요 LLM FC 정확도 정밀 측정",
    "KAKAO-FunctionChat-Bench": "카카오 FunctionChat-Bench 기반 — LLM-as-Judge로 1,306개 한국어 Tool-Use 케이스 채점",
    "TAU2-Bench":               "τ²-bench 기반 멀티턴 에이전트 평가 — 고객센터 시나리오로 5개 모델의 과업 완수율 측정",
}

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
            desc = CUSTOM_DESC.get(name) or r["description"] or ""
            cells.append(
                f'<td width="50%" valign="top">\n\n'
                f"**[{name}]({url})**  \n"
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

    # 각 리포 description(About) 업데이트
    for r in repos:
        name = r["name"]
        if name in CUSTOM_DESC:
            desc = CUSTOM_DESC[name]
            if r["description"] != desc:
                requests.patch(
                    f"https://api.github.com/repos/{USERNAME}/{name}",
                    headers=headers,
                    json={"description": desc},
                )
                print(f"Updated description: {name}")

    table = build_table(repos)
    update_readme(table)
