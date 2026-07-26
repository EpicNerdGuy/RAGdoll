# runner/run_payload.py
import sys, os, re, json, yaml, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "target"))
from query import build_chain, ask

PAYLOAD_ROOT = Path(__file__).parent.parent / "payloads"
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

def parse_payload_md(path: Path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        return None
    frontmatter = yaml.safe_load(match.group(1))
    body = match.group(2)

    payload_match = re.search(r"## Payload\s*```\s*(.*?)\s*```", body, re.DOTALL)
    if not payload_match:
        return None
    frontmatter["payload_text"] = payload_match.group(1).strip()
    frontmatter["source_file"] = str(path.relative_to(PAYLOAD_ROOT))
    return frontmatter

def score(response_text: str, success_markers: list):
    hit = [m for m in success_markers if m.lower() in response_text.lower()]
    return "SUCCESS" if hit else "BLOCKED", hit

def run_all():
    qa_chain = build_chain()
    all_files = list(PAYLOAD_ROOT.rglob("*.md"))
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

        verdict, hits = score(answer, parsed.get("success_markers", []))

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
    path = RESULTS_DIR / "payload-log.json"
    existing = []
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
    existing.extend(results)
    path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

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
        lines.append(f"### {r['id']} — {r['verdict']}")
        lines.append(f"**Payload:**\n```\n{r['payload']}\n```")
        lines.append(f"**Response:**\n```\n{r['answer']}\n```\n")

    with open(path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n\n---\n\n")

if __name__ == "__main__":
    run_all()