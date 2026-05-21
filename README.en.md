# claude-tech-writing

> A [Claude Code](https://code.claude.com) skill: treat mermaid diagrams as first-class citizens in technical writing, and let a Python linter enforce every rule on them.

[中文](README.md) | **English**

---

## Background: why this exists

When I write technical articles / design docs / post-mortems, two things consistently bite me:

### 1. Diagrams are systematically under-used

Relationships, flows, and timing claims that should obviously be diagrams get rendered as walls of prose instead — because drawing the right diagram has friction (picking a type, fighting the layout, getting the syntax right). The reader then has to mentally re-render that prose into the diagram I didn't draw. Slow, exhausting, error-prone.

When I ask Claude Code to help with technical writing, the same pattern shows up. Without rules in place, CC's default is to mimic typical samples — which means under-drawing too.

### 2. Drawn diagrams are often still bad

Common failure modes:

- A single "system overview" with 30+ nodes that nobody can follow
- Nodes called `A` / `B` / `S1` — readers have no idea what each shape means
- Naked arrows everywhere, no edge semantics (sync? async? read? write?)
- No prose hook before, no reading guide after — the diagram is dropped into the void
- Color used as the sole differentiator, breaking dark mode and grayscale print
- 5-field comparisons forced into `classDiagram`, blowing up the layout

Combined: either no diagram, or the diagram doesn't help either.

## What this skill solves

Goal: make "use diagrams to convey something" the **default move** for CC when writing technical content, not an afterthought:

- **Trigger is "writing"**, not "drawing" — it kicks in when you say "write an article about X" or "explain how X works", not when you explicitly ask for a diagram
- **Every diagram is held to hard checks**: per-type complexity caps, no-bare-IDs label rule, edges must carry verbs/conditions, named subgraphs, 5+ field comparison → must be a table, color never the only differentiator…
- **The linter runs**: after the draft, `python3 lint_article.py article.md` produces ❌ markers — gut feeling doesn't get to be the final judge

It's opinionated. Defaults are mine. **Fork and tune freely.**

## What it does

When you ask Claude Code to write a technical article / design doc / post-mortem / "how X works" explainer, the skill makes it:

1. **Ask "could a diagram go here?"** at every non-trivial relationship, flow, or timing claim — instead of defaulting to prose
2. **Stay within per-type complexity budgets**:
   - `flowchart` / `classDiagram` ≤ 12 nodes
   - `sequenceDiagram` ≤ 8 participants, ≤ 15 messages
   - `stateDiagram-v2` ≤ 10 states, ≤ 15 transitions
   - `erDiagram` ≤ 8 entities
   - `mindmap` ≤ 6 level-2 nodes, ≤ 6 leaves per level-2
3. **Use self-explanatory labels** (no bare `A` / `B` / `S1`)
4. **Wrap every diagram in 2 paragraphs of prose** (1-2 sentence setup + 3-5 sentence reading guide)
5. **Run the linter** as the final workflow step to enforce all of the above

## What it doesn't do

- Doesn't figure out *what* to write for you — only kicks in once you've decided
- Doesn't render mermaid to validate syntax — the linter is static regex-based; for full validation install [`mermaid-cli`](https://github.com/mermaid-js/mermaid-cli) and run `mmdc`
- Doesn't support non-mermaid tools (PlantUML / D2 / Graphviz — PRs welcome)
- Isn't an industry standard — it's one person's writing taste codified

## Install

```bash
git clone https://github.com/eastonsuo/claude-tech-writing
cd claude-tech-writing
./install.sh
```

The install script symlinks `tech-writing/` into `~/.claude/skills/tech-writing/`. Restart Claude Code if it's running.

Uninstall: `rm ~/.claude/skills/tech-writing`.

## Use

The skill auto-invokes on prompts like:

- "Write an article about how X works"
- "Explain the design of …"
- "Document the architecture of …"
- "Write a post-mortem / design doc"
- Chinese supported too: 「写一篇关于…的文章」, 「解释一下…的原理 / 设计」

Or call it explicitly: `/tech-writing` + your prompt.

After Claude finishes a draft, the linter runs as the final step. You'll see:

```
图 1 (行 5-26, 类型: flowchart, nodes: 9)
  ✅ 通过所有检查

图 2 (行 30-50, 类型: sequenceDiagram, participants: 12, messages: 18)
  ❌ participants 12 > 8（考虑拆图）
  ❌ messages 18 > 15（考虑拆图）

=== 共 2 张图，2 个问题 ===
```

(Linter output is currently Chinese; English translation welcome via PR.)

## Enforced rules

Full spec in [`tech-writing/SKILL.en.md`](tech-writing/SKILL.en.md) (Chinese: [`SKILL.md`](tech-writing/SKILL.md)). Headlines:

| Rule | Why |
|---|---|
| Per-type complexity budgets | A 30-node flowchart is two ideas crammed into one shell |
| Node labels readable to strangers (no `A` / `B`) | The IM screenshot test — share the diagram, do outsiders get ≥ 70%? |
| Edges labeled with verbs / conditions | Naked arrows convey almost nothing |
| Subgraphs have human-readable names | `subgraph storage["persistence layer"]`, not `s1` |
| Code references in prose, not in node labels | Line numbers drift; nodes should be stable |
| Colors from a fixed semantic palette, used consistently | Otherwise readers re-learn the legend each diagram |
| Color is never the only differentiator | Dark mode + grayscale print + colorblindness |
| Every diagram has prose before AND after | "As shown below" with no follow-up is wasted ink |
| 5+ field comparison → always a table, never a diagram | Tables are the right tool; `classDiagram`s blow up |

## Examples

`tech-writing/examples/` ships 5 reference patterns the skill points Claude to:

- `01-good-flowchart-storage-layers.md` — layered architecture (subgraphs + labeled edges)
- `02-bad-flowchart-too-many-nodes.md` — overcrowded + bare IDs + split suggestion
- `03-good-sequence-api-call.md` — clean request-response sequence
- `04-bad-no-prose-around.md` — diagram dropped without context
- `05-good-state-machine.md` — order lifecycle

(Currently in Chinese; the mermaid diagrams themselves are language-agnostic. English translations welcome.)

## Run lint standalone

Works without Claude Code — run against any markdown file:

```bash
python3 tech-writing/scripts/lint_article.py path/to/article.md
```

Exit 0 = clean, 1 = at least one ❌. Plug into a pre-commit hook or CI if you're feeling rigorous.

Zero dependencies — stdlib Python only.

## FAQ

**Why these specific numbers?** Opinionated defaults from my own writing/reading taste. Tune `LIMITS` in [`tech-writing/scripts/lint_article.py`](tech-writing/scripts/lint_article.py).

**Why mermaid only?** Mermaid renders in GitHub, GitLab, most IDEs, and most static-site generators without extra tooling. PlantUML / D2 / Graphviz support means: extra installs for users, more diagram-type detection logic, more example diversity. PRs welcome.

**Does the linter render mermaid?** No — it parses with regex. Catches structural issues (too many nodes, missing labels, naked IDs, embedded refs), not full syntax errors. For full validation install [`mermaid-cli`](https://github.com/mermaid-js/mermaid-cli) and run `mmdc`.

**Can I disable specific rules?** No config layer yet. Fork and edit. `.tech-writing.toml` style configs welcome via PR.

**Does the skill load in every session?** No — CC only invokes a skill when your prompt matches its `description`. Non-writing sessions aren't affected.

**Which CC version?** Skills with bundled scripts are stable on CC v2.1.x and later. Verified on v2.1.145.

## License

MIT. See [LICENSE](LICENSE).

## Author

[@eastonsuo](https://github.com/eastonsuo) · feedback, issues, PRs welcome.
