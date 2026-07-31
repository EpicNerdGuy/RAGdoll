# runner/render_report.py
import json
import datetime
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / "results"
JSONL_PATH = RESULTS_DIR / "payload-log.jsonl"
REPORT_PATH = RESULTS_DIR / "payload-report.md"


def load_runs():
    if not JSONL_PATH.exists():
        return []
    runs = []
    with open(JSONL_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                runs.append(json.loads(line))
    return runs


def render(runs, expand_verdicts=("SUCCESS",)):
    lines = ["# RAGdoll Payload Report\n"]
    lines.append(f"Generated: {datetime.datetime.now().isoformat()}")
    lines.append(f"Total runs logged: {len(runs)}\n")

    lines.append("## Summary\n")
    lines.append("| Timestamp | ID | Tier | Verdict | Markers Hit |")
    lines.append("|---|---|---|---|---|")
    for r in runs:
        ts = r["timestamp"].split(".")[0].split("T")[1]
        markers = ", ".join(r["matched_markers"]) or "-"
        lines.append(f"| {ts} | {r['id']} | {r.get('tier', '-')} | **{r['verdict']}** | {markers} |")

    interesting = [r for r in runs if r["verdict"] in expand_verdicts]
    if interesting:
        lines.append("\n## Expanded Transcripts (interesting runs only)\n")
        for r in interesting:
            lines.append(f"### {r['id']} — {r['verdict']} ({r['timestamp']})")
            lines.append(f"**Payload:**\n```\n{r['payload']}\n```")
            lines.append(f"**Response:**\n```\n{r['answer']}\n```\n")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    runs = load_runs()
    render(runs)