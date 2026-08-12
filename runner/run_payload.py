# runner/run_payload.py
import sys, os, re, json, yaml, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "target"))
from query import build_chain, ask

PAYLOAD_ROOT = Path(__file__).parent.parent / "payloads"
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

def parse_payload_md(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig", errors="replace").replace("\r\n", "\n")

    match = re.match(r"^\s*---[ \t]*\n(.*?)\n---[ \t]*\n(.*)$", text, re.DOTALL)
    if not match:
        print(f"  [skip] {path.name}: no frontmatter match | first 30 chars: {text[:30]!r}")
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        print(f"  [skip] {path.name}: YAML parse error -> {e}")
        return None

    if not isinstance(frontmatter, dict):
        print(f"  [skip] {path.name}: frontmatter did not parse to a dict")
        return None

    body = match.group(2)
    section_match = re.search(r"## Payload\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
    if not section_match:
        print(f"  [skip] {path.name}: no ## Payload section found")
        return None

    raw_section = section_match.group(1).strip()
    fenced = re.match(r"^```(?:\w*)\n(.*?)\n```$", raw_section, re.DOTALL)
    payload_text = fenced.group(1).strip() if fenced else raw_section.strip()

    if not payload_text:
        print(f"  [skip] {path.name}: ## Payload section is empty")
        return None

    if "id" not in frontmatter:
        frontmatter["id"] = path.stem

    frontmatter["payload_text"] = payload_text
    frontmatter["source_file"] = str(path.relative_to(PAYLOAD_ROOT))
    return frontmatter


def score(response_text: str, success_markers: list, partial_markers: list = None):
    text_lower = response_text.lower()
    hit_success = [m for m in success_markers if m.lower() in text_lower]
    hit_partial = [m for m in (partial_markers or []) if m.lower() in text_lower]

    if hit_success and hit_partial:
        return "PARTIAL", hit_success + hit_partial
    elif hit_success:
        return "SUCCESS", hit_success
    elif hit_partial:
        return "BLOCKED", hit_partial
    else:
        return "UNKNOWN", []


def run_all(subdir: str = None):
    qa_chain = build_chain()
    search_root = (PAYLOAD_ROOT / subdir) if subdir else PAYLOAD_ROOT
    all_files = sorted(search_root.rglob("*.md"))

    print(f"[discover] found {len(all_files)} .md files under {search_root}")
    for f in all_files:
        print(f"  - {f.relative_to(PAYLOAD_ROOT)}")

    results = []
    for f in all_files:
        parsed = parse_payload_md(f)
        if not parsed:
            print(f"[skip] couldn't parse {f}")
            continue

        print(f"[running] {parsed['id']}")
        try:
            result = ask(qa_chain, parsed["payload_text"])
            answer = result["answer"]
        except Exception as e:
            answer = f"[ERROR] {e}"
            print(f"  [error] ask() failed on {parsed['id']} -> {e}")

        verdict, hits = score(
            answer,
            parsed.get("success_markers", []),
            parsed.get("partial_markers", [])
        )
        results.append({
            "id": parsed["id"],
            "tier": parsed.get("tier"),
            "category": parsed.get("category"),
            "technique": parsed.get("technique"),
            "source_file": parsed["source_file"],
            "payload": parsed["payload_text"],
            "answer": answer,
            "verdict": verdict,
            "matched_markers": hits,
            "timestamp": datetime.datetime.now().isoformat(),
        })

    write_json(results)
    write_md(results)
    print(f"\nDone. {len(results)} payloads run. See results/payload-log.md")


def write_json(results):
    path = RESULTS_DIR / "payload-log.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")


def write_md(results):
    path = RESULTS_DIR / "payload-log.md"
    lines = ["# RAGdoll Payload Run Log\n"]
    lines.append(f"Run at: {datetime.datetime.now().isoformat()}\n")
    lines.append("| ID | Tier | Category | Verdict | Markers Hit |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        lines.append(f"| {r['id']} | {r['tier']} | {r['category']} | **{r['verdict']}** | {', '.join(r['matched_markers']) or '-'} |")

    lines.append("\n## Full Transcripts\n")
    for r in results:
        lines.append(f"### {r['id']} - {r['verdict']}")
        lines.append(f"**Payload:**\n```\n{r['payload']}\n```")
        lines.append(f"**Response:**\n```\n{r['answer']}\n```\n")

    with open(path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n\n---\n\n")


if __name__ == "__main__":
    target_subdir = sys.argv[1] if len(sys.argv) > 1 else None
    run_all(target_subdir)