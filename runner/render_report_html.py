import json
import datetime
import html
from pathlib import Path
from collections import defaultdict

RESULTS_DIR = Path(__file__).parent.parent / "results"
JSON_PATH = RESULTS_DIR / "payload-log.json"
REPORT_PATH = RESULTS_DIR / "payload-report.html"

VERDICT_COLORS = {
    "BLOCKED": "#3fb950",
    "PARTIAL": "#d29922",
    "SUCCESS": "#f85149",
    "ERROR": "#8b949e",
    "UNKNOWN": "#8b949e",
}


JSON_PATH = RESULTS_DIR / "payload-log.jsonl"

def load_runs():
    if not JSON_PATH.exists():
        return []
    runs = []
    with open(JSON_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                runs.append(json.loads(line))
    return runs


def normalize_verdict(r):
    if r["answer"].startswith("[ERROR]"):
        return "ERROR"
    return r.get("verdict", "UNKNOWN")


def esc(s):
    return html.escape(str(s))


def format_timestamp(ts):
    if not ts or ts == "-":
        return "-"
    try:
        dt = datetime.datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return ts


def render(runs):
    by_tier = defaultdict(list)
    for r in runs:
        by_tier[r.get("tier", "unknown")].append(r)

    scoreboard_rows = ""
    for tier, tier_runs in by_tier.items():
        counts = defaultdict(int)
        for r in tier_runs:
            counts[normalize_verdict(r)] += 1
        scoreboard_rows += f"""
        <tr>
          <td>{esc(tier)}</td>
          <td>{len(tier_runs)}</td>
          <td class="v-blocked">{counts.get('BLOCKED', 0)}</td>
          <td class="v-partial">{counts.get('PARTIAL', 0)}</td>
          <td class="v-success">{counts.get('SUCCESS', 0)}</td>
          <td class="v-error">{counts.get('ERROR', 0)}</td>
        </tr>"""

    tier_sections = ""
    for tier, tier_runs in by_tier.items():
        cards = ""
        for r in tier_runs:
            verdict = normalize_verdict(r)
            color = VERDICT_COLORS.get(verdict, "#8b949e")
            markers = ", ".join(r.get("matched_markers", [])) or "-"
            run_time = format_timestamp(r.get("timestamp", "-"))
            cards += f"""
            <details class="card">
              <summary>
                <span class="badge" style="background:{color}">{verdict}</span>
                <span class="card-id">{esc(r['id'])}</span>
                <span class="card-cat">{esc(r.get('category', '-'))}</span>
                <span class="card-time">{esc(run_time)}</span>
              </summary>
              <div class="card-body">
                <div class="meta">
                  <div><strong>Technique</strong><br>{esc(r.get('technique', '-'))}</div>
                  <div><strong>Markers hit</strong><br>{esc(markers)}</div>
                  <div><strong>Run at</strong><br>{esc(run_time)}</div>
                </div>
                <div class="label">Payload</div>
                <pre>{esc(r['payload'])}</pre>
                <div class="label">Response</div>
                <pre>{esc(r['answer'])}</pre>
              </div>
            </details>"""

        tier_sections += f"""
        <h2>{esc(tier)}</h2>
        {cards}"""

    html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>RAGdoll Injection Report</title>
<style>
  body {{
    background: #0d1117;
    color: #c9d1d9;
    font-family: -apple-system, Segoe UI, sans-serif;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
  }}
  h1 {{ color: #f0f6fc; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
  h2 {{ color: #58a6ff; margin-top: 40px; border-bottom: 1px solid #21262d; padding-bottom: 6px; }}
  .meta-line {{ color: #8b949e; font-size: 14px; margin-bottom: 30px; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
  th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #21262d; }}
  th {{ color: #8b949e; font-weight: 600; font-size: 13px; text-transform: uppercase; }}
  .v-blocked {{ color: #3fb950; font-weight: 600; }}
  .v-partial {{ color: #d29922; font-weight: 600; }}
  .v-success {{ color: #f85149; font-weight: 600; }}
  .v-error {{ color: #8b949e; font-weight: 600; }}
  .card {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    margin-bottom: 12px;
    overflow: hidden;
  }}
  .card summary {{
    padding: 14px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 12px;
    list-style: none;
  }}
  .card summary::-webkit-details-marker {{ display: none; }}
  .badge {{
    color: #0d1117;
    font-weight: 700;
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 12px;
    letter-spacing: 0.5px;
  }}
  .card-id {{ font-weight: 600; color: #f0f6fc; }}
  .card-cat {{ color: #8b949e; font-size: 13px; }}
  .card-time {{ color: #6e7681; font-size: 12px; font-family: 'Cascadia Code', Consolas, monospace; margin-left: auto; }}
  .card-body {{ padding: 0 16px 16px 16px; border-top: 1px solid #21262d; }}
  .meta {{ display: flex; gap: 40px; margin: 14px 0; font-size: 13px; }}
  .meta strong {{ color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase; }}
  .label {{ color: #8b949e; font-size: 12px; text-transform: uppercase; margin: 14px 0 6px 0; font-weight: 600; }}
  pre {{
    background: #010409;
    border: 1px solid #21262d;
    border-radius: 6px;
    padding: 12px;
    white-space: pre-wrap;
    word-break: break-word;
    font-family: 'Cascadia Code', Consolas, monospace;
    font-size: 13px;
    color: #79c0ff;
  }}
</style>
</head>
<body>
  <h1>RAGdoll Injection Test Report</h1>
  <div class="meta-line">
    Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · {len(runs)} payloads run
  </div>

  <h2>Scoreboard</h2>
  <table>
    <tr><th>Tier</th><th>Total</th><th>Blocked</th><th>Partial</th><th>Success</th><th>Error</th></tr>
    {scoreboard_rows}
  </table>

  {tier_sections}
</body>
</html>"""

    REPORT_PATH.write_text(html_doc, encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    runs = load_runs()
    render(runs)