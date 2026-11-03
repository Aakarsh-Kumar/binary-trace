# AGENTS

This repository is governed by four documents at the root, in this precedence order:

1. `PRD.md`         — scope, user stories, metrics
2. `ARCHITECTURE.md` — stack, schemas, layout, algorithms
3. `INSTRUCTIONS.md` — operational guardrails
4. `MEMORY.md`       — history, roadblocks, decisions

Read all four, in that order, before writing any code. `INSTRUCTIONS.md §1` mandates this.

The three design commitments in `ARCHITECTURE.md §1` (capability-gated retrieval, evidence-gated flagging, disagreement shown not averaged) are the project's novelty. They are frozen by `INSTRUCTIONS.md §8`. Do not weaken them.

When blocked, log to `MEMORY.md → Active Roadblocks` and stop. Do not invent tables, dependencies, endpoints, directories, or model tags.