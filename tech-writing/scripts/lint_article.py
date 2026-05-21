#!/usr/bin/env python3
"""
lint_article.py — 检查一篇 markdown 技术文章里的 mermaid 块和它周围的文字。

按 tech-writing skill SKILL.md 里规定的规则打分：
  - 各图类型分级的复杂度上限
      flowchart / classDiagram: nodes ≤ 12
      sequenceDiagram:          participants ≤ 8, messages ≤ 15
      stateDiagram-v2:          states ≤ 10, transitions ≤ 15
      erDiagram:                entities ≤ 8
  - flowchart 的边带标签 (≥ 50%)
  - subgraph 有显示名字
  - 全篇 flowchart 方向一致
  - 节点标签人话化（无 ≤2 字符的裸 ID）
  - 节点标签里没嵌 file.ext:行号
  - 每张图前有钩子文字、图后有 ≥30 字符散文
  - 没有 "如图所示" / "见下图" 套话

返回码：0 = 通过；1 = 有任何 ❌。
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

MERMAID_RE = re.compile(r"^```mermaid\s*\n(.*?)\n```", re.MULTILINE | re.DOTALL)

LIMITS: dict[str, dict[str, int]] = {
    "flowchart":       {"nodes": 12},
    "graph":           {"nodes": 12},
    "classDiagram":    {"nodes": 12},
    "sequenceDiagram": {"participants": 8, "messages": 15},
    "stateDiagram-v2": {"states": 10, "transitions": 15},
    "stateDiagram":    {"states": 10, "transitions": 15},
    "erDiagram":       {"entities": 8},
}

RESERVED = {
    "subgraph", "end", "direction", "TD", "LR", "TB", "BT", "RL",
    "classDef", "class", "click", "linkStyle", "style", "state", "note",
}

CODE_REF_RE = re.compile(
    r"[\w/.\-]+\.(?:py|ts|tsx|js|jsx|rs|go|java|rb|cpp|cc|c|h|hpp|kt|swift|sh|md|yaml|yml|json|toml):\d+"
)


def find_blocks(text: str) -> list[tuple[int, int, str]]:
    """返回 [(start_line_1based, end_line_1based, body), ...]"""
    blocks = []
    for m in MERMAID_RE.finditer(text):
        start_line = text[:m.start()].count("\n") + 1
        end_line = start_line + m.group(0).count("\n")
        blocks.append((start_line, end_line, m.group(1)))
    return blocks


def detect_type(body: str) -> str:
    first = body.strip().split("\n", 1)[0].strip()
    for t in (
        "flowchart", "graph", "sequenceDiagram", "stateDiagram-v2",
        "stateDiagram", "classDiagram", "erDiagram", "C4Context",
        "sankey-beta", "pie", "journey", "gitGraph", "mindmap",
    ):
        if first.startswith(t):
            return t
    return "unknown"


def detect_direction(body: str) -> str | None:
    m = re.search(r"\b(TD|LR|TB|BT|RL)\b", body[:200])
    return m.group(1) if m else None


def compute_metrics(body: str, dtype: str) -> dict[str, int]:
    """返回该图类型的关键复杂度指标"""
    if dtype in ("flowchart", "graph"):
        ids = set(re.findall(
            r"\b([A-Za-z_][\w]*)\b(?=\s*(?:\[|\(|\{|-->|---|\.|==|-\.))",
            body,
        ))
        return {"nodes": len(ids - RESERVED)}
    if dtype == "classDiagram":
        return {"nodes": len(set(re.findall(r"\bclass\s+(\w+)", body)))}
    if dtype == "sequenceDiagram":
        participants = set(re.findall(r"participant\s+(\w+)", body))
        participants |= set(re.findall(r"actor\s+(\w+)", body))
        if not participants:
            participants = set(re.findall(r"^\s*(\w+)\s*-?->>?", body, re.MULTILINE))
            participants |= set(re.findall(r"->>?\s*(\w+)", body))
            participants -= RESERVED
        messages = len(re.findall(r"-?->>|--?>|-{1,2}x", body))
        return {"participants": len(participants), "messages": messages}
    if dtype in ("stateDiagram-v2", "stateDiagram"):
        ids = set(re.findall(r"\b([A-Za-z_]\w*)\b\s*-->", body))
        ids |= set(re.findall(r"-->\s*([A-Za-z_]\w*)", body))
        ids -= RESERVED
        transitions = len(re.findall(r"-->", body))
        return {"states": len(ids), "transitions": transitions}
    if dtype == "erDiagram":
        entities = set(re.findall(r"^\s*(\w+)\s*\{", body, re.MULTILINE))
        entities |= set(re.findall(r"^\s*(\w+)\s+[|}o][|}o\-]", body, re.MULTILINE))
        return {"entities": len(entities)}
    return {}


def has_edge_label(line: str) -> bool:
    return "|" in line


def check_naked_labels(body: str, dtype: str) -> list[str]:
    """flowchart 里 ≤2 字符且无显式 [label] 的节点 ID 算"裸"——读者看不懂"""
    if dtype not in ("flowchart", "graph"):
        return []
    ids = set(re.findall(
        r"\b([A-Za-z_][\w]*)\b(?=\s*(?:\[|\(|\{|-->|---|\.|==|-\.))",
        body,
    )) - RESERVED
    labeled = set(re.findall(r"\b([A-Za-z_]\w*)\b\s*[\[\({]", body)) - RESERVED
    naked = sorted(i for i in ids if i not in labeled and len(i) <= 2)
    if naked:
        return [f"裸节点（≤2 字符 ID 且无显式 label）: {naked[:5]}"]
    return []


def check_code_refs_in_diagram(body: str) -> list[str]:
    refs = CODE_REF_RE.findall(body)
    if refs:
        sample = list(dict.fromkeys(refs))[:3]
        return [f"图里嵌了源码行号（应放在散文里）: {sample}"]
    return []


def lint_block(body: str) -> tuple[str, dict[str, int], list[str]]:
    issues: list[str] = []
    dtype = detect_type(body)
    metrics = compute_metrics(body, dtype)

    for k, lim in LIMITS.get(dtype, {}).items():
        actual = metrics.get(k, 0)
        if actual > lim:
            issues.append(f"{k} {actual} > {lim}（考虑拆图）")

    if dtype in ("flowchart", "graph"):
        edge_lines = [
            l for l in body.split("\n")
            if re.search(r"-->|---|==>|-\.->", l) and "subgraph" not in l
        ]
        unlabeled = [e for e in edge_lines if not has_edge_label(e)]
        if edge_lines and len(unlabeled) / len(edge_lines) > 0.5:
            issues.append(
                f"{len(unlabeled)}/{len(edge_lines)} 条边没有标签（>50%）"
            )
        if "subgraph" in body and not re.search(r'subgraph\s+\w+\s*\[', body):
            issues.append("subgraph 没有显示名字（用 `subgraph id[\"名字\"]` 形式）")

    issues.extend(check_naked_labels(body, dtype))
    issues.extend(check_code_refs_in_diagram(body))
    return dtype, metrics, issues


def _collect_prose(line_iter, max_chars: int = 200) -> str:
    """累计连续散文：允许跨单空行，停在双空行 / 标题 / 代码块 / 字数够。"""
    chunks: list[str] = []
    blank_streak = 0
    for l in line_iter:
        s = l.strip()
        if not s:
            blank_streak += 1
            if blank_streak >= 2 and chunks:
                break
            continue
        blank_streak = 0
        if s.startswith("```"):
            break
        if re.match(r"^#{1,6}\s", s):
            break
        chunks.append(s)
        if sum(len(c) for c in chunks) >= max_chars:
            break
    return " ".join(chunks)


def lint_surroundings(text: str, start_line: int, end_line: int) -> list[str]:
    """检查图前 1-2 句钩子 / 图后 3-5 句解读"""
    lines = text.split("\n")
    prev_chunks = _collect_prose(reversed(lines[:start_line - 1])).split(" ")
    prev = " ".join(reversed(prev_chunks))
    nxt = _collect_prose(iter(lines[end_line:]))
    issues = []
    if not prev.strip():
        issues.append("图前没有说明文字")
    elif any(kw in prev for kw in ("如图所示", "见下图", "如下图")):
        issues.append(f"图前用了套话: '{prev[:30]}...'")
    if not nxt.strip():
        issues.append("图后没有解读文字")
    elif len(nxt) < 30:
        issues.append(f"图后解读太短（{len(nxt)} 字符 < 30）")
    return issues


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("用法: lint_article.py <article.md>")
    path = pathlib.Path(sys.argv[1])
    if not path.exists():
        sys.exit(f"文件不存在: {path}")
    text = path.read_text(encoding="utf-8")
    blocks = find_blocks(text)
    if not blocks:
        print(
            "⚠️  整篇文章没有任何 mermaid 块——技术文章里图被低估了，"
            "回去想想哪几段该补图。"
        )
        return
    directions: list[str] = []
    total_issues = 0
    for i, (s, e, body) in enumerate(blocks, 1):
        dtype, metrics, issues = lint_block(body)
        ctx_issues = lint_surroundings(text, s, e)
        d = detect_direction(body)
        if d:
            directions.append(d)
        metrics_str = ", ".join(f"{k}: {v}" for k, v in metrics.items()) or "—"
        print(f"\n图 {i} (行 {s}-{e}, 类型: {dtype}, {metrics_str})")
        all_issues = issues + ctx_issues
        if all_issues:
            for x in all_issues:
                print(f"  ❌ {x}")
                total_issues += 1
        else:
            print("  ✅ 通过所有检查")
    if len(set(directions)) > 1:
        counter = collections.Counter(directions)
        print(f"\n❌ 全篇 flowchart 方向不一致: {dict(counter)}")
        total_issues += 1
    print(f"\n=== 共 {len(blocks)} 张图，{total_issues} 个问题 ===")
    sys.exit(1 if total_issues else 0)


if __name__ == "__main__":
    main()
