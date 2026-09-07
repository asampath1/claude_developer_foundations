#!/usr/bin/env python3
"""Verify the coach program's question files.

Checks each mock exam and coaching session for question/answer-entry counts,
answer-letter balance, difficulty spread, per-domain counts against
`coach/mock_exams/blueprint.md`, complete answer entries, and near-duplicate
stems across every question in the repo (sessions, mocks, and
`study_practice_questions.md`).

    python3 tools/check_questions.py

Exits non-zero when a structural problem is found. Near-duplicate stems are
reported but not treated as failures, since a genuine overlap needs a human
judgement about which of the two to reframe.
"""

import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MOCKS = sorted((REPO / "coach/mock_exams").glob("mock_exam_*.md"))
SESSIONS = sorted((REPO / "coach/sessions").glob("session_*.md"))

EXPECTED_MOCK = {
    "mock_exam_1.md": {"Applications and Integration": 17, "Model Selection and Optimization": 8,
                       "Agents and Workflows": 7, "Prompt and Context Engineering": 6,
                       "Tools and MCP": 5, "Security and Safety": 4, "Claude Code": 2,
                       "Eval, Testing, and Debugging": 1},
    "mock_exam_2.md": {"Applications and Integration": 16, "Model Selection and Optimization": 9,
                       "Agents and Workflows": 7, "Prompt and Context Engineering": 6,
                       "Tools and MCP": 5, "Security and Safety": 4, "Claude Code": 2,
                       "Eval, Testing, and Debugging": 1},
    "mock_exam_3.md": {"Applications and Integration": 17, "Model Selection and Optimization": 8,
                       "Agents and Workflows": 8, "Prompt and Context Engineering": 5,
                       "Tools and MCP": 5, "Security and Safety": 4, "Claude Code": 2,
                       "Eval, Testing, and Debugging": 1},
    "mock_exam_4.md": {"Applications and Integration": 16, "Model Selection and Optimization": 8,
                       "Agents and Workflows": 7, "Prompt and Context Engineering": 6,
                       "Tools and MCP": 6, "Security and Safety": 4, "Claude Code": 2,
                       "Eval, Testing, and Debugging": 1},
}

STEM_STOP = re.compile(r"^(?:-\s+\*\*[A-D]\.\*\*|[A-D]\.)\s")


def parse(path):
    """Return (stems, answers) where stems maps Qn -> stem text."""
    text = path.read_text()
    stems, answers = {}, {}

    # Question stems: '### Qn' blocks that are not answer entries.
    for m in re.finditer(r"^### Q(\d+)\s*$", text, re.M):
        n = int(m.group(1))
        body = text[m.end():]
        nxt = re.search(r"^#{3,4} ", body, re.M)
        block = body[: nxt.start()] if nxt else body
        lines = [ln for ln in block.strip().splitlines() if not STEM_STOP.match(ln.strip())]
        stems[n] = " ".join(" ".join(lines).split())

    # Answer entries: '#### Qn — Answer: X' (mocks/sessions) or '### Qn — Answer: X'
    for m in re.finditer(r"^#{3,4} Q(\d+) — Answer:\s*([A-D])\s*$", text, re.M):
        n = int(m.group(1))
        body = text[m.end():]
        nxt = re.search(r"^#{2,4} ", body, re.M)
        block = body[: nxt.start()] if nxt else body
        answers[n] = {
            "letter": m.group(2),
            "difficulty": (re.search(r"\*\*Difficulty:\*\*\s*(\w+)", block) or [None, "?"])[1]
            if re.search(r"\*\*Difficulty:\*\*\s*(\w+)", block) else "?",
            "domain": (re.search(r"\*\*Domain:\*\*\s*(.+)", block).group(1).strip()
                       if re.search(r"\*\*Domain:\*\*\s*(.+)", block) else None),
            "tag": (re.search(r"\*\*Tag:\*\*\s*`?([^`\n]+)`?", block).group(1).strip()
                    if re.search(r"\*\*Tag:\*\*\s*`?([^`\n]+)`?", block) else None),
            "body": block,
        }
    return stems, answers


def practice_stems():
    text = (REPO / "study_practice_questions.md").read_text()
    out = {}
    for m in re.finditer(r"^\*\*(\d+)\.\*\*\s*(.+?)(?=^\n?(?:-\s+\*\*A\.\*\*|A\.)\s)", text, re.M | re.S):
        out[int(m.group(1))] = " ".join(m.group(2).split())
    return out


def normalize(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower())


def main():
    problems = []
    all_stems = []  # (label, text)

    for path in MOCKS:
        stems, answers = parse(path)
        name = path.name
        print(f"\n=== {name} ===")
        print(f"questions: {len(stems)}  answer entries: {len(answers)}")
        if len(stems) != 50:
            problems.append(f"{name}: {len(stems)} questions, expected 50")
        missing = sorted(set(range(1, 51)) - set(answers))
        if missing:
            problems.append(f"{name}: missing answer entries for {missing}")
        letters = Counter(a["letter"] for a in answers.values())
        print("letters:", dict(sorted(letters.items())))
        for L in "ABCD":
            if not (9 <= letters.get(L, 0) <= 16):
                problems.append(f"{name}: letter {L} appears {letters.get(L,0)} times")
        print("difficulty:", dict(Counter(a["difficulty"] for a in answers.values())))
        domains = Counter(a["domain"] for a in answers.values())
        exp = EXPECTED_MOCK[name]
        for dom, want in exp.items():
            got = domains.get(dom, 0)
            if got != want:
                problems.append(f"{name}: domain '{dom}' has {got}, expected {want}")
        unknown = set(domains) - set(exp)
        if unknown:
            problems.append(f"{name}: unrecognized domain labels {unknown}")
        print("domains ok" if not any(p.startswith(name) and "domain" in p for p in problems)
              else f"domains: {dict(domains)}")
        for n, s in stems.items():
            all_stems.append((f"{name}:Q{n}", s))
        # incomplete answer entries
        for n, a in answers.items():
            for field in ("Why not", "Difficulty", "Domain", "Tag", "Revise"):
                if field not in a["body"]:
                    problems.append(f"{name}:Q{n}: answer entry missing '{field}'")

    total_sessions = 0
    for path in SESSIONS:
        stems, answers = parse(path)
        total_sessions += len(stems)
        if len(stems) != len(answers):
            problems.append(f"{path.name}: {len(stems)} questions vs {len(answers)} answers")
        letters = Counter(a["letter"] for a in answers.values())
        print(f"{path.name}: {len(stems)} questions, letters {dict(sorted(letters.items()))}")
        for n, s in stems.items():
            all_stems.append((f"{path.name}:Q{n}", s))
    print(f"\nsession questions total: {total_sessions}")

    for n, s in practice_stems().items():
        all_stems.append((f"study_practice_questions.md:Q{n}", s))
    print(f"total stems compared: {len(all_stems)}")

    # near-duplicate detection
    print("\n=== near-duplicate stems (ratio >= 0.72) ===")
    norm = [(label, normalize(s)) for label, s in all_stems]
    dupes = 0
    for i in range(len(norm)):
        li, si = norm[i]
        for j in range(i + 1, len(norm)):
            lj, sj = norm[j]
            if abs(len(si) - len(sj)) > max(len(si), len(sj)) * 0.5:
                continue
            r = SequenceMatcher(None, si, sj).ratio()
            if r >= 0.72:
                dupes += 1
                print(f"{r:.2f}  {li}  <->  {lj}")
                print(f"      A: {si[:150]}")
                print(f"      B: {sj[:150]}")
    if not dupes:
        print("none")

    print("\n=== problems ===")
    if problems:
        for p in problems:
            print("-", p)
    else:
        print("none")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
