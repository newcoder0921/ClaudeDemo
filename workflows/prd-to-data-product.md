# Workflow: Source Data → PRD → Jira → Data Product Code

**Trigger:** "Run prd-to-data-product for <PRODUCT_NAME>" (e.g. `DP_Member_360`)
**Inputs:** source CSVs + a sample target file (the product's shape)
**Tools used:** Python (pandas, pytest, python-docx, openpyxl), Atlassian (Jira), BMad agents (PM → Architect → Dev)
**Output folder:** `output/<PRODUCT_NAME>/`
**Reference build:** `output/DP_Member_360/` (PRD, Jira SCRUM-17, framework in `04_code/`)

---

## Before you start (always)

- Ask:
  - Which product, and who uses it?
  - Which Jira project?
  - Any stack override (default: Python + SQLite locally, ANSI DDL)?
- Show the plan (steps below) and wait for a go-ahead.
- Confirm where the files go:
  - sources → `sources/data/raw/`
  - target sample → `data/output/product/`
  - Never edit `raw/` (the wiki's sources).

---

## Step 1 — Place the inputs

- Write the source files byte-for-byte to `sources/data/raw/`, and the target sample to `data/output/product/`.
- Verify the row count of every file.

## Step 2 — Profile the data (read-only)

For each source and the target sample, record:
- grain
- primary key and foreign keys
- row count
- every column's raw format and example

Check every target column and sort it into one of:
- **direct**: copied as-is from a source
- **rule**: derived from a source by a rule
- **gap**: no source

Then look for problems, and **verify each one against the data before writing it down**:
- ID format mismatches between sources and target
- target values that don't line up with the sources
- negative or odd values
- sign conventions
- running balance vs. single-transaction balance
- status combinations (e.g. Dormant members with activity)

## Step 3 — PRD (with data types)

Build `PRD_<name>.docx` + `.md` from one generator script. Use bullets over paragraphs. Sections:

1. Overview
2. Goals, non-goals and success metrics
3. Personas
4. Scope
5. **Source inventory + data dictionary**: per column, give the logical type, physical type, nullability, key, raw example and conversion rule
6. **Target schema**: same columns as section 5, plus allowed values
7. Source-to-target mapping (marked direct / rule / GAP)
8. Functional requirements FR-xx + user stories
9. Non-functional requirements
10. DQ rules (block / reject / warn) and acceptance criteria
11. Open questions (every finding from Step 2)
12. Dependencies, risks, milestones
13. Appendix: sources

Also write `Data_Dictionary_<name>.xlsx`, with sheets Source_Dictionary, Target, S2T_Mapping.

Type conventions:
- currency text → `DECIMAL(15,2)` (parentheses mean negative)
- M/D/YYYY → `DATE`
- TRUE/FALSE → `BOOLEAN`
- YYYYMMDD keys → `INT`
- IDs and postal codes → text

## Step 4 — Push to Jira

- **Check the issue types first** (`listJiraProjectIssueTypesMetadata`). If "Feature" doesn't exist, create an **Epic labeled `feature`** and say so.
  - The Epic holds: summary, goals, metrics, open questions, and the **target schema table with types**.
- Create one **Story per FR** under the Epic. Each holds: a user story, the columns it touches with their types, and acceptance criteria as checkboxes.
- Verify with JQL (`parent = <EPIC>`). Save keys and links to `jira_issues.md`.

## Step 5 — Architecture (optional, `bmad-agent-architect`)

Decide only what keeps the build consistent:
- layers (raw → typed staging → product)
- where the ID crosswalk lives
- which DQ rules block publishing
- how columns that have no source yet are handled

## Step 6 — Build (`bmad-agent-dev`)

- Write `stories.md`: each story's acceptance criteria as a checklist, traced to tests.
- Copy the reusable framework from `output/DP_Member_360/04_code/src/dp_framework/` into `output/<name>/04_code/src/`. Don't rewrite it.
- Write only the product-specific parts:

```
contracts/sources.py        # one Column per source column (types from PRD §5)
contracts/<product>.py      # target contract (PRD §6); status="pending" for gap columns
src/<product>/config.py     # paths + Settings switches for unapproved rules
src/<product>/transform.py  # one function per mapping rule (PRD §7)
src/<product>/dq_rules.py   # PRD §10 rules using dp_framework.dq factories
src/<product>/run.py        # ingest → standardize → source DQ → transform → product DQ → publish
tests/                      # one test file per story; use the real sample sources
```

Rules:
- Tests first. **All tests must pass** before you report done.
- Types live only in the contracts. DDL is generated (`--write-ddl`) and a test keeps it in sync.
- Gap columns are published as NULL, marked `pending`, and skipped by NOT NULL checks.
- Rules that are still undecided (open questions) are `Settings` switches, never hard-coded.
- A blocking DQ failure means the previous product stays published.
- No PII in the product.
- No story or ticket IDs in code comments.

## Step 7 — Verify

- `pytest -q` passes. Run `python -m src.<product>.run --as-of <date>` and confirm:
  - exit code 0
  - expected row count
  - all DQ rules Pass
- The product CSV header matches the target sample's columns and order.
- Every story acceptance criterion in `stories.md` is either ticked with a test name or marked blocked with its reason.

## Step 8 — Wrap up

Summary to the user, in bullets:
- what was built
- test count
- the run result
- Jira keys
- open questions that block stories

Offer to comment on the Jira stories with their status, or to open a PR (follow `jira-to-pr.md` Step 7).
