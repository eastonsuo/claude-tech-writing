# claude-tech-writing

> A [Claude Code](https://code.claude.com) skill that pushes diagrams to the front of technical writing — and lints each one so they're actually useful.

When you ask Claude Code to write a technical article, design doc, or explainer, this skill makes it:

1. Reach for diagrams (mermaid) at every non-trivial relationship, flow, or timing claim
2. Stay within per-type complexity budgets (`flowchart` ≤ 12 nodes, `sequenceDiagram` ≤ 8 participants & ≤ 15 messages, etc.)
3. Use self-explanatory labels — no bare `A` / `B` / `S1` nodes
4. Wrap every diagram in 2 paragraphs of prose (setup + reading guide)
5. Run a Python linter over the output to catch every rule violation

It's opinionated. The defaults are mine. Fork and tune.

## Install

```bash
git clone https://github.com/eastonsuo/claude-tech-writing
cd claude-tech-writing
./install.sh
```

That symlinks `tech-writing/` into `~/.claude/skills/tech-writing/`. Restart Claude Code if it's running.

To uninstall: `rm ~/.claude/skills/tech-writing`.

## Use

The skill auto-invokes on prompts like:

- "Write an article about how X works"
- "Explain the design of …"
- "Document the architecture of …"
- "Write a post-mortem / design doc / explainer"

Or invoke explicitly: `/tech-writing` followed by your prompt.

After Claude writes a draft, the linter runs as the last workflow step. You'll see output like:

```
图 1 (行 5-26, 类型: flowchart, nodes: 9)
  ✅ 通过所有检查

图 2 (行 30-50, 类型: sequenceDiagram, participants: 12, messages: 18)
  ❌ participants 12 > 8（考虑拆图）
  ❌ messages 18 > 15（考虑拆图）

=== 共 2 张图，2 个问题 ===
```

## What gets enforced

See [`tech-writing/SKILL.md`](tech-writing/SKILL.md) for the full skill spec. Headline rules:

| Rule | Why |
|---|---|
| Per-type complexity budgets | A 25-node `flowchart` is two ideas in a trenchcoat |
| Node labels readable to strangers (no `A` / `B`) | The "IM screenshot test" — share the diagram, see if outsiders get it |
| Edges labeled with verbs or conditions | Bare arrows convey almost nothing |
| Subgraphs have human-readable names | `subgraph storage["persistence layer"]`, not `s1` |
| Code references in prose, not in node labels | Line numbers drift; nodes should be stable |
| Colors from a fixed semantic palette, used consistently | Otherwise readers re-learn the legend every diagram |
| Color is never the only differentiator | Dark mode + grayscale print + colorblindness |
| Every diagram has prose before AND after | "As shown below" with no follow-up is wasted ink |
| 5+ field comparison → always a table, never a diagram | Tables are the right tool; classDiagrams blow up |

## Examples

`tech-writing/examples/` ships 5 reference patterns the skill points Claude to:

- `01-good-flowchart-storage-layers.md` — what a well-scoped layered flowchart looks like
- `02-bad-flowchart-too-many-nodes.md` — overcrowded, with a split suggestion
- `03-good-sequence-api-call.md` — clean request-response sequence
- `04-bad-no-prose-around.md` — diagram dropped without context
- `05-good-state-machine.md` — order lifecycle

(Examples are currently in Chinese; English translations welcome via PR.)

## Lint by itself

You can run the linter standalone on any markdown file, no Claude Code involved:

```bash
python3 tech-writing/scripts/lint_article.py path/to/article.md
```

Exit code 0 = clean, 1 = at least one ❌. Wire it into a pre-commit hook or CI if you're feeling rigorous.

Zero dependencies — stdlib Python only.

## Philosophy

Most writing advice tells you to **trim**: cut the fluff, kill your darlings, less is more. That's good advice for prose.

But it's wrong for diagrams. **Diagrams aren't over-used; they're systematically under-used.** The friction of "drawing the right diagram" — picking a type, getting the layout, fighting the syntax — pushes writers to fall back on prose for things that should obviously be visual. Readers then have to mentally re-render that prose into the diagram the writer didn't draw.

This skill exists to invert the default. "Could this be a diagram?" goes from a rare consideration to a first thought. The complexity budget exists so the answer isn't "yes, a massive one" but "yes, and that means this paragraph is actually two paragraphs."

## FAQ

**Why these specific numbers?** They're opinionated defaults from my own taste. Fork and tune `LIMITS` in [`tech-writing/scripts/lint_article.py`](tech-writing/scripts/lint_article.py).

**Why mermaid only?** Mermaid renders in GitHub, GitLab, most IDEs, and most static-site generators without extra tooling. PlantUML / D2 / Graphviz support would mean: extra installs for users, more diagram-type detection logic, and more example diversity. PRs welcome.

**Does the linter actually render the diagrams?** No — it parses mermaid with regex. It catches structural issues (too many nodes, missing labels, naked IDs, embedded file refs) but won't catch every syntax error. For full syntactic validation, install [`mermaid-cli`](https://github.com/mermaid-js/mermaid-cli) and run `mmdc` manually.

**Can I disable specific lint rules?** Not via config yet. For now: fork and edit. PRs for a `.tech-writing.toml` config would be welcome.

**Why is the skill loaded by default in every session?** It isn't — Claude Code only invokes a skill when your prompt matches its `description`. The description here filters for technical-writing intent; other sessions won't see it.

**What CC version is required?** Skills with bundled scripts work on Claude Code v2.1.x and later. Verified on v2.1.145.

## License

MIT. See [LICENSE](LICENSE).

## Author

Feedback, issues, and PRs welcome.
