# RAGdoll

Give an LLM a cheat sheet and it'll read it. Give it a poisoned one and it'll follow it.

RAGdoll is a local RAG pipeline built for one purpose: getting attacked by its own creator. It stands up a working LangChain RAG stack, then systematically breaks it through indirect prompt injection and system prompt extraction, logging every payload into a reusable library along the way.

## Why this exists

An LLM has no ring 0. There is no hardware boundary between "instructions I should obey" and "content I should summarize." It's all tokens in the same buffer, and the model has to guess which parts are commands based on nothing but phrasing and position.

RAG makes this worse, not better. It hands the model a live feed of external, often untrusted, text and asks it to treat that text as reference material. RAGdoll exists to find out exactly how much you can abuse that trust before the model breaks character.

## What it actually does

1. Ingests a set of documents into a local vector store
2. Answers questions by retrieving relevant chunks and stuffing them into the model's context
3. Gets attacked, on purpose, by documents laced with instructions instead of information
4. Gets attacked again, directly, with prompts designed to leak its own system prompt
5. Logs every attempt, working or not, into a structured payload library

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/6bb40158-9daa-40d6-91d2-929bfc8f2411" />


## Project structure

```
RAGdoll/
├── target/              the RAG app itself, the thing under test
│   ├── ingest.py         builds the vector store from docs
│   ├── query.py          the live pipeline, retrieval plus LLM call
│   ├── config.py         every tunable constant in one place
│   └── docs/
│       ├── clean/         control group, proves the pipeline works
│       └── poisoned/      live fire range, one payload at a time
│
├── payloads/             the permanent payload library
│   ├── indirect-injection/
│   │   ├── tier1-direct-override/
│   │   ├── tier2-role-confusion/
│   │   ├── tier3-exfiltration/
│   │   ├── tier4-placement/
│   │   └── tier5-chaining/
│   └── system-prompt-extraction/
│       ├── role-confusion/
│       ├── completion-attack/
│       ├── translation-bypass/
│       ├── documentation-framing/
│       └── multi-turn-erosion/
│
├── runner/               automation for running payloads at scale
│   ├── run_payload.py
│   ├── batch_run.py
│   └── compare_models.py
│
├── results/              the actual dataset
│   ├── payload-log.md
│   └── payload-log.json
│
├── vectorstore/          Chroma persistence, gitignored
│
└── writeup/              the research narrative
    ├── methodology.md
    └── owasp-mapping.md
```

## Setup

```bash
git clone <repo-url>
cd RAGdoll
pip install -r requirements.txt
```

Pull a local model through Ollama. Small models work fine here, this project isn't about reasoning ability, it's about instruction hierarchy discipline, and a smaller model is arguably a more interesting target since it has less capacity to resist getting talked into things.

```bash
ollama pull llama3.2:3b
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
python runner/run_payload.py payloads/indirect-injection/tier1-direct-override/basic.md
```

Run the whole library and log results:

```bash
python runner/batch_run.py
```

Compare behavior across models:

```bash
python runner/compare_models.py
```

## Attack categories

### Indirect prompt injection

The document route. Instructions get planted inside otherwise normal looking content, ingested like any other document, and retrieved into the model's context as trusted data. Tested across five tiers, from a blunt "ignore previous instructions" to multi-document payload chaining.

### System prompt extraction

The direct route. No documents involved, these go straight into the query input. Role confusion, completion attacks, translation bypasses, and multi-turn erosion, all aimed at getting the model to hand over its own instructions.

## The payload library

Every payload gets logged with its injection vector, the model it was tested against, the result, and a short hypothesis for why it worked or got blocked. Full log lives in `results/payload-log.md`. Categories are mapped to the OWASP LLM Top 10 in `writeup/owasp-mapping.md`, mostly LLM01.

## Disclaimer

Every target in this project is local and self hosted. No live production systems, no third party services, no HackerOne scope anywhere near this repo. This is a lab for understanding the vulnerability class, not a toolkit pointed at someone else's stack.
