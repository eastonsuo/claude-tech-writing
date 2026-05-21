---
name: tech-writing
description: Use when writing tech articles, design docs, or "how X works" explainers. Pushes mermaid diagrams as primary tool, lint-checks every one. 触发：写…文章 / 解释…原理 / design doc / explain how X works.
---

# Tech writing — diagrams as a first-class tool, but each one held to a high bar

## The core opinion: diagrams are systematically under-used in tech writing

When you describe **structure / flow / timing** in prose, the reader has to mentally re-render it into a diagram — slow, tiring, and error-prone. A well-chosen diagram lets the reader see the relationship at a glance, often beating two hundred words of explanation.

So the default move when writing technical content isn't "consider a diagram only when I really need one." It's:

> **After describing any non-trivial relationship, flow, or sequence, first ask "could a diagram go here?" — and only then decide it can't.**

Better to over-draw and trim than to under-draw from the start. The latter turns paragraphs that should have been diagrams into walls of text that readers skim and skip.

### Quick test for "should this be a diagram?"

**Lean toward a diagram**:
- The prose mentions 3+ distinct objects and the relationships between them
- You're describing "first A, then B, in parallel C, returning to D" type flows
- Multiple parties exchange messages over time (request-response, state transitions)

**Hard no — never a diagram**:
- **5+ field comparisons, property enumerations, config catalogs → always a markdown table**.
  Forcing these into `classDiagram` or label-heavy nodes makes the diagram explode; tables are the natural home for this kind of content.
- Just listing a few facts in order → use a bullet list
- Comparing two things on a few dimensions → use a table

## Every diagram must earn its place

"More diagrams" is not "stuff diagrams everywhere." Each one has to pass three checks:

### 1. One diagram, one focus

Each diagram answers **one** question. Write it on the line above the diagram:

> The diagram below answers: "How many hops does a request take from X to Y?"

Better to split into 3 small diagrams than cram one big one that answers two questions.

### 2. Complexity budget by diagram type

Different diagram types have different complexity dimensions — `sequenceDiagram` complexity comes from messages, not participants; `mindmap` is inherently divergent and can't be capped by node count. So per-type limits:

| Diagram type | Limit |
|---|---|
| `flowchart` / `classDiagram` | nodes ≤ 12 |
| `sequenceDiagram` | participants ≤ 8, messages ≤ 15 |
| `stateDiagram-v2` | states ≤ 10, transitions ≤ 15 |
| `erDiagram` | entities ≤ 8 |
| `mindmap` | level-2 nodes ≤ 6, leaves per level-2 ≤ 6 |

Crossing the limit almost always means the diagram is trying to convey two things — split it into two, each answering one question.

### 3. Each diagram needs prose around it

- **Before**: 1-2 sentences saying "what this diagram will show you"
- **After**: 3-5 sentences of reading guidance — call out key nodes, asymmetric edges, easily-missed corners

Don't write "as shown below" and drop a diagram with no setup or follow-through.

## Style constraints (so all diagrams in one piece look like a set)

### Labels must be intelligible to strangers — the 70% test

- **Node IDs** use snake_case (purely for source readability, doesn't affect rendering)
- **Display labels** must be short phrases a first-time reader can roughly guess. **No bare A/B/S1/Component1**:
- ❌ `A[Component A]` `B[Service]` `S1[State 1]`
- ✅ `apiserver["apiserver<br/>control plane"]` `worker["worker pool<br/>async processing"]`

**The IM-screenshot test**: take a screenshot of the diagram, drop it in a chat with people who haven't read the article. If they can guess ≥70% of nodes and edges' meaning, the diagram passes. If anyone asks "what's A?", it fails.

### Label your edges

Unless the meaning is glaringly obvious, every edge gets a verb or condition label: `-->|"read"|`, `-->|"retry on timeout"|`, `-->|"success"|`. Bare arrows are only acceptable in the simplest linear chains (A → B → C).

### Name your subgraphs

Use `subgraph` to group related nodes, and give the subgraph a human name:

```
subgraph storage["persistence layer"]
```

Not `subgraph s1`.

### Stay consistent on direction

All `flowchart` diagrams in the same article use the same direction (`TD` or `LR`) — don't mix. `sequenceDiagram` naturally flows top-down; pair it with `flowchart TD` for the most visually coherent piece.

### Code references go in prose, not in node labels

If the diagram is illustrating concrete code behavior, reference the location in surrounding prose: `src/foo.py:42`. Don't bake `apiserver[foo.py:42]` into the diagram.

**Why**: line numbers drift as code changes. Nodes should be stable abstractions. Embedding line numbers means every refactor requires editing the diagram, and nobody actually will.

### Use color from a fixed semantic palette

Default to no color. When you do use color, pick from this palette and keep the meaning consistent across the entire article (**don't have red mean "error" in one diagram and "main path" in another**):

| Meaning | Color | When |
|---|---|---|
| Main path / current focus | warm yellow `#fff0aa` | Drawing attention to "look here" |
| Success / completed | light green `#aaffaa` | Terminal states / OK branches |
| Failure / exception | light red `#ffcccc` | Error branches |
| External system / black box | grey `#f4f4f4` | Not the focus of this article |
| Phase grouping | blue / orange / red gradient | Step 1 / 2 / 3 coloring |

Define with `classDef` and explain the color semantics in a sentence after the diagram.

### Color is never the only differentiator

Once you use color, the diagram must also be readable in **dark mode + black-and-white print + with color-blindness**. That means key distinctions must **also** appear in:

- **Shape**: `[rect]` `((circle))` `{diamond}` `[/parallelogram/]`
- **Line style**: solid `-->` / dashed `-.->` / thick `==>`
- **Text labels**: verbs/conditions on edges

Color is icing, never the only channel.

### Don't mix ASCII and mermaid

Pick one and stick with it across the whole piece. ASCII art tends to render less cleanly in GitHub, IDEs, and most markdown viewers compared to mermaid.

## Diagram-type quick reference

| To express | Use |
|---|---|
| Static relationships between modules (A contains B, A depends on C) | `flowchart` or `classDiagram` |
| Messages exchanged over time | `sequenceDiagram` |
| State machine for one object | `stateDiagram-v2` |
| Data model (entities + fields + relationships) | `erDiagram` |
| Proportions / flows | `sankey-beta` or `pie` |
| Bird's-eye system architecture | `C4Context` or `flowchart` with `subgraph` |
| Divergent knowledge tree | `mindmap` |

## Anti-patterns (don't do these)

- ❌ A `flowchart` with 25 nodes and crossing arrows
- ❌ Node IDs are A/B/S1 with no display labels
- ❌ Using `classDiagram` to enumerate 5+ fields (use a table)
- ❌ Embedding `foo.py:42` in a node label
- ❌ Distinguishing "main vs exception" with color alone, identical shape and line style (dies in dark mode)
- ❌ Opening with "as shown below" and following with no prose explanation
- ❌ Mixing mermaid and ASCII art in the same piece

## Workflow

When you get a writing request, do this first — don't dive into prose:

1. **List claims**: write down the 3-7 core claims the article will make
2. **Pick the medium**: for each claim ask "would the reader grasp this fastest as prose, a table, or a diagram?" — **default toward diagrams, but respect the hard-no rules**
3. **Write the diagram's question**: for each diagram-bound claim, write one sentence stating the question it answers
4. **Draw**: check the per-type limit table; if you blow the cap, split
5. **Write surrounding prose**: 2 paragraphs per diagram (before-hook and after-reading-guide)
6. **Final review**:
   - Delete any diagram that's purely decorative
   - Look for paragraphs that should have a diagram but don't (≥3 objects with relationships, or multi-step flows)
   - Check that color semantics stay consistent across the article
7. **Run the linter**:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/lint_article.py <your-file.md>
   ```
   Fix every ❌. The script checks:
   - Per-type complexity limits (nodes / participants / messages / states / transitions / entities)
   - Edge-label coverage in flowcharts
   - Subgraph naming
   - Bare 1-2 char node IDs (A/B/S1)
   - File:line references embedded in node labels
   - Direction consistency across all flowcharts
   - Prose presence before and after each diagram (≥30 chars)

## Reference examples

Before writing, skim 1-2 relevant examples under `${CLAUDE_SKILL_DIR}/examples/` to establish a style baseline:

- `01-good-flowchart-storage-layers.md` — layered architecture diagram (subgraphs + labeled edges + readable labels)
- `02-bad-flowchart-too-many-nodes.md` — too many nodes + bare IDs + suggested split
- `03-good-sequence-api-call.md` — clean request-response sequence
- `04-bad-no-prose-around.md` — typical "no prose around the diagram" failure
- `05-good-state-machine.md` — order lifecycle state machine

(Examples are currently in Chinese; the diagrams themselves are language-agnostic. English translations welcome.)
