import os
import re
import requests

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = "mink555"
EXCLUDE = {USERNAME}  # 프로필 리포 자체는 제외

# 리포별 커스텀 설명 (없으면 GitHub description 사용)
CUSTOM_DESC = {
    "insurance-compare":       "보험 PDF를 파싱해 당사·타사 암보험 특약을 자동 비교 — 규칙 기반 매칭으로 급부명 차이를 흡수하고 인사이트 리포트 생성",
    "agent-mvp-eval":          "보험 챗봇의 Tool Routing 고도화 — 54개 도구 중 필요한 것만 동적으로 선택해 오호출·비용·지연을 동시에 줄이는 RAG-MCP 패턴 구현",
    "lina-bench":              "폐쇄망 MCP 서빙을 위한 오픈소스 LLM 선정 벤치마크 — 106턴 멀티턴 스트레스 테스트로 5개 모델의 Tool Calling 정확도·한국어 품질 비교",
    "BFCL-V4-Bench":           "BFCL V4 기반 Function Calling 평가 프레임워크 — AST 채점으로 Llama·Mistral·Qwen3 시리즈의 싱글턴 FC 정확도를 정밀 측정",
    "KAKAO-FunctionChat-Bench": "카카오 FunctionChat-Bench 기반 한국어 Tool-Use 평가 — LLM-as-Judge(GPT-4.1)로 1,306개 케이스의 멀티턴 함수 선택 능력 채점",
    "TAU2-Bench":              "τ²-bench 기반 멀티턴 에이전트 평가 — 평균 19턴·6회 tool 호출의 고객센터 시나리오로 5개 모델의 실제 과업 완수율 측정",
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
    table = build_table(repos)
    update_readme(table)
