# RAGdoll

RAGdoll is a local RAG pipeline built for one purpose: getting attacked by its own creator. It stands up a working LangChain RAG stack over a hardcoded Steins;Gate wiki PDF, then systematically breaks it through prompt injection and system prompt extraction, logging every payload into a reusable library along the way.

Current status: 7 direct prompt injection payloads landed. Indirect prompt injection payloads coming soon.


## What it actually does

1. Ingests a set of documents into a local vector store
2. Answers questions by retrieving relevant chunks and stuffing them into the model's context
3. Gets attacked, on purpose, by documents laced with instructions instead of information
4. Gets attacked again, directly, with prompts designed to leak its own system prompt
5. Logs every attempt, working or not, into a structured payload library

<img width="1109" height="297" alt="image" src="https://github.com/user-attachments/assets/be2c9d09-6ed6-4b98-a8ee-439c44e79b7f" />


## Project structure

```
RAGdoll/
├── .vscode/
│
├── payloads/                         permanent payload library
│   ├── direct-injection/
│   │   ├── direct-01-instr-override.md
│   │   ├── direct-02-role-hijack.md
│   │   ├── direct-03-fake-delimiter.md
│   │   ├── direct-04-encoding-smuggle.md
│   │   ├── direct-05-prefix-priming.md
│   │   ├── direct-06-authority-impersonation.md
│   │   └── direct-07-hypothetical-distancing.md
│   └── indirect-injection/
│       └── tier1-direct-override/
│           └── basic.md
│
├── results/                          the actual dataset
│   ├── payload-log.json
│   ├── payload-log.jsonl
│   ├── payload-log.md
│   ├── payload-report.html
│   └── payload-report.md
│
├── runner/                           automation for running payloads
│   ├── render_report.py
│   ├── render_report_html.py
│   └── run_payload.py
│
└── target/                           the RAG app itself, the thing under test
    ├── docs/
    │   ├── clean/                    control group, proves the pipeline works
    │   │   ├── steins_gate_summary.txt
    │   │   └── Steins;Gate_(TV_series).pdf
    │   └── poisoned/                 live fire range, one payload at a time
    │       └── steins;gate_poisoned.txt
    ├── vectorstore/chroma_db/        Chroma persistence, gitignored
    ├── config.py                     every tunable constant in one place
    ├── ingest.py                     builds the vector store from docs
    ├── query.py                      the live pipeline, retrieval plus LLM call
    ├── .env.example
    ├── .gitignore
    ├── README.md
    └── requirements.txt
```

## Setup

```bash
git clone <repo-url>
cd RAGdoll
pip install -r requirements.txt
```

Pull a local model through Ollama. Small models work fine here, this project isn't about reasoning ability, it's about instruction hierarchy discipline, and a smaller model is arguably a more interesting target since it has less capacity to resist getting talked into things.

```bash
ollama pull llama3.2:1b
```

## Usage

Build the vector store from clean documents:

```bash
python target/ingest.py
```

Ask it something to confirm it works before you start breaking it:

```bash
python target/query.py
```

Run a single payload:

```bash
python runner/run_payload.py payloads/direct-injection/direct-01-instr-override.md
```

Run the whole batch of direct prompt injection payloads:

```bash
python runner/run_payload.py
```

Save it as a html report
```bash
python runner/render_report_html.py
```


https://github.com/user-attachments/assets/2b1d15e7-3ce0-4a50-8934-f5d8feb1548f




## Attack categories

### Direct prompt injection
<img width="1512" height="537" alt="image" src="https://github.com/user-attachments/assets/2ce03153-8e55-4f56-850f-7141deed8da9" />

The query route. The payload rides in as the attacker's own input, no documents involved, sent straight into the pipeline and aimed at overriding the model's behavior in that turn. Seven payloads tested so far: instruction override, role hijack, fake delimiter, encoding smuggle, prefix priming, authority impersonation, and hypothetical distancing.

### Indirect prompt injection (Adding Soon)
The document route. Instructions get planted inside otherwise normal looking content, ingested like any other document, and retrieved into the model's context as trusted data. Tiered from a blunt "ignore previous instructions" up through multi-document payload chaining. Tier 1 is in progress, tiers 2 through 5 coming soon.

### System prompt extraction
A specific goal rather than a delivery route, aimed at getting the model to hand over its own instructions rather than just override its behavior. Role confusion, completion attacks, translation bypasses, and multi-turn erosion. Coming soon.

## The payload library
Every payload gets logged with its injection vector, the model it was tested against, the result, and a short hypothesis for why it worked or got blocked. Full log lives in `results/payload-log.md`. Categories will be mapped to the OWASP LLM Top 10, mostly LLM01, once the writeup lands.

## Disclaimer

Every target in this project is local and self hosted. No live production systems, no third party services, no HackerOne scope anywhere near this repo. This is a lab for understanding the vulnerability class, not a toolkit pointed at someone else's stack.
